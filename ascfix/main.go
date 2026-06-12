package main

import (
	"bufio"
	"fmt"
	"os"
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
	fix(lines)
	w := bufio.NewWriter(os.Stdout)
	for _, line := range lines {
		fmt.Fprintln(w, string(line))
	}
	if err := w.Flush(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
