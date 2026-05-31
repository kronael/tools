#!/usr/bin/env python3
# Ant stigmergy — headless mp4 render.
# Deps: pip install numpy opencv-python
# Run:  python3 ant_coordination.py [--variant default|race|bloom|chaos]
#       python3 ant_coordination.py --frames 3600 --fps 60 --out out.mp4

import argparse
import math
import sys

import cv2
import numpy as np

W, H = 1080, 1920
CELL = 10
COLS = W // CELL  # 108
ROWS = H // CELL  # 192

VARIANTS = {
    # two sources, warm red food / cool blue home — the default
    'default': {
        'n': 280,
        'evap': 0.994,
        'diffuse': 0.06,
        'trail_f': 100,
        'trail_h': 25,
        'speed': 2.6,
        'wand': 0.28,
        'sense': 22,
        'nest': (0.50, 0.72),
        'foods': [(0.28, 0.28), (0.72, 0.28)],
        'col_food': (220, 50, 20),
        'col_home': (20, 80, 220),
    },
    # three sources at different distances; shorter path wins first
    'race': {
        'n': 340,
        'evap': 0.991,
        'diffuse': 0.09,
        'trail_f': 130,
        'trail_h': 35,
        'speed': 2.8,
        'wand': 0.24,
        'sense': 24,
        'nest': (0.50, 0.72),
        'foods': [(0.50, 0.35), (0.22, 0.18), (0.78, 0.18)],
        'col_food': (255, 200, 0),
        'col_home': (60, 40, 200),
    },
    # slow evaporation + heavy diffusion = glowing pheromone clouds
    'bloom': {
        'n': 240,
        'evap': 0.9985,
        'diffuse': 0.30,
        'trail_f': 45,
        'trail_h': 10,
        'speed': 2.4,
        'wand': 0.30,
        'sense': 20,
        'nest': (0.50, 0.72),
        'foods': [(0.25, 0.25), (0.75, 0.25)],
        'col_food': (255, 110, 0),
        'col_home': (0, 60, 255),
    },
    # 5 sources, 500 ants, fast decay — frantic competition
    'chaos': {
        'n': 500,
        'evap': 0.983,
        'diffuse': 0.04,
        'trail_f': 160,
        'trail_h': 50,
        'speed': 3.0,
        'wand': 0.32,
        'sense': 20,
        'nest': (0.50, 0.72),
        'foods': [(0.20, 0.20), (0.50, 0.11), (0.80, 0.20), (0.15, 0.50), (0.85, 0.50)],
        'col_food': (0, 255, 160),
        'col_home': (255, 0, 110),
    },
}

DIFFUSE_K = np.ones((3, 3), dtype=np.float32) / 9.0


def cell_val(grid, x, y):
    c = int(max(0, min(COLS - 1, x / CELL)))
    r = int(max(0, min(ROWS - 1, y / CELL)))
    return grid[r, c]


