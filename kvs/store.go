package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"modernc.org/sqlite"
)

const schema = `CREATE TABLE IF NOT EXISTS kv (
	project TEXT NOT NULL,
	session TEXT NOT NULL,
	key TEXT NOT NULL,
	value TEXT NOT NULL,
	expires INTEGER,
	updated INTEGER NOT NULL,
	PRIMARY KEY (project, session, key)
)`

const busyRetries = 5

var errAbsent = errors.New("absent")

// Scope is the (project, session) pair a key lives under; "" means none.
type Scope struct {
	Project string
	Session string
}

// Entry is one stored key with its value.
type Entry struct {
	Key   string
	Value string
}

// SessionRow is one session of a project with its key count and last write.
type SessionRow struct {
	Project string
	Session string
	Keys    int
	Updated time.Time
}

// Store is one open SQLite database.
type Store struct {
	db *sql.DB
}

// Open opens or creates dir/kv.db in WAL mode.
func Open(dir string) (*Store, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, err
	}
	dsn := "file:" + filepath.Join(dir, "kvs.db") +
		"?_txlock=immediate&_pragma=busy_timeout(5000)&_pragma=journal_mode(WAL)&_pragma=synchronous(NORMAL)"
	db, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(schema); err != nil {
		// schema failed; the handle is useless
		_ = db.Close()
		return nil, err
	}
	return &Store{db: db}, nil
}

func (s *Store) Close() error {
	return s.db.Close()
}

func isBusy(err error) bool {
	var sqerr *sqlite.Error
	if errors.As(err, &sqerr) {
		code := sqerr.Code() & 0xff
		return code == 5 || code == 6
	}
	return false
}

// write runs fn inside one transaction that takes the write lock at BEGIN
// (_txlock=immediate), retrying only when SQLite reports busy or locked.
func (s *Store) write(fn func(tx *sql.Tx) error) error {
	var err error
	for attempt := 0; attempt < busyRetries; attempt++ {
		err = s.writeOnce(fn)
		if !isBusy(err) {
			return err
		}
		time.Sleep(time.Duration(20*(attempt+1)) * time.Millisecond)
	}
	return err
}

func (s *Store) writeOnce(fn func(tx *sql.Tx) error) error {
	tx, err := s.db.BeginTx(context.Background(), nil)
	if err != nil {
		return err
	}
	if err := fn(tx); err != nil {
		// the caller's error is the one to report; rollback failure adds nothing
		_ = tx.Rollback()
		return err
	}
	return tx.Commit()
}

func (s *Store) Get(scope Scope, key string) (string, error) {
	now := time.Now().Unix()
	var value string
	err := s.db.QueryRow(
		`SELECT value FROM kv WHERE project = ? AND session = ? AND key = ?
		 AND (expires IS NULL OR expires > ?)`,
		scope.Project, scope.Session, key, now,
	).Scan(&value)
	if errors.Is(err, sql.ErrNoRows) {
		return "", errAbsent
	}
	return value, err
}

func expiry(now int64, ttl int64) sql.NullInt64 {
	if ttl <= 0 {
		return sql.NullInt64{}
	}
	return sql.NullInt64{Int64: now + ttl, Valid: true}
}

func purge(tx *sql.Tx, now int64) error {
	_, err := tx.Exec(`DELETE FROM kv WHERE expires IS NOT NULL AND expires <= ?`, now)
	return err
}

func put(tx *sql.Tx, scope Scope, key, value string, now, ttl int64) error {
	_, err := tx.Exec(
		`INSERT INTO kv (project, session, key, value, expires, updated) VALUES (?, ?, ?, ?, ?, ?)
		 ON CONFLICT (project, session, key) DO UPDATE SET
		   value = excluded.value, expires = excluded.expires, updated = excluded.updated`,
		scope.Project, scope.Session, key, value, expiry(now, ttl), now,
	)
	return err
}

func current(tx *sql.Tx, scope Scope, key string) (string, bool, error) {
	var value string
	err := tx.QueryRow(
		`SELECT value FROM kv WHERE project = ? AND session = ? AND key = ?`,
		scope.Project, scope.Session, key,
	).Scan(&value)
	if errors.Is(err, sql.ErrNoRows) {
		return "", false, nil
	}
	return value, err == nil, err
}

