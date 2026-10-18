# Billiards Lab

Interactive two-ball billiards sandbox, built with plain JavaScript and Canvas. No package installation or build required.

## Run

```sh
cd billiards-lab
npm start
```

Open http://127.0.0.1:8765. Requires Python 3. Alternatively, open `index.html` directly in a modern browser. Optional Google Fonts fall back to system fonts when offline.

## Explore

- Drag either ball to position it; click empty cloth to aim.
- Adjust direction and initial speed; place the cue tip on the spin pad or use the spin sliders.
- Positive top spin produces follow, negative produces draw. Side spin influences collision throw and cushion rebound.
- Shoot, pause, reset, scrub the timeline, or choose 0.25×, 0.5×, 1×, 2× playback.
- Dashed lines predict the complete shot. Solid lines show the paths already traveled.
- Presets demonstrate stop, follow, draw and a cut with side spin. Changed friction settings affect preset outcomes.

## Physics

Coordinates and speeds use SI units; table 2.54 × 1.27 m, ball radius 0.028575 m. Equal solid spheres have I = 2mR²/5. The integrator uses 1 ms steps and stores frames every 10 ms.

Cloth contact slip is `(vx - R*wy, vy + R*wx)`. Coulomb friction changes translation and horizontal spin together. Slip impulse is capped at the rolling transition to prevent numerical overshoot. Rolling resistance reduces rolling speed. Vertical spin decays independently.

Ball contacts use normal restitution and a tangential impulse limited by Coulomb friction, transferring linear momentum and vertical spin. Cushion contacts use a simplified vertical-wall impulse with tangential friction. Initial spin comes from a horizontal cue impulse at offsets up to 0.6 radii from center. The spin pad constrains the combined offset.

This is an educational approximation, not a calibrated coaching engine. It excludes pockets, jump shots, masse, cue elevation, squirt, swerve, cloth grain and the full 3D ball-contact model. Horizontal ball spin persists through ball contact; vertical tangential contact impulses are omitted. Prediction is capped at 30 seconds. Very low friction can leave balls moving at that horizon.

Background: [Evan Kiefl, The physics of pool](https://ekiefl.github.io/2020/04/24/pooltool-theory/). The engine is independently implemented, not a pooltool dependency.

## Verify

```sh
npm test
```

Tests cover elastic head-on transfer, linear momentum conservation, collision dissipation, the analytic 5/7 sliding-to-rolling speed, draw/follow behavior, table bounds, finite states, and energy bounds across varied shots.

## Files

- `physics.js`: DOM-independent simulation, also importable in Node.
- `app.js`: controls, trajectories and playback.
- `index.html`, `style.css`: responsive interface.
- `test.js`: physics regression checks.
