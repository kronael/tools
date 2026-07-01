"""Kuramoto coupled oscillators converging to phase sync — Manim Community.

The cleanest differential-dynamics demo of coordination: N oscillators with
random natural frequencies, coupled, pull into a common phase. The order
parameter r (mean vector length) rises from ~0 (incoherent) to ~1 (synced).

Render:
    uv run --with manim manim -qh examples/manim_kuramoto.py Kuramoto
    # -ql draft (480p), -qh high (1080p60), -qk 4k
"""

import numpy as np
from manim import BLUE
from manim import YELLOW
from manim import Circle
from manim import Create
from manim import DecimalNumber
from manim import Dot
from manim import Scene
from manim import VGroup
from manim import always_redraw

N = 60
K = 1.6  # coupling strength; > critical Kc → sync
DT = 0.04
STEPS = 260


def simulate():
    rng = np.random.default_rng(7)
    omega = rng.normal(0.0, 0.6, N)  # natural frequencies
    theta = rng.uniform(0, 2 * np.pi, N)  # initial phases
    frames = []
    for _ in range(STEPS):
        z = np.exp(1j * theta)
        r_complex = z.mean()
        r, psi = np.abs(r_complex), np.angle(r_complex)
        theta = theta + DT * (omega + K * r * np.sin(psi - theta))
        frames.append((theta.copy(), r))
    return frames


class Kuramoto(Scene):
    def construct(self):
        frames = simulate()
        ring = Circle(radius=2.6, color=BLUE).set_stroke(width=2, opacity=0.5)
        self.play(Create(ring), run_time=0.6)

        state = {'i': 0}

        def dots():
            theta, _ = frames[state['i']]
            g = VGroup()
            for ph in theta:
                p = ring.point_from_proportion((ph % (2 * np.pi)) / (2 * np.pi))
                g.add(Dot(p, radius=0.06, color=YELLOW))
            return g

        live = always_redraw(dots)
        r_label = always_redraw(
            lambda: DecimalNumber(frames[state['i']][1], num_decimal_places=2)
            .scale(0.8)
            .to_corner((1, 1, 0))
        )
        self.add(live, r_label)

        for i in range(STEPS):
            state['i'] = i
            self.wait(DT)
