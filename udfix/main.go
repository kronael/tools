// Command udfix rewrites Unicode box-drawing junction characters in an ASCII
// diagram so each junction matches the segments that actually touch it. It
// reads a diagram from stdin and writes the corrected diagram to stdout.
//
// With -lint it does not rewrite: it reports junctions that fail to represent a
// segment that touches them (a real defect) and ASCII arrows, and exits non-zero
// if the diagram is not clean. Lint tolerates a junction that draws *more* arms
// than connect — a tree branch (`├──` with nothing above) is a deliberate stub,
// not an error — so it can gate box diagrams and tree listings alike.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"strings"
)

type sides struct{ up, down, left, right bool }

// subsetOf reports whether every arm of s is also drawn by o.
func (s sides) subsetOf(o sides) bool {
	return (!s.up || o.up) && (!s.down || o.down) &&
		(!s.left || o.left) && (!s.right || o.right)
}

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

// touching returns the sides on which a neighbour connects toward cell (r, c).
func touching(lines [][]rune, r, c int) sides {
	get := func(r, c int) rune {
		if r < 0 || r >= len(lines) || c < 0 || c >= len(lines[r]) {
			return ' '
		}
		return lines[r][c]
	}
	return sides{
		up:    connectors[get(r-1, c)].down,
		down:  connectors[get(r+1, c)].up,
		left:  connectors[get(r, c-1)].right,
		right: connectors[get(r, c+1)].left,
	}
}

// fix rewrites each box-drawing junction in place to the character whose sides
// exactly match the neighboring cells that connect toward it. Cells outside the
// box-drawing set (including arrows and ragged short lines) are left untouched.
func fix(lines [][]rune) {
	for r := range lines {
		for c, ch := range lines[r] {
			if _, ok := boxChars[ch]; !ok {
				continue
			}
			if fixed, ok := sidesChar[touching(lines, r, c)]; ok {
				lines[r][c] = fixed
			}
		}
	}
}

type issue struct {
	row, col int
	msg      string
}

// lint reports diagram defects without mutating. A junction is flagged only when
// a segment touches it that its glyph does not draw (want ⊄ have) — an
// underspecified or wrong junction. A glyph that draws an arm nothing connects to
// (want ⊂ have) is left alone: that is how a tree branch or a deliberate stub
// looks, and flagging it would nag every `├──` listing. ASCII arrows are flagged
// against the box-drawing arrow glyphs.
func lint(lines [][]rune) []issue {
	var issues []issue
	for r := range lines {
		line := lines[r]
		for c, ch := range line {
			have, ok := boxChars[ch]
			if !ok {
				continue
			}
			want := touching(lines, r, c)
			if want.subsetOf(have) {
				continue
			}
			msg := fmt.Sprintf("junction %q does not represent every segment touching it", string(ch))
			if fixed, ok := sidesChar[want]; ok {
				msg += fmt.Sprintf("; expected %q", string(fixed))
			}
			issues = append(issues, issue{r + 1, c + 1, msg})
		}
		for c := 0; c+1 < len(line); c++ {
			if pair := string(line[c : c+2]); pair == "->" || pair == "<-" {
				issues = append(issues, issue{r + 1, c + 1,
					fmt.Sprintf("ASCII arrow %q; use ► ◄ ▲ ▼", pair)})
			}
		}
	}
	return issues
}

// splitDiagram returns the diagram's lines and whether it ended with a newline.
func splitDiagram(input []byte) (lines [][]rune, trailingNewline bool) {
	text := string(input)
	trailingNewline = strings.HasSuffix(text, "\n")
	if trailingNewline {
		text = text[:len(text)-1]
	}
	for _, line := range strings.Split(text, "\n") {
		lines = append(lines, []rune(line))
	}
	return lines, trailingNewline
}

// process fixes an entire diagram. It preserves the input's trailing-newline
// state and returns empty output for empty input.
func process(input []byte) []byte {
	if len(input) == 0 {
		return nil
	}
	lines, trailingNewline := splitDiagram(input)
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
	var lintMode bool
	const lintUsage = "report junction and arrow defects instead of rewriting; exit 1 if any"
	flag.BoolVar(&lintMode, "lint", false, lintUsage)
	flag.BoolVar(&lintMode, "l", false, "alias for --lint")
	flag.Parse()

	input, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	if lintMode {
		if len(input) == 0 {
			return
		}
		lines, _ := splitDiagram(input)
		issues := lint(lines)
		for _, i := range issues {
			fmt.Printf("%d:%d: %s\n", i.row, i.col, i.msg)
		}
		if len(issues) > 0 {
			os.Exit(1)
		}
		return
	}

	if _, err := os.Stdout.Write(process(input)); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
