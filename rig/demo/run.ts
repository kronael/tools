const R = "\x1b[0m";
const B = "\x1b[1m";
const D = "\x1b[2m";
const G = "\x1b[32m";
const C = "\x1b[36m";
const Y = "\x1b[33m";
const M = "\x1b[35m";

const PROMPT = `${G}~/project ${D}$${R} `;

async function type(cmd: string) {
  process.stdout.write(PROMPT);
  for (const ch of cmd) {
    process.stdout.write(ch);
    await Bun.sleep(38);
  }
  await Bun.sleep(280);
  process.stdout.write("\n");
}

function h1(s: string) {
  console.log(`\n${C}${B}── ${s}${R}\n`)
}

function story(s: string) {
  console.log(`${Y}» ${s}${R}`)
}

function clear() {
  process.stdout.write("\x1b[2J\x1b[H")
}

// ── Title card ───────────────────────────────────────────────────────
clear();
await Bun.sleep(400);
console.log(`\n\n  ${B}${C}rig${R}  ${D}—${R}  ${B}ripgit${R}`);
console.log(`  ${D}upstream-only git workflow toolkit${R}\n`);
console.log(`  ${D}checkout  push  rebase  merge  fixup${R}`);
console.log(`  ${D}gl  gis  gig  gitg  gp  gpc  gpa${R}\n`);
await Bun.sleep(2800);

// ── Section 1: Daily orientation ────────────────────────────────────
clear();
h1("Daily orientation");
story("Where am I? What changed?");
await Bun.sleep(600);

await type("gl");
console.log(
  `${G}a1b2c3d${R} feat: add retry logic to api client
${G}e4f5678${R} fix: handle empty response body
${G}9ab0cde${R} chore: update dependencies
${G}1f23456${R} feat: initial api client
${G}789abcd${R} docs: add usage examples`,
);
await Bun.sleep(1400);

await type("gis");
console.log(` M src/client.ts`);
await Bun.sleep(1000);

await type("gig");
console.log(
  `${G}*${R} ${G}a1b2c3d${R} (${Y}HEAD${R}) feat: retry logic
${G}*${R} ${G}e4f5678${R} (${M}origin/feature/retry${R}) fix: empty response
${G}*${R} ${G}9ab0cde${R} chore: deps
${G}/${R}
${G}*${R} ${G}1f23456${R} (${M}origin/main${R}) feat: init api client`,
);
await Bun.sleep(1800);

// ── Section 2: Checkout ──────────────────────────────────────────────
clear();
h1("Checkout a branch");
story("rco — fetch + checkout origin/branch (detached HEAD)");
await Bun.sleep(600);

await type("rco feature/auth");
console.log(`${D}Fetching...
  9ab0cde..7c8d9e0  feature/auth -> origin/feature/auth${R}`);
await Bun.sleep(500);
console.log(`HEAD is now at 7c8d9e0 feat: add token refresh`);
await Bun.sleep(1000);

await type("gl");
console.log(
  `${G}7c8d9e0${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies
${G}1f23456${R} feat: initial api client`,
);
await Bun.sleep(1400);

// ── Section 3: Rebase + push ─────────────────────────────────────────
clear();
h1("Rebase + push");
story("rir — interactive rebase on origin/main, then push");
await Bun.sleep(600);

await type("rir main");
console.log(
  `${D}Fetching...
  1f23456..3d4e5f6  main -> origin/main${R}
Successfully rebased and updated detached HEAD.`,
);
await Bun.sleep(1200);

await type("rip feature/auth");
console.log(
  `${D}To github.com:acme/project.git
   9ab0cde..7c8d9e0  HEAD -> feature/auth${R}`,
);
await Bun.sleep(1600);

// ── Section 4: Merge workflow ────────────────────────────────────────
clear();
h1("Merge workflow");
story("Checkout main, merge feature, push");
await Bun.sleep(600);

await type("rco main");
console.log(
  `${D}Fetching...${R}
HEAD is now at 3d4e5f6 chore: bump version`,
);
await Bun.sleep(900);

await type("rim feature/retry");
console.log(
  `${D}Fetching...${R}
Merge made by the 'ort' strategy.
 src/client.ts | 38 ${G}+++++++++++++++++++++++++++++++${R}${M}-------${R}
 1 file changed, 31 insertions(+), 7 deletions(-)`,
);
await Bun.sleep(1200);

await type("rip main");
console.log(
  `${D}To github.com:acme/project.git
   3d4e5f6..b2c1d0e  HEAD -> main${R}`,
);
await Bun.sleep(1600);

// ── Section 5: Fixup squash ──────────────────────────────────────────
clear();
h1("Squash fixup commits");
story("riq auto-squashes commits prefixed with 'fixup:'");
await Bun.sleep(600);

await type("gl");
console.log(
  `${Y}f1e2d3c${R} fixup: remove debug log
${Y}b4a5968${R} fixup: correct off-by-one
${G}7c8d9e0${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies`,
);
await Bun.sleep(1400);

await type("riq");
console.log(`Successfully rebased and updated detached HEAD.`);
await Bun.sleep(700);

await type("gl");
console.log(
  `${G}2e3f4a5${R} feat: add token refresh
${G}9ab0cde${R} chore: update dependencies`,
);
await Bun.sleep(1800);

// ── Summary ──────────────────────────────────────────────────────────
clear();
console.log(`\n  ${B}${C}rig${R}  command reference\n`);
console.log(`  ${C}${B}rco${R} ${D}[branch]${R}    fetch + checkout origin (detached)`);
console.log(`  ${C}${B}rip${R} ${D}[branch]${R}    push HEAD → origin/branch`);
console.log(`  ${C}${B}rir${R} ${D}[branch]${R}    fetch + rebase -i origin`);
console.log(`  ${C}${B}rim${R} ${D}[branch]${R}    fetch + merge origin`);
console.log(`  ${C}${B}riq${R}             auto-squash fixup commits\n`);
console.log(`  ${G}${B}gl${R}              git log --oneline -20`);
console.log(`  ${G}${B}gis${R}             git status -uno`);
console.log(`  ${G}${B}gig${R}  ${G}${B}gitg${R}      graph log (simplified / full)`);
console.log(`  ${G}${B}gp${R}  ${G}${B}gpc${R}  ${G}${B}gpa${R}  cherry-pick / continue / abort\n`);
console.log(`  ${D}cd rig && make install${R}\n`);
await Bun.sleep(5000);
