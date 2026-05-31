#!/usr/bin/env python3
# Ant stigmergy — headless mp4 / gif.
# Deps: pip install numpy opencv-python   (+ imageio for --gif)
# Run:  ./ant_coordination.py --variant bloom --speed 2 --gif \
#           --text "Arizuko 0.49.0" "Shortest path always wins"

import argparse
import math
import sys

import cv2
import numpy as np

W, H = 1080, 1920
CELL = 10
COLS = W // CELL  # 108
ROWS = H // CELL  # 192

# Food placed at y~0.45-0.56 (midscreen); nest at y=0.72.
# Distance ~250-430 px -> random walk finds food in seconds with N ants.
VARIANTS = {
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
        'foods': [(0.28, 0.45), (0.72, 0.45)],
        'col_f': (220, 50, 20),
        'col_h': (20, 80, 220),
    },
    'race': {  # 3 sources at different distances — closest colonised first
        'n': 340,
        'evap': 0.991,
        'diffuse': 0.09,
        'trail_f': 130,
        'trail_h': 35,
        'speed': 2.8,
        'wand': 0.24,
        'sense': 24,
        'nest': (0.50, 0.72),
        'foods': [(0.50, 0.50), (0.22, 0.38), (0.78, 0.38)],
        'col_f': (255, 200, 0),
        'col_h': (60, 40, 200),
    },
    'bloom': {  # slow decay + heavy blur = glowing cloud trails
        'n': 240,
        'evap': 0.9985,
        'diffuse': 0.30,
        'trail_f': 45,
        'trail_h': 10,
        'speed': 2.4,
        'wand': 0.30,
        'sense': 20,
        'nest': (0.50, 0.72),
        'foods': [(0.25, 0.45), (0.75, 0.45)],
        'col_f': (255, 110, 0),
        'col_h': (0, 60, 255),
    },
    'chaos': {  # 5 sources, 500 ants, fast decay — frantic competition
        'n': 500,
        'evap': 0.983,
        'diffuse': 0.04,
        'trail_f': 160,
        'trail_h': 50,
        'speed': 3.0,
        'wand': 0.32,
        'sense': 20,
        'nest': (0.50, 0.72),
        'foods': [(0.20, 0.42), (0.50, 0.33), (0.80, 0.42), (0.15, 0.56), (0.85, 0.56)],
        'col_f': (0, 255, 160),
        'col_h': (255, 0, 110),
    },
}

DK = np.ones((3, 3), dtype=np.float32) / 9.0  # 3x3 box-blur diffusion kernel


def cell_val(grid, x, y):
    r = int(max(0, min(ROWS - 1, y / CELL)))
    c = int(max(0, min(COLS - 1, x / CELL)))
    return grid[r, c]


def sniff(grid, x, y, a, off, sense):
    return cell_val(grid, x + math.cos(a + off) * sense, y + math.sin(a + off) * sense)


