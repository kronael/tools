package main

import (
	"strings"
	"testing"
)

func run(in string) string {
	var lines [][]rune
	for _, line := range strings.Split(in, "\n") {
		lines = append(lines, []rune(line))
	}
	fix(lines)
	out := make([]string, len(lines))
	for i, line := range lines {
		out[i] = string(line)
	}
	return strings.Join(out, "\n")
}

func TestFix(t *testing.T) {
	correct := strings.Join([]string{
		"┌─┬─┐",
		"│ │ │",
		"├─┼─┤",
		"│ │ │",
		"└─┴─┘",
	}, "\n")
	arrows := "──► ok\n◄── x\n│\n▼"
	tests := []struct {
		name, in, want string
	}{
		{
			"cross with no stem becomes dash",
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
		{"arrows preserved", arrows, arrows},
		{"correct diagram unchanged", correct, correct},
		{"empty input", "", ""},
		{"single char", "┼", "┼"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := run(tt.in); got != tt.want {
				t.Errorf("got:\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}
