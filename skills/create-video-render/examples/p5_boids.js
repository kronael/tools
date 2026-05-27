// Boids flocking — emergent coordination from three local rules (Reynolds).
// Each agent steers by separation + alignment + cohesion against neighbors;
// global order emerges with no leader. The coordination metaphor for a
// distributed agent system.
//
// Render to mp4:
//   1. Load in a p5 sketch with the p5.capture addon (github.com/tapioca24/p5.capture)
//   2. P5Capture.setDefaultOptions({ format: 'mp4', framerate: 60 })
//   3. Run; it records frames to a webm/mp4. Or screen-capture the canvas.
//
// Headless alternative: run under node-canvas + ffmpeg piping each frame.

const N = 180;
const R = 60;        // neighbor radius
const MAXV = 3.2;
const boids = [];

function setup() {
  createCanvas(1080, 1920);   // 9:16 vertical
  for (let i = 0; i < N; i++) {
    boids.push({
      p: createVector(random(width), random(height)),
      v: p5.Vector.random2D().mult(random(1, MAXV)),
    });
  }
}

function steer(b) {
  const sep = createVector(), ali = createVector(), coh = createVector();
  let n = 0;
  for (const o of boids) {
    if (o === b) continue;
    const d = b.p.dist(o.p);
    if (d > 0 && d < R) {
      sep.add(p5.Vector.sub(b.p, o.p).div(d * d));
      ali.add(o.v);
      coh.add(o.p);
      n++;
    }
  }
  if (n > 0) {
    ali.div(n).setMag(MAXV).sub(b.v).limit(0.06);
    coh.div(n).sub(b.p).setMag(MAXV).sub(b.v).limit(0.05);
    sep.setMag(MAXV).sub(b.v).limit(0.09);
    b.v.add(sep).add(ali).add(coh).limit(MAXV);
  }
}

function draw() {
  background(8, 18, 17);          // near-black
  stroke(58, 195, 188);          // one accent
  strokeWeight(3);
  for (const b of boids) {
    steer(b);
    b.p.add(b.v);
    if (b.p.x < 0) b.p.x += width;
    if (b.p.x > width) b.p.x -= width;
    if (b.p.y < 0) b.p.y += height;
    if (b.p.y > height) b.p.y -= height;
    point(b.p.x, b.p.y);
  }
}
