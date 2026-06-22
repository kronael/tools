const R = "\x1b[0m"
const B = "\x1b[1m"
const D = "\x1b[2m"
const G = "\x1b[32m"
const C = "\x1b[36m"
const Y = "\x1b[33m"
const M = "\x1b[35m"

const PROMPT = `${G}~/project ${D}$${R} `

async function type(cmd: string) {
  process.stdout.write(PROMPT)
  for (const ch of cmd) {
    process.stdout.write(ch)
    await Bun.sleep(38)
  }
  await Bun.sleep(280)
  process.stdout.write("\n")
}

function h1(s: string) {
  console.log(`\n${C}${B}── ${s}${R}\n`)
}

function story(s: string) {
  console.log(`${Y}» ${s}${R}`)
}

function note(s: string) {
  console.log(`  ${D}${s}${R}`)
}

function clear() {
  process.stdout.write("\x1b[2J\x1b[H")
}

// ── Title card ───────────────────────────────────────────────────────
clear()
await Bun.sleep(400)
console.log(`\n\n  ${B}${C}rig${R}  ${D}—${R}  ${B}ripgit${R}\n`)
console.log(`  ${B}No local branches. Work directly from origin.${R}\n`)
console.log(`  ${D}You grab a remote branch, make changes, push back.${R}`)
console.log(`  ${D}No checkout -b. No tracking. No cleanup.${R}\n`)
await Bun.sleep(3200)

// ── Section 1: The old way (briefly) ────────────────────────────────
clear()
h1("The usual way to start on a remote branch")
story("Five commands before you can even start working")
await Bun.sleep(800)

await type("git fetch origin")
await type("git checkout -b feature origin/feature")
await type("# ... do work ...")
await type("git push -u origin feature")
await type("git branch -d feature  # cleanup later")
await Bun.sleep(1000)
console.log(`\n  ${Y}» With rig: one command. No branch created.${R}\n`)
await Bun.sleep(2200)

// ── Section 2: Orientation ───────────────────────────────────────────
clear()
h1("Know where you are")
story("gl — last 20 commits at a glance")
await Bun.sleep(600)

await type("gl")
console.log(
  `${G}a1b2c3d${R} feat: add retry logic to api client
${G}e4f5678${R} fix: handle empty response body
${G}9ab0cde${R} chore: update dependencies
${G}1f23456${R} feat: initial api client
${G}789abcd${R} docs: add usage examples`,
)
await Bun.sleep(1800)

story("gis — what changed? (staged + tracked only, no noise)")
await Bun.sleep(600)

await type("gis")
console.log(` M src/client.ts`)
await Bun.sleep(1400)

story("gig — the whole branch graph, simplified")
await Bun.sleep(600)

await type("gig")
console.log(
  `${G}*${R} ${G}a1b2c3d${R} (${Y}HEAD${R}) feat: retry logic
${G}*${R} ${G}e4f5678${R} (${M}origin/feature/retry${R}) fix: empty response
${G}*${R} ${G}9ab0cde${R} chore: deps
${G}/${R}
${G}*${R} ${G}1f23456${R} (${M}origin/main${R}) feat: init api client`,
)
note("Each * is a commit. Branches show where origin pointers are.")
await Bun.sleep(2200)

// ── Section 3: Checkout ──────────────────────────────────────────────
clear()
h1("Grab a remote branch — no local branch created")
story("rco = rig checkout. Fetches first, then puts you on that commit.")
await Bun.sleep(800)

await type("rco feature/auth")
console.log(`${D}Fetching...
  9ab0cde..7c8d9e0  feature/auth -> origin/feature/auth${R}`)
await Bun.sleep(400)
console.log(`HEAD is now at 7c8d9e0 feat: add token refresh`)
await Bun.sleep(1400)

note('"HEAD is now at" = detached HEAD. You are ON the commit.')
note("No local branch exists. This is intentional — and freeing.")
await Bun.sleep(2000)

await type("gl")
console.log(
  `${G}7c8d9e0${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies
${G}1f23456${R} feat: initial api client`,
)
await Bun.sleep(1600)

// ── Section 4: Push back to origin ──────────────────────────────────
clear()
h1("Make changes, push back")
story("rip = rig push. Detects which remote branch you came from.")
await Bun.sleep(800)