def sniff(grid, x, y, heading, offset, sense):
    a = heading + offset
    return cell_val(grid, x + math.cos(a) * sense, y + math.sin(a) * sense)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', default='default', choices=VARIANTS)
    ap.add_argument('--frames', type=int, default=1800)
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    v = VARIANTS[args.variant]
    out = args.out or f'ant_{args.variant}.mp4'
    sense = v['sense']
    rng = np.random.default_rng()

    ph_food = np.zeros((ROWS, COLS), dtype=np.float32)
    ph_home = np.zeros((ROWS, COLS), dtype=np.float32)

    nest = (int(v['nest'][0] * W), int(v['nest'][1] * H))
    foods = [(int(fx * W), int(fy * H)) for fx, fy in v['foods']]

    angles = rng.uniform(0, 2 * math.pi, v['n'])
    radii = rng.uniform(0, 8, v['n'])
    ants = [
        {
            'x': nest[0] + radii[i] * math.cos(angles[i]),
            'y': nest[1] + radii[i] * math.sin(angles[i]),
            'a': angles[i],
            'food': False,
        }
        for i in range(v['n'])
    ]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(out, fourcc, args.fps, (W, H))
    if not vw.isOpened():
        sys.exit('VideoWriter failed — check opencv-python install')

    pi = math.pi
    cf, ch = v['col_food'], v['col_home']

    for fi in range(args.frames):
        ph_food[:] = cv2.filter2D(ph_food, -1, DIFFUSE_K) * v['diffuse'] + ph_food * (
            1 - v['diffuse']
        )
        ph_home[:] = cv2.filter2D(ph_home, -1, DIFFUSE_K) * v['diffuse'] + ph_home * (
            1 - v['diffuse']
        )

        fv = np.repeat(np.repeat(ph_food, CELL, axis=0), CELL, axis=1)
        hv = np.repeat(np.repeat(ph_home, CELL, axis=0), CELL, axis=1)
        img = np.zeros((H, W, 3), dtype=np.float32)
        img[:, :, 0] += fv * (cf[2] / 255.0) + hv * (ch[2] / 255.0)  # B
        img[:, :, 1] += fv * (cf[1] / 255.0) + hv * (ch[1] / 255.0)  # G
        img[:, :, 2] += fv * (cf[0] / 255.0) + hv * (ch[0] / 255.0)  # R
        np.clip(img, 0, 255, out=img)
        frame = img.astype(np.uint8)

        cv2.circle(frame, nest, 16, (50, 220, 255), -1)
        for f in foods:
            cv2.circle(frame, f, 13, (110, 230, 70), -1)

        wands = rng.uniform(-v['wand'], v['wand'], len(ants))
        for idx, ant in enumerate(ants):
            x, y, a = ant['x'], ant['y'], ant['a']
            target = ph_home if ant['food'] else ph_food
            sl = sniff(target, x, y, a, -pi / 5, sense)
            sf = sniff(target, x, y, a, 0, sense)
            sr = sniff(target, x, y, a, pi / 5, sense)
            if not (sf > sl and sf > sr):
                if sl > sr:
                    a -= 0.18
                elif sr > sl:
                    a += 0.18
            a += wands[idx]

            x += math.cos(a) * v['speed']
            y += math.sin(a) * v['speed']
            if x < 0:
                x = 0
                a = pi - a
            if x > W:
                x = W
                a = pi - a
            if y < 0:
                y = 0
                a = -a
            if y > H:
                y = H
                a = -a

            gc = int(max(0, min(COLS - 1, x / CELL)))
            gr = int(max(0, min(ROWS - 1, y / CELL)))
            if ant['food']:
                ph_food[gr, gc] = min(255.0, ph_food[gr, gc] + v['trail_f'])
            else:
                ph_home[gr, gc] = min(255.0, ph_home[gr, gc] + v['trail_h'])

            nx, ny = nest
            if ant['food'] and math.hypot(x - nx, y - ny) < 18:
                ant['food'] = False
                a += pi
            else:
                for fx, fy in foods:
                    if not ant['food'] and math.hypot(x - fx, y - fy) < 18:
                        ant['food'] = True
                        a += pi
                        break

            ant['x'], ant['y'], ant['a'] = x, y, a
            ix, iy = int(x), int(y)
            if 0 <= ix < W and 0 <= iy < H:
                tip = (ix + int(math.cos(a) * 6), iy + int(math.sin(a) * 6))
                color = (110, 230, 70) if ant['food'] else (200, 190, 160)
                cv2.line(frame, (ix, iy), tip, color, 1)
                cv2.circle(frame, (ix, iy), 2, color, -1)

        ph_food *= v['evap']
        ph_home *= v['evap']

        vw.write(frame)
        if fi % 60 == 0:
            print(f'\r  [{args.variant}] {100 * fi // args.frames:3d}%', end='', flush=True)  # noqa: T201

    vw.release()
    print(f'\ndone → {out}')  # noqa: T201


if __name__ == '__main__':
    main()
