# my-video — HyperFrames starter

Build videos with HTML/CSS, animate with GSAP, render to MP4 with FFmpeg.

## Setup
- Node 22+, FFmpeg installed (`ffmpeg -version`)
- `npm install` (installs GSAP)
- `npx hyperframes browser ensure` (downloads headless Chrome for rendering)

## Use
- `npm run dev` — live preview in the browser
- `npm run check` — lint and validate the composition
- `npm run render` — render to MP4 in `renders/`

## Tools
- **HyperFrames** — turns an HTML page into a video: seeks each frame in headless Chrome and screenshots it.
- **GSAP** — the animation timeline HyperFrames seeks through (fades, moves, easing).
- **FFmpeg** — encodes the frames (and audio) into the final MP4.

GSAP is loaded from `vendor/gsap.min.js` so renders work offline.