note("# ... you edited files, ran git add, git commit ...")
await Bun.sleep(1200)

await type("rip")
console.log(
  `${D}To github.com:acme/project.git
   7c8d9e0..3f1a8b2  HEAD -> feature/auth${R}`,
)
await Bun.sleep(1400)

note("No branch name needed — rip walks ancestry to find origin/feature/auth.")
note("No -u, no tracking config, no cleanup. Done.")
await Bun.sleep(2200)

// ── Section 5: Rebase workflow ───────────────────────────────────────
clear()
h1("Keep history clean: rebase before push")
story("rir = rig rebase. Fetch + interactive rebase on origin/branch.")
await Bun.sleep(800)

await type("rir main")
console.log(
  `${D}Fetching...
  1f23456..3d4e5f6  main -> origin/main${R}
Successfully rebased and updated detached HEAD.`,
)
await Bun.sleep(1600)

story("Clean linear history. Now push.")
await Bun.sleep(600)

await type("rip")
console.log(
  `${D}To github.com:acme/project.git
   9ab0cde..3f1a8b2  HEAD -> feature/auth${R}`,
)
await Bun.sleep(1800)

// ── Section 6: Merge workflow ────────────────────────────────────────
clear()
h1("Merge a feature into main")
story("rco main, then rim to merge the feature branch in, then rip.")
await Bun.sleep(800)

await type("rco main")
console.log(
  `${D}Fetching...${R}
HEAD is now at 3d4e5f6 chore: bump version`,
)
await Bun.sleep(1200)

await type("rim feature/retry")
console.log(
  `${D}Fetching...${R}
Merge made by the 'ort' strategy.
 src/client.ts | 38 ${G}+++++++++++++++++++++++++++++${R}${M}-------${R}
 1 file changed, 31 insertions(+), 7 deletions(-)`,
)
await Bun.sleep(1600)

await type("rip")
console.log(
  `${D}To github.com:acme/project.git
   3d4e5f6..b2c1d0e  HEAD -> main${R}`,
)
await Bun.sleep(1800)

// ── Section 7: Fixup squash ──────────────────────────────────────────
clear()
h1("Squash 'fixup' commits before pushing")
story("Prefix a commit with 'fixup:' to mark it for squashing.")
note("riq finds them automatically and squashes into the parent commit.")
await Bun.sleep(1000)

await type("gl")
console.log(
  `${Y}f1e2d3c${R} fixup: remove debug log
${Y}b4a5968${R} fixup: correct off-by-one
${G}7c8d9e0${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies`,
)
note("Two sloppy fixup commits sitting on top of the real commit.")
await Bun.sleep(1800)

await type("riq")
console.log(`Successfully rebased and updated detached HEAD.`)
await Bun.sleep(800)

await type("gl")
console.log(
  `${G}2e3f4a5${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies`,
)
note("Clean. One commit. Ready to push.")
await Bun.sleep(2000)

// ── Summary ──────────────────────────────────────────────────────────
clear()
console.log(`\n  ${B}${C}rig${R}  workflow in full\n`)
console.log(`  ${C}${B}rco${R} ${D}[branch]${R}    fetch + jump to origin/branch  ${D}(no local branch)${R}`)
console.log(`  ${C}${B}rip${R} ${D}[branch]${R}    push HEAD → origin              ${D}(auto-detects branch)${R}`)
console.log(`  ${C}${B}rir${R} ${D}[branch]${R}    fetch + rebase -i on origin     ${D}(clean history)${R}`)
console.log(`  ${C}${B}rim${R} ${D}[branch]${R}    fetch + merge from origin`)
console.log(`  ${C}${B}riq${R}             squash fixup: commits\n`)
console.log(`  ${G}${B}gl${R}   ${G}${B}gis${R}   ${G}${B}gig${R}   ${G}${B}gitg${R}       log · status · graph`)
console.log(`  ${G}${B}gp${R}   ${G}${B}gpc${R}   ${G}${B}gpa${R}          cherry-pick · continue · abort\n`)
console.log(`  ${D}No local branches. Reflog keeps 90 days. Nothing gets lost.${R}\n`)
console.log(`  ${D}cd rig && make install${R}\n`)
await Bun.sleep(6000)
