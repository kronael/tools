# Flavor: GPU fields & swarm coordination

**Pick when**: the visual is a continuous field (reaction-diffusion, fluid, advection) or a many-agent swarm (boids, Vicsek) and you want it in Python/Rust/JS without a full game engine.

All render offline: tick the sim → write a frame → `ffmpeg` the sequence.

| tool | stack | best at | headless mp4 |
|---|---|---|---|
| **Taichi Lang** | Python→GPU JIT | reaction-diffusion, stable-fluid, MPM, millions of particles | `ti.tools.VideoManager` writes mp4/gif |
| **nannou** | Rust/wgpu | reliable boids/Vicsek/generative; long runs without dropped frames | `app.main_window().capture_frame(path)` → PNG seq |
| **VisPy** | Python/GLSL | custom-shader field viz, millions of points @60fps | `canvas.render()` → numpy → imageio; EGL headless |
| **ParaView** | Python/MPI (`pvbatch`) | cinematic 3D PDE/volumetric fields, cluster-scale | off-screen EGL/OSMesa → `SaveAnimation()` |
| **p5.js** | JS | fastest path to a live swarm sketch (~40 lines) | p5.capture addon → mp4 |
| **openFrameworks** | C++ | largest creative-coding addon set | `ofxVideoRecorder` from an FBO |

## Picking within this group

- Plain-Python + GPU speed → **Taichi**.
- Rust reliability / installation-grade → **nannou**.
- Custom GLSL but stay in Python → **VisPy**.
- Big 3D scientific field, cinematic camera → **ParaView**.
- Throwaway prototype or web embed → **p5.js**.

Example: [`../examples/p5_boids.js`](../examples/p5_boids.js) — leaderless flocking from three local rules (separation/alignment/cohesion).

Sources: [Taichi](https://www.taichi-lang.org/) · [nannou](https://github.com/nannou-org/nannou) · [VisPy](https://vispy.org/) · [ParaView pvbatch](https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/pythonAndBatchPvpythonAndPvbatch.html)