def put_centered(frame, text, y, scale, color, thick):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)
    x = (W - tw) // 2
    cv2.putText(
        frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 3, cv2.LINE_AA
    )
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', default='default', choices=VARIANTS)
    ap.add_argument(
        '--frames', type=int, default=1200, help='rendered frames (1200 = 20 s @ 60 fps)'
    )
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--speed', type=int, default=1, help='sim steps per rendered frame (timelapse)')
    ap.add_argument('--gif', action='store_true', help='also write a 270x480 GIF at 15 fps')
    ap.add_argument('--text', nargs='+', default=[], metavar='LINE', help='"version" "tagline"')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    v = VARIANTS[args.variant]
    out = args.out or f'ant_{args.variant}.mp4'
    sense = v['sense']
    pi = math.pi
    rng = np.random.default_rng()

    ph_f = np.zeros((ROWS, COLS), dtype=np.float32)  # food pheromone
    ph_h = np.zeros((ROWS, COLS), dtype=np.float32)  # home pheromone

    nest = (int(v['nest'][0] * W), int(v['nest'][1] * H))
    foods = [(int(fx * W), int(fy * H)) for fx, fy in v['foods']]

    angles = rng.uniform(0, 2 * pi, v['n'])
    radii = rng.uniform(0, 8, v['n'])
    ants = [
        {
            'x': float(nest[0] + radii[i] * math.cos(angles[i])),
            'y': float(nest[1] + radii[i] * math.sin(angles[i])),
            'a': float(angles[i]),
            'food': False,
        }
        for i in range(v['n'])
    ]

    # pre-seed scouts near each food source carrying food toward nest
    # so trails start forming from frame 1, not after random discovery
    scouts = max(8, v['n'] // (len(foods) * 8))
    for si, (fx, fy) in enumerate(foods):
        base_a = math.atan2(nest[1] - fy, nest[0] - fx)
        for j in range(scouts):
            idx = si * scouts + j
            if idx >= len(ants):
                break
            ants[idx].update(
                {
                    'x': float(fx + rng.uniform(-12, 12)),
                    'y': float(fy + rng.uniform(-12, 12)),
                    'a': float(base_a + rng.uniform(-0.5, 0.5)),
                    'food': True,
                }
            )

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(out, fourcc, args.fps, (W, H))
    if not vw.isOpened():
        sys.exit('VideoWriter failed — check opencv-python install')

    gif_frames = []
    gif_out = ''
    gif_stride = max(1, args.fps // 15)
    gw, gh = int(W * 0.25), int(H * 0.25)  # 270x480
    if args.gif:
        try:
            import imageio  # noqa: PLC0415
        except ImportError:
            sys.exit('--gif requires: pip install imageio')
        gif_out = out.rsplit('.', 1)[0] + '.gif'

    cf, ch = v['col_f'], v['col_h']

    def step():
        wands = rng.uniform(-v['wand'], v['wand'], len(ants))
        for idx, ant in enumerate(ants):
            x, y, a = ant['x'], ant['y'], ant['a']
            tgt = ph_h if ant['food'] else ph_f
            sl = sniff(tgt, x, y, a, -pi / 5, sense)
            sf = sniff(tgt, x, y, a, 0, sense)
            sr = sniff(tgt, x, y, a, pi / 5, sense)
            if not (sf > sl and sf > sr):
                if sl > sr:
                    a -= 0.18
                elif sr > sl:
                    a += 0.18
            a += float(wands[idx])
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
                ph_f[gr, gc] = min(255.0, ph_f[gr, gc] + v['trail_f'])
            else:
                ph_h[gr, gc] = min(255.0, ph_h[gr, gc] + v['trail_h'])
            nx, ny = nest
            if ant['food'] and math.hypot(x - nx, y - ny) < 18:
                ant['food'] = False
                a += pi
            else:
                for pfx, pfy in foods:
                    if not ant['food'] and math.hypot(x - pfx, y - pfy) < 18:
                        ant['food'] = True
                        a += pi
                        break
            ant['x'], ant['y'], ant['a'] = x, y, a

    for fi in range(args.frames):
        for _ in range(args.speed):
            ph_f[:] = cv2.filter2D(ph_f, -1, DK) * v['diffuse'] + ph_f * (1 - v['diffuse'])
            ph_h[:] = cv2.filter2D(ph_h, -1, DK) * v['diffuse'] + ph_h * (1 - v['diffuse'])
            step()
            ph_f *= v['evap']
            ph_h *= v['evap']

        fv = np.repeat(np.repeat(ph_f, CELL, axis=0), CELL, axis=1)
        hv = np.repeat(np.repeat(ph_h, CELL, axis=0), CELL, axis=1)
        img = np.zeros((H, W, 3), dtype=np.float32)
        img[:, :, 0] += fv * (cf[2] / 255.0) + hv * (ch[2] / 255.0)  # B
        img[:, :, 1] += fv * (cf[1] / 255.0) + hv * (ch[1] / 255.0)  # G
        img[:, :, 2] += fv * (cf[0] / 255.0) + hv * (ch[0] / 255.0)  # R
        np.clip(img, 0, 255, out=img)
        frame = img.astype(np.uint8)

        cv2.circle(frame, nest, 16, (50, 220, 255), -1)
        for f in foods:
            cv2.circle(frame, f, 13, (110, 230, 70), -1)

        for ant in ants:
            ix, iy = int(ant['x']), int(ant['y'])
            if 0 <= ix < W and 0 <= iy < H:
                a = ant['a']
                tip = (ix + int(math.cos(a) * 6), iy + int(math.sin(a) * 6))
                col = (110, 230, 70) if ant['food'] else (200, 190, 160)
                cv2.line(frame, (ix, iy), tip, col, 1)
                cv2.circle(frame, (ix, iy), 2, col, -1)

        if args.text:
            alpha = min(1.0, fi / (args.fps * 1.5))
            if alpha > 0:
                overlay = frame.copy()
                put_centered(overlay, args.text[0], 130, 2.6, (255, 255, 255), 4)
                if len(args.text) > 1:
                    put_centered(overlay, args.text[1], H - 90, 1.5, (200, 200, 200), 3)
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        vw.write(frame)
        if args.gif and fi % gif_stride == 0:
            small = cv2.resize(frame, (gw, gh))
            gif_frames.append(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))

        if fi % 60 == 0:
            print(  # noqa: T201
                f'\r  [{args.variant} x{args.speed}] {100 * fi // args.frames:3d}%',
                end='',
                flush=True,
            )

    vw.release()
    if gif_frames:
        import imageio  # noqa: PLC0415

        imageio.mimsave(gif_out, gif_frames, fps=15, loop=0)

    extra = f', {gif_out}' if gif_frames else ''
    print(f'\ndone → {out}{extra}')  # noqa: T201


if __name__ == '__main__':
    main()
