# Ang Anino sa Kagubatan — Episode 1: Ang Buhay sa Sitio

A 3-minute animatic of Episode 1, built from the storyboard: 30 shots, 16:9, 1920×1080, 24 fps,
with camera moves, color grading, Filipino/Hiligaynon subtitles with English translations,
a music + sound-design bed, and spoken dialogue/narration.

Each shot is currently the storyboard panel. Replace them with real generated clips
using the prompts in **SHOT_PROMPTS.md**.

## Files
- `tools/build.py` — the shot list: timings, camera moves, grades, dialogue. Generates `index.html` and `subtitles.srt`.
- `tools/template.html` — the page layout, styling and GSAP animation.
- `tools/prep_shots.py` — cuts the 30 panels out of `assets/storyboard.webp` into `assets/shots/`.
- `tools/make_audio.py` — generates `audio/soundtrack.wav` (guitar, birds, crickets, night drone, sting).
- `tools/make_voices.py` — speaks every line with a Filipino text-to-speech voice (Google Translate), shaped per character with FFmpeg, into `audio/voices.wav`. Placeholder until real actors are recorded.
- `SHOT_PROMPTS.md` — character sheet + prompts for generating the real clips.
- `subtitles.srt` — dialogue and narration with timings, for voice recording or an editor.

## Make the video
```bash
npm run build    # shot list -> index.html
npm run dev      # preview in the browser
npm run render   # HyperFrames + GSAP -> renders/video-only.mp4 (24 fps)
npm run audio    # numpy + FFmpeg -> audio/soundtrack.wav
npm run voices   # text-to-speech -> audio/voices.wav
npm run mix      # FFmpeg: music + voices -> audio/final_mix.wav
npm run final    # FFmpeg: video + final mix -> renders/ang-anino-sa-kagubatan-ep1.mp4
```
