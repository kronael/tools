// Command udfix rewrites Unicode box-drawing junction characters in an ASCII
// diagram so each junction matches the segments that actually touch it. It
// reads a diagram from stdin and writes the corrected diagram to stdout.
package main

import (
	"fmt"
	"io"
	"os"
	"strings"
)

type sides struct{ up, down, left, right bool }

var boxChars = map[rune]sides{
	'─': {left: true, right: true},
	'│': {up: true, down: true},
	'┌': {down: true, right: true},
	'┐': {down: true, left: true},
	'└': {up: true, right: true},
	'┘': {up: true, left: true},
	'├': {up: true, down: true, right: true},
	'┤': {up: true, down: true, left: true},
	'┬': {down: true, left: true, right: true},
	'┴': {up: true, left: true, right: true},
	'┼': {up: true, down: true, left: true, right: true},
}

// Arrows connect but are never rewritten; boxChars merge in via init.
var connectors = map[rune]sides{
	'►': {left: true},
	'◄': {right: true},
	'▼': {up: true},
	'▲': {down: true},
}

var sidesChar = map[sides]rune{}

func init() {
	for ch, s := range boxChars {
		connectors[ch] = s
		sidesChar[s] = ch
	}
}

// fix rewrites each box-drawing junction in place to the character whose sides
// exactly match the neighboring cells that connect toward it. Cells outside the
// box-drawing set (including arrows and ragged short lines) are left untouched.
func fix(lines [][]rune) {
	h := len(lines)
	get := func(r, c int) rune {
		if r < 0 || r >= h || c < 0 || c >= len(lines[r]) {
			return ' '
		}
		return lines[r][c]
	}
	for r := range lines {
		for c, ch := range lines[r] {
			if _, ok := boxChars[ch]; !ok {
				continue
			}
			// A side is active if the neighbor connects toward us.
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
}

// process fixes an entire diagram. It preserves the input's trailing-newline
// state and returns empty output for empty input.
func process(input []byte) []byte {
	if len(input) == 0 {
		return nil
	}
	text := string(input)
	trailingNewline := strings.HasSuffix(text, "\n")
	if trailingNewline {
		text = text[:len(text)-1]
	}
	rawLines := strings.Split(text, "\n")
	lines := make([][]rune, len(rawLines))
	for i, line := range rawLines {
		lines[i] = []rune(line)
	}
	fix(lines)
	var b strings.Builder
	for i, line := range lines {
		if i > 0 {
			b.WriteByte('\n')
		}
		b.WriteString(string(line))
	}
	if trailingNewline {
		b.WriteByte('\n')
	}
	return []byte(b.String())
}

func main() {
	input, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if _, err := os.Stdout.Write(process(input)); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
