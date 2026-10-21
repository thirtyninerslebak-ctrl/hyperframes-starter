"""Builds index.html (the HyperFrames composition) from the shot list below.

Edit SHOTS / LINES / SCENES here, then run:  python3 tools/build.py
Each shot shows assets/shots/shotNN.jpg. To swap in real footage later, put
assets/shots/shotNN.mp4 next to it and rebuild: the video is used instead.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (shot, start, duration, camera move, grade)
# camera move: (scale_from, scale_to, x_from, x_to, y_from, y_to, handheld)
SHOTS = [
    # SCENE 1 - ANG UMAGA SA MALINAW
    (1,   0, 5, (1.00, 1.10,   0,   0,  20, -20, 0), "day"),
    (2,   5, 5, (1.08, 1.08, -60,  60,   0,   0, 0), "day"),
    (3,  10, 5, (1.00, 1.12,   0, -30,   0,   0, 0), "day"),
    (4,  15, 5, (1.02, 1.10,   0,   0,   0,  10, 1), "day"),
    (5,  20, 10, (1.08, 1.08, 80, -80,   0,   0, 0), "day"),
    # SCENE 2 - ANG MAGSASAKA
    (6,  30, 5, (1.10, 1.10,   0,   0,  50, -50, 1), "day"),
    (7,  35, 5, (1.00, 1.08,   0,   0,   0,   0, 0), "day"),
    (8,  40, 5, (1.00, 1.06,   0,  20,   0,   0, 0), "day"),
    (9,  45, 10, (1.02, 1.07,  0,   0,   0,   0, 1), "day"),
    (10, 55, 5, (1.00, 1.08,   0,   0,   0,   0, 0), "day"),
    # SCENE 3 - ANG PAGBALIK
    (11, 60, 5, (1.08, 1.08,  40, -40,   0,   0, 1), "day"),
    (12, 65, 5, (1.08, 1.08, -70,  70,   0,   0, 0), "day"),
    (13, 70, 5, (1.00, 1.08,   0,   0,   0,   0, 1), "day"),
    (14, 75, 10, (1.00, 1.05,  0,   0,   0,   0, 1), "day"),
    (15, 85, 5, (1.00, 1.12,   0,   0,   0,   0, 0), "day"),
    # SCENE 4 - ANG BABALA
    (16, 90, 5, (1.08, 1.08,  60, -60,   0,   0, 0), "warm"),
    (17, 95, 5, (1.00, 1.06,   0,   0,   0,   0, 1), "warm"),
    (18, 100, 5, (1.02, 1.10,  0,   0,   0,   0, 0), "warm"),
    (19, 105, 5, (1.00, 1.05,  0,   0,   0,   0, 1), "warm"),
    (20, 110, 10, (1.00, 1.14, 0, -40,   0,   0, 0), "warm"),
    # SCENE 5 - BAGO DUMILIM
    (21, 120, 5, (1.08, 1.08, -60, 60,   0,   0, 0), "dusk"),
    (22, 125, 5, (1.02, 1.08,  0,   0,   0,   0, 1), "dusk"),
    (23, 130, 5, (1.00, 1.06,  0,  20,   0,   0, 0), "dusk"),
    (24, 135, 5, (1.00, 1.16,  0,   0,   0,   0, 0), "dusk"),
    (25, 140, 10, (1.06, 1.06, 90, -90,  0,   0, 0), "dusk"),
    # SCENE 6 - ANG UNANG TAWAG
    (26, 150, 5, (1.08, 1.08,  50, -50,  0,   0, 1), "night"),
    (27, 155, 5, (1.00, 1.10,  0,   0,   0,   0, 1), "night"),
    (28, 160, 5, (1.00, 1.12,  0,   0,   0,   0, 1), "night"),
    (29, 165, 10, (1.00, 1.18, 0,  30,   0,   0, 1), "night"),
    (30, 175, 2.5, (1.05, 1.16, 0,  0,   0,   0, 0), "night"),
]

SCENES = [
    (0,   "SCENE 1", "Ang Umaga sa Malinaw"),
    (30,  "SCENE 2", "Ang Magsasaka"),
    (60,  "SCENE 3", "Ang Pagbalik"),
    (90,  "SCENE 4", "Ang Babala"),
    (120, "SCENE 5", "Bago Dumilim"),
    (150, "SCENE 6", "Ang Unang Tawag"),
]

# (start, end, speaker, line, english, style)
LINES = [
    (21.0, 29.6, "NARRATOR", "Sa isang liblib na sitio sa kabundukan ng Lebak...",
     "In a remote village in the mountains of Lebak...", "vo"),
    (45.3, 49.6, "ALING ROSA", "Daniel! Kaon na anay! Basi maabtan ka sang init!",
     "Daniel! Come eat first! Before the heat gets to you!", ""),
    (49.8, 54.8, "DANIEL", "Sige, Nay! Tapuson ko lang ni. Kinahanglan madala ta ang kopra sa banwa buwas.",
     "Okay, Ma! Let me finish this. We have to bring the copra to town tomorrow.", ""),
    (55.3, 59.7, "NARRATOR", "Para kay Daniel, bawat ani ay may katumbas na pagod...",
     "For Daniel, every harvest is paid for in sweat...", "vo"),
    (75.3, 79.0, "MARA", "Parang walang nagbago rito. Pareho pa rin ang daan, pati ang mga bahay.",
     "Nothing seems to have changed. Same road, same houses.", ""),
    (79.2, 82.2, "DRIVER", "Madamo na ang nagbag-o, Ma'am. Labi na kon gab-i.",
     "A lot has changed, Ma'am. Especially at night.", ""),
    (82.4, 84.9, "MARA", "Bakit? Anong meron sa gabi?",
     "Why? What happens at night?", ""),
    (95.3, 99.8, "ALING ROSA", "Tatlong gabi nang may nawawalang alagang hayop.",
     "For three nights now, animals have gone missing.", ""),
    (100.3, 104.8, "LOLA ISING", "Hindi lahat ng nasa kagubatan ay dapat hanapin.",
     "Not everything in the forest should be looked for.", ""),
    (105.3, 109.8, "DANIEL", "Lola, baka ligaw na aso lang 'yan.",
     "Lola, it's probably just a stray dog.", ""),
    (110.6, 115.5, "LOLA ISING", "Sana nga, apo. Sana nga.",
     "I hope so, child. I hope so.", ""),
    (140.3, 143.5, "NARRATOR", "Sa Sitio Malinaw, may isang kaugaliang sinusunod ng matatanda.",
     "In Sitio Malinaw, the elders keep one old rule.", "vo"),
    (143.7, 146.7, "NARRATOR", "Kapag dumilim, walang batang pinapayagang lumapit sa kagubatan.",
     "After dark, no child may go near the forest.", "vo"),
    (146.9, 149.8, "NARRATOR", "At kapag may tumawag mula sa dilim, huwag na huwag kang sasagot.",
     "And if something calls to you from the dark, never answer.", "vo"),
    (157.0, 159.8, "JUNJUN", "Sino 'yan?", "Who's there?", ""),
    (160.8, 164.6, "TINIG", "Junjun...", "", "whisper"),
    (165.6, 169.6, "TINIG", "Junjun... tulungan mo ako.", "Junjun... help me.", "whisper"),
    (170.2, 172.8, "JUNJUN", "Sino ka?", "Who are you?", ""),
]

GRADES = {
    "day":   "saturate(1.06) contrast(1.05) sepia(0.06)",
    "warm":  "saturate(1.02) contrast(1.06) sepia(0.12)",
    "dusk":  "saturate(0.98) contrast(1.08) sepia(0.14) brightness(0.94)",
    "night": "saturate(0.82) contrast(1.08) brightness(0.97)",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    shots_html, subs_html, labels_html = [], [], []
    shot_js = []
    for n, start, dur, move, grade in SHOTS:
        sid = f"s{n:02d}"
        mp4 = f"assets/shots/shot{n:02d}.mp4"
        if os.path.exists(os.path.join(ROOT, mp4)):
            media = (f'<video class="media" src="{mp4}" data-start="{start}" data-duration="{dur}" muted playsinline '
                     f'style="filter:{GRADES[grade]}"></video>')
        else:
            media = (f'<img class="media" src="assets/shots/shot{n:02d}.jpg" alt="Shot {n}" '
                     f'style="filter:{GRADES[grade]}" />')
        shots_html.append(
            f'      <div id="{sid}" class="clip shot" data-start="{start}" data-duration="{dur}" '
            f'data-track-index="1"><div class="cam" id="{sid}c">{media}</div></div>')
        shot_js.append({"id": sid, "start": start, "dur": dur, "move": move})

    for i, (start, label, title) in enumerate(SCENES):
        labels_html.append(
            f'      <div id="lab{i}" class="clip label" data-start="{start + 0.6}" data-duration="4" '
            f'data-track-index="3"><span class="lab-num">{label}</span>'
            f'<span class="lab-title">{esc(title)}</span></div>')

    for i, (a, b, who, line, eng, style) in enumerate(LINES):
        eng_html = f'<div class="eng">{esc(eng)}</div>' if eng else ""
        subs_html.append(
            f'      <div id="sub{i}" class="clip sub {style}" data-start="{a}" data-duration="{round(b - a, 2)}" '
            f'data-track-index="4"><div class="who">{esc(who)}</div>'
            f'<div class="line">{esc(line)}</div>{eng_html}</div>')

    tpl = open(os.path.join(ROOT, "tools", "template.html"), encoding="utf-8").read()
    html = (tpl.replace("{{SHOTS}}", "\n".join(shots_html))
               .replace("{{LABELS}}", "\n".join(labels_html))
               .replace("{{SUBS}}", "\n".join(subs_html))
               .replace("{{SHOT_DATA}}", json.dumps(shot_js))
               .replace("{{SCENE_STARTS}}", json.dumps([s[0] for s in SCENES[1:]]))
               .replace("{{SUB_DATA}}", json.dumps([[l[0], l[1]] for l in LINES])))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)

    # Subtitle file for players / editors
    def ts(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    srt = []
    for i, (a, b, who, line, eng, _) in enumerate(LINES, 1):
        srt.append(f"{i}\n{ts(a)} --> {ts(b)}\n{who}: {line}\n" + (f"({eng})\n" if eng else ""))
    open(os.path.join(ROOT, "subtitles.srt"), "w", encoding="utf-8").write("\n".join(srt))
    print(f"index.html: {len(SHOTS)} shots, {len(LINES)} lines")


if __name__ == "__main__":
    build()
