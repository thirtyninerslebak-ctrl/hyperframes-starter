# Ang Anino sa Kagubatan — Episode 1: Ang Buhay sa Sitio

A 3-minute animatic of Episode 1, built from the storyboard: 30 shots, 16:9, 1920×1080, 24 fps,
with camera moves, color grading, Filipino/Hiligaynon subtitles with English translations,
and a music + sound-design bed.

Each shot is currently the storyboard panel. Replace them with real generated clips
using the prompts in **SHOT_PROMPTS.md**.

## Files
- `tools/build.py` — the shot list: timings, camera moves, grades, dialogue. Generates `index.html` and `subtitles.srt`.
- `tools/template.html` — the page layout, styling and GSAP animation.
- `tools/prep_shots.py` — cuts the 30 panels out of `assets/storyboard.webp` into `assets/shots/`.
- `tools/make_audio.py` — generates `audio/soundtrack.wav` (guitar, birds, crickets, night drone, sting). No voices.
- `SHOT_PROMPTS.md` — character sheet + prompts for generating the real clips.
- `subtitles.srt` — dialogue and narration with timings, for voice recording or an editor.

## Make the video
```bash
npm run build    # shot list -> index.html
npm run dev      # preview in the browser
npm run render   # HyperFrames + GSAP -> renders/video-only.mp4 (24 fps)
npm run audio    # numpy + FFmpeg -> audio/soundtrack.wav
npm run final    # FFmpeg: video + soundtrack -> renders/ang-anino-sa-kagubatan-ep1.mp4
```
