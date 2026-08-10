package main

import "testing"

func run(in string) string { return string(process([]byte(in))) }

// TestJunctionTable checks that a junction with a given set of connecting
// neighbors is rewritten to the expected box-drawing character. Each case
// centers the junction at row 1, column 1 and surrounds it with the segments
// that should (and should not) connect.
func TestJunctionTable(t *testing.T) {
	tests := []struct {
		name, in, want string
	}{
		{"corner down+right", " \n ┼─\n │", " \n ┌─\n │"},
		{"corner down+left", "  \n─┼\n │", "  \n─┐\n │"},
		{"corner up+right", " │\n ┼─", " │\n └─"},
		{"corner up+left", " │\n─┼", " │\n─┘"},
		{"tee up+down+right", " │\n ┼─\n │", " │\n ├─\n │"},
		{"tee up+down+left", " │ \n─┼ \n │ ", " │ \n─┤ \n │ "},
		{"tee down+left+right", "   \n─┼─\n │ ", "   \n─┬─\n │ "},
		{"tee up+left+right", " │ \n─┼─", " │ \n─┴─"},
		{"cross all four", " │ \n─┼─\n │ ", " │ \n─┼─\n │ "},
		{"horizontal segment", "─┼─", "───"},
		{"vertical segment", "│\n┼\n│", "│\n│\n│"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := run(tt.in); got != tt.want {
				t.Errorf("got:\n%q\nwant:\n%q", got, tt.want)
			}
		})
	}
}

func TestDiagrams(t *testing.T) {
	correct := "┌─┬─┐\n│ │ │\n├─┼─┤\n│ │ │\n└─┴─┘"
	arrows := "──► ok\n◄── x\n│\n▼"
	tests := []struct {
		name, in, want string
	}{
		{
			"stray cross in border becomes dash",
			"┌─┼─┐\n│   │\n└───┘",
			"┌───┐\n│   │\n└───┘",
		},
		{
			"cross with stem only below becomes tee",
			"─┼─\n │",
			"─┬─\n │",
		},
		{
			"tee with all four neighbors becomes cross",
			" │ \n─┤─\n │ ",
			" │ \n─┼─\n │ ",
		},
		{"arrows preserved, never rewritten", arrows, arrows},
		{"already-correct diagram unchanged", correct, correct},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := run(tt.in); got != tt.want {
				t.Errorf("got:\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}

func TestEdgeCases(t *testing.T) {
	tests := []struct {
		name, in, want string
	}{
		{"empty input", "", ""},
		{"single junction, no neighbors", "┼", "┼"},
		{"plain text passes through", "hello world", "hello world"},
		{"no box chars, multiline", "a\nbb\nccc", "a\nbb\nccc"},
		{"trailing newline preserved", "─┼─\n │\n", "─┬─\n │\n"},
		{"no trailing newline preserved", "─┼─\n │", "─┬─\n │"},
		{"blank line preserved", "\n", "\n"},
		{"ragged short lines", "┌─┐\n│\n└─┘", "┌─┐\n│\n└─┘"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := run(tt.in); got != tt.want {
				t.Errorf("got:\n%q\nwant:\n%q", got, tt.want)
			}
		})
	}
}

func lintOf(in string) []issue {
	lines, _ := splitDiagram([]byte(in))
	return lint(lines)
}

// TestLint covers the non-mutating checker: real junction defects and ASCII
// arrows are reported, while correct diagrams and tree stubs are clean.
func TestLint(t *testing.T) {
	tests := []struct {
		name, in string
		want     int // number of issues expected
	}{
		{"correct box is clean", "┌─┬─┐\n│ │ │\n└─┴─┘", 0},
		{"tree listing is clean (overspecified branches tolerated)",
			"root\n├── a\n├── b\n└── c", 0},
		{"corner where a tee is needed is flagged", "─┐─\n │", 1},
		{"straight char at a real crossing is flagged", " │\n──\n │", 1},
		{"ASCII arrow flagged", "a -> b", 1},
		{"reverse ASCII arrow flagged", "a <- b", 1},
		{"box arrows are clean", "──► x\n◄── y", 0},
		{"empty is clean", "", 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := len(lintOf(tt.in)); got != tt.want {
				t.Errorf("got %d issues, want %d: %+v", got, tt.want, lintOf(tt.in))
			}
		})
	}
}

// TestLintPosition pins the 1-based row:col reporting. The ┐ on row 2 has a
// segment entering from the right, so it should be a ┬ — a real defect at 2:2.
func TestLintPosition(t *testing.T) {
	got := lintOf("x\n─┐─\n │")
	if len(got) != 1 {
		t.Fatalf("want 1 issue, got %+v", got)
	}
	if got[0].row != 2 || got[0].col != 2 {
		t.Errorf("want 2:2, got %d:%d", got[0].row, got[0].col)
	}
}
