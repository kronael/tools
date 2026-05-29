// Ant stigmergy — emergent trail coordination via pheromones.
// Ants search randomly; food-carriers deposit food-pheromone so others can
// find the source. Trails reinforce: more ants → stronger gradient → more
// follow. Two food sources compete; shorter route accumulates faster.
//
// Render to mp4:
//   1. Load in p5 with p5.capture addon (github.com/tapioca24/p5.capture)
//   2. P5Capture.setDefaultOptions({ format: 'mp4', framerate: 60 })
//   3. Or open at editor.p5js.org and screen-capture the canvas.

const N     = 280;   // ant count
const CELL  = 10;    // px per pheromone grid cell
const EVAP  = 0.994; // pheromone decay per frame
const SPEED = 2.6;
const SENSE = 22;    // sense radius px
const WAND  = 0.28;  // random turn magnitude
const TRAIL = 100;   // food-pheromone deposit per step

let COLS, ROWS;
let phFood, phHome;  // pheromone grids [row][col]
let ants = [];
let nest, food;

function setup() {
  createCanvas(1080, 1920);
  pixelDensity(1);
  COLS = ceil(width  / CELL);
  ROWS = ceil(height / CELL);
  phFood = Array.from({ length: ROWS }, () => new Float32Array(COLS));
  phHome = Array.from({ length: ROWS }, () => new Float32Array(COLS));
  nest = createVector(width / 2, height * 0.72);
  food = [
    createVector(width * 0.28, height * 0.28),
    createVector(width * 0.72, height * 0.28),
  ];
  for (let i = 0; i < N; i++) {
    ants.push({
      p: nest.copy().add(p5.Vector.random2D().mult(random(8))),
      a: random(TWO_PI),
      hasFood: false,
    });
  }
}

function cellAt(grid, x, y) {
  const r = constrain(floor(y / CELL), 0, ROWS - 1);
  const c = constrain(floor(x / CELL), 0, COLS - 1);
  return grid[r][c];
}

function sense(grid, x, y, heading, offset) {
  const a = heading + offset;
  return cellAt(grid, x + cos(a) * SENSE, y + sin(a) * SENSE);
}

function stepAnt(ant) {
  const { p, hasFood } = ant;
  const target = hasFood ? phHome : phFood;
  const L = sense(target, p.x, p.y, ant.a, -PI / 5);
  const F = sense(target, p.x, p.y, ant.a,  0);
  const R = sense(target, p.x, p.y, ant.a,  PI / 5);
  if      (F > L && F > R) { /* ahead is strongest — hold course */ }
  else if (L > R)           ant.a -= 0.18;
  else if (R > L)           ant.a += 0.18;
  ant.a += random(-WAND, WAND);

  p.x += cos(ant.a) * SPEED;
  p.y += sin(ant.a) * SPEED;
  if (p.x < 0)      { p.x = 0;      ant.a = PI - ant.a; }
  if (p.x > width)  { p.x = width;  ant.a = PI - ant.a; }
  if (p.y < 0)      { p.y = 0;      ant.a = -ant.a; }
  if (p.y > height) { p.y = height; ant.a = -ant.a; }

  const gc = constrain(floor(p.x / CELL), 0, COLS - 1);
  const gr = constrain(floor(p.y / CELL), 0, ROWS - 1);
  if (hasFood) phFood[gr][gc] = min(255, phFood[gr][gc] + TRAIL);
  else         phHome[gr][gc] = min(255, phHome[gr][gc] + 25);

  if (hasFood && dist(p.x, p.y, nest.x, nest.y) < 18) {
    ant.hasFood = false;
    ant.a += PI;
  }
  for (const f of food) {
    if (!hasFood && dist(p.x, p.y, f.x, f.y) < 18) {
      ant.hasFood = true;
      ant.a += PI;
      break;
    }
  }
}

function draw() {
  loadPixels();
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const fv = phFood[r][c];
      const hv = phHome[r][c];
      for (let dy = 0; dy < CELL; dy++) {
        for (let dx = 0; dx < CELL; dx++) {
          const i = ((r * CELL + dy) * width + c * CELL + dx) * 4;
          pixels[i]     = min(255, fv * 1.6) | 0;  // red  — food trail
          pixels[i + 1] = min(255, hv * 0.8) | 0;  // green — home trail
          pixels[i + 2] = 14;
          pixels[i + 3] = 255;
        }
      }
    }
  }
  updatePixels();

  noStroke();
  fill(255, 220, 50);
  circle(nest.x, nest.y, 32);
  fill(70, 230, 110);
  for (const f of food) circle(f.x, f.y, 26);

  for (const ant of ants) {
    stepAnt(ant);
    fill(ant.hasFood ? color(70, 230, 110) : color(230, 210, 170));
    circle(ant.p.x, ant.p.y, 5);
  }

  for (let r = 0; r < ROWS; r++)
    for (let c = 0; c < COLS; c++) {
      phFood[r][c] *= EVAP;
      phHome[r][c] *= EVAP;
    }
}
