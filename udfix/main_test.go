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
