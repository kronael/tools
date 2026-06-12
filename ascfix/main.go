package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

type sides struct{ up, down, left, right bool }

// boxChars: chars we fix — structural box-drawing only, not arrows.
var boxChars = map[rune]sides{
	'─': {false, false, true, true},
	'│': {true, true, false, false},
	'┌': {false, true, false, true},
	'┐': {false, true, true, false},
	'└': {true, false, false, true},
	'┘': {true, false, true, false},
	'├': {true, true, false, true},
	'┤': {true, true, true, false},
	'┬': {false, true, true, true},
	'┴': {true, false, true, true},
	'┼': {true, true, true, true},
}

// connectors: all chars that carry connections (for neighbor detection).
var connectors = map[rune]sides{
	'─': {false, false, true, true},
	'│': {true, true, false, false},
	'┌': {false, true, false, true},
	'┐': {false, true, true, false},
	'└': {true, false, false, true},
	'┘': {true, false, true, false},
	'├': {true, true, false, true},
	'┤': {true, true, true, false},
	'┬': {false, true, true, true},
	'┴': {true, false, true, true},
	'┼': {true, true, true, true},
	'►': {false, false, true, false},
	'◄': {false, false, false, true},
	'▼': {true, false, false, false},
	'▲': {false, true, false, false},
}

// sidesChar: reverse map — connectivity tuple → char.
var sidesChar = map[sides]rune{}

func init() {
	for ch, s := range boxChars {
		sidesChar[s] = ch
	}
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	var lines [][]rune
	for scanner.Scan() {
		lines = append(lines, []rune(scanner.Text()))
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	maxW := 0
	for _, l := range lines {
		if len(l) > maxW {
			maxW = len(l)
		}
	}
	// Pad to uniform width so neighbor lookups are safe.
	for i := range lines {
		for len(lines[i]) < maxW {
			lines[i] = append(lines[i], ' ')
		}
	}

	h := len(lines)
	get := func(r, c int) rune {
		if r < 0 || r >= h || c < 0 || c >= maxW {
			return ' '
		}
		return lines[r][c]
	}

	for r := 0; r < h; r++ {
		for c := 0; c < maxW; c++ {
			ch := get(r, c)
			if _, ok := boxChars[ch]; !ok {
				continue
			}
			// A side is active if the neighbor's char connects toward us.
			want := sides{
				up:    connectors[get(r-1, c)].down,
				down:  connectors[get(r+1, c)].up,
				left:  connectors[get(r, c-1)].right,
				right: connectors[get(r, c+1)].left,
			}
			if fixed, ok := sidesChar[want]; ok {
				lines[r][c] = fixed
			}
		}
	}

	w := bufio.NewWriter(os.Stdout)
	for _, l := range lines {
		fmt.Fprintln(w, strings.TrimRight(string(l), " "))
	}
	w.Flush()
}