// Set writes value; with ifOld set, only when the current value equals it
// (an empty ifOld means: only when absent). errAbsent reports a failed
// condition.
func (s *Store) Set(scope Scope, key, value string, ttl int64, ifOld *string) error {
	return s.write(func(tx *sql.Tx) error {
		now := time.Now().Unix()
		if err := purge(tx, now); err != nil {
			return err
		}
		if ifOld != nil {
			old, present, err := current(tx, scope, key)
			if err != nil {
				return err
			}
			if present != (*ifOld != "") || (present && old != *ifOld) {
				return errAbsent
			}
		}
		return put(tx, scope, key, value, now, ttl)
	})
}

// Incr adds n to the integer at key, creating it from 0, and returns the result.
// ttl arms an expiry only when the key is created.
func (s *Store) Incr(scope Scope, key string, n int64, ttl int64) (int64, error) {
	var result int64
	err := s.write(func(tx *sql.Tx) error {
		now := time.Now().Unix()
		if err := purge(tx, now); err != nil {
			return err
		}
		old, present, err := current(tx, scope, key)
		if err != nil {
			return err
		}
		var value int64
		if present {
			value, err = strconv.ParseInt(old, 10, 64)
			if err != nil {
				return fmt.Errorf("%s holds %q, not an integer", key, old)
			}
			result = value + n
			_, err = tx.Exec(
				`UPDATE kv SET value = ?, updated = ? WHERE project = ? AND session = ? AND key = ?`,
				strconv.FormatInt(result, 10), now, scope.Project, scope.Session, key,
			)
			return err
		}
		result = n
		return put(tx, scope, key, strconv.FormatInt(result, 10), now, ttl)
	})
	return result, err
}

func (s *Store) Del(scope Scope, keys []string) error {
	return s.write(func(tx *sql.Tx) error {
		for _, key := range keys {
			_, err := tx.Exec(
				`DELETE FROM kv WHERE project = ? AND session = ? AND key = ?`,
				scope.Project, scope.Session, key,
			)
			if err != nil {
				return err
			}
		}
		return nil
	})
}

// List returns the live keys of the scope that start with prefix, sorted by key.
func (s *Store) List(scope Scope, prefix string) ([]Entry, error) {
	rows, err := s.db.Query(
		`SELECT key, value FROM kv WHERE project = ? AND session = ? AND key >= ? AND key < ?
		 AND (expires IS NULL OR expires > ?) ORDER BY key`,
		scope.Project, scope.Session, prefix, prefix+"￿", time.Now().Unix(),
	)
	if err != nil {
		return nil, err
	}
	// rows fully consumed below; Close only releases the statement
	defer rows.Close() //nolint:errcheck
	var entries []Entry
	for rows.Next() {
		var entry Entry
		if err := rows.Scan(&entry.Key, &entry.Value); err != nil {
			return nil, err
		}
		entries = append(entries, entry)
	}
	return entries, rows.Err()
}

// Sessions returns the sessions of project with live keys, newest write first;
// an empty project lists every project.
func (s *Store) Sessions(project string, all bool) ([]SessionRow, error) {
	query := `SELECT project, session, count(*), max(updated) FROM kv
		 WHERE session != '' AND (expires IS NULL OR expires > ?)`
	args := []any{time.Now().Unix()}
	if !all {
		query += ` AND project = ?`
		args = append(args, project)
	}
	query += ` GROUP BY project, session ORDER BY max(updated) DESC`
	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	// rows fully consumed below; Close only releases the statement
	defer rows.Close() //nolint:errcheck
	var out []SessionRow
	for rows.Next() {
		var row SessionRow
		var updated int64
		if err := rows.Scan(&row.Project, &row.Session, &row.Keys, &updated); err != nil {
			return nil, err
		}
		row.Updated = time.Unix(updated, 0)
		out = append(out, row)
	}
	return out, rows.Err()
}
