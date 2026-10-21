"""Speaks every dialogue/narration line from tools/build.py and places it on the timeline.

Usage: python3 tools/make_voices.py audio/voices.wav
- Text-to-speech: Google Translate's Filipino (tl) voice. One base voice, so each
  character gets their own pitch / pace / effects with FFmpeg (rubberband).
- Each line starts at its subtitle time and is sped up slightly if it would run
  past the subtitle's end.
Replace with recorded actors later: drop audio/voices.wav and mix real takes instead.
"""
import os, sys, subprocess, urllib.parse, urllib.request, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import LINES  # (start, end, speaker, line, english, style)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "audio", "voices")
SR = 48000

# pitch: frequency ratio (0.75 = about 5 semitones down); tempo: speaking speed
VOICES = {
    "NARRATOR":   dict(pitch=0.80, tempo=0.95, fx="aecho=0.8:0.6:45|90:0.18|0.10,bass=g=3", gain=1.0),
    "ALING ROSA": dict(pitch=0.94, tempo=1.06, fx="highpass=f=90", gain=1.0),
    "DANIEL":     dict(pitch=0.74, tempo=1.02, fx="bass=g=2", gain=1.05),
    "MARA":       dict(pitch=1.00, tempo=1.00, fx="highpass=f=90", gain=0.95),
    "DRIVER":     dict(pitch=0.70, tempo=0.95, fx="bass=g=3", gain=1.05),
    "LOLA ISING": dict(pitch=0.90, tempo=0.82, fx="vibrato=f=5.5:d=0.12,lowpass=f=6500", gain=0.95),
    "JUNJUN":     dict(pitch=0.84, tempo=1.05, fx="highpass=f=100", gain=1.0),
    "TINIG":      dict(pitch=0.92, tempo=0.78,
                       fx="highpass=f=350,lowpass=f=5000,tremolo=f=6:d=0.3,aecho=0.8:0.7:120|260|420:0.35|0.25|0.15",
                       gain=0.75),
}


def tts(text):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(text.encode()).hexdigest()[:12]
    path = os.path.join(CACHE, f"raw_{key}.mp3")
    if not os.path.exists(path):
        url = ("https://translate.googleapis.com/translate_tts?ie=UTF-8&client=gtx&tl=tl&q="
               + urllib.parse.quote(text))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())


TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,")


def rms_db(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "astats", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    overall = err.split("Overall")[-1]
    return float([l for l in overall.splitlines() if "RMS level" in l][0].split()[-1])


def render_line(raw, wav, who, v, tempo):
    if who == "TINIG":
        # quiet octave-down shadow under the whisper
        chain = (f"{TRIM}aresample={SR},rubberband=pitch={v['pitch']}:tempo={tempo:.3f},asplit[a][b];"
                 f"[b]rubberband=pitch=0.5,volume=0.35[lo];[a][lo]amix=inputs=2:normalize=0,"
                 f"{v['fx']},volume={v['gain']}")
    else:
        chain = (f"{TRIM}aresample={SR},rubberband=pitch={v['pitch']}:tempo={tempo:.3f}:formant=shifted,"
                 f"{v['fx']},volume={v['gain']}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-filter_complex", chain,
                    "-ac", "1", wav], check=True)


def main(out):
    placed = []
    for i, (a, b, who, line, eng, style) in enumerate(LINES):
        v = VOICES[who]
        raw = tts(line)
        wav = os.path.join(CACHE, f"line{i:02d}.wav")
        window = (b - a) - 0.15
        tempo = v["tempo"]
        for attempt in range(2):
            render_line(raw, wav, who, v, tempo)
            d = dur(wav)
            if d <= window or attempt == 1:
                break
            tempo = min(v["tempo"] * 1.35, tempo * d / window)
        if rms_db(wav) > -8:  # a filter glitched (clipped noise): redo without effects
            render_line(raw, wav, who, dict(v, fx="volume=1"), tempo)
            if rms_db(wav) > -8:
                raise SystemExit(f"voice line {i} is distorted")
        target = -25.0 if who == "TINIG" else -20.0   # even out loudness between characters
        gain_db = target - rms_db(wav)
        tmp = wav + ".tmp.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af",
                        f"volume={gain_db:.2f}dB,alimiter=limit=0.9", tmp], check=True)
        os.replace(tmp, wav)
        d = dur(wav)
        placed.append((a + 0.08, wav))
        print(f"{a:6.1f}s {who:<10} {d:4.1f}s / window {b - a:4.1f}s  {line[:48]}")

    # Lay every line on a 180 s track.
    inputs, filters = [], []
    for k, (t, wav) in enumerate(placed):
        inputs += ["-i", wav]
        ms = int(t * 1000)
        filters.append(f"[{k}]adelay={ms}|{ms},apad=whole_dur=180[d{k}]")
    mix = "".join(f"[d{k}]" for k in range(len(placed)))
    filters.append(f"{mix}amix=inputs={len(placed)}:normalize=0:duration=longest,atrim=0:180,"
                   f"pan=stereo|c0=c0|c1=c0[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(filters), "-map", "[out]", "-ar", str(SR), out],
                   check=True)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "audio", "voices.wav"))
