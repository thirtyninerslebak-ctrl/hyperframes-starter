"""Cut the 30 shot panels out of the storyboard and upscale them for a 1920x1080 frame.
Usage: python3 tools/prep_shots.py assets/storyboard.webp assets/shots"""
import sys, os
from PIL import Image, ImageFilter, ImageEnhance
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
# x-range of each storyboard column, and y-range of the 5 photos in it
cols = [(7,260),(270,515),(524,769),(779,1018),(1027,1278),(1288,1530)]
rows = [
 [(176,300),(358,478),(536,640),(688,795),(838,935)],
 [(176,311),(360,478),(527,628),(678,766),(877,944)],
 [(176,311),(362,478),(527,632),(680,766),(885,955)],
 [(176,310),(362,470),(532,637),(700,788),(845,952)],
 [(176,305),(357,474),(522,631),(680,781),(825,880)],
 [(176,310),(357,478),(537,617),(682,784),(873,952)],
]
os.makedirs(out, exist_ok=True)
TW = 2400  # target width: room for slow camera moves inside a 1920px frame
for c,(x0,x1) in enumerate(cols):
    for r,(y0,y1) in enumerate(rows[c]):
        n = c*5 + r + 1
        p = im.crop((x0+2, y0+2, x1-2, y1-2))
        p = p.filter(ImageFilter.SMOOTH_MORE)               # soften compression blocks
        h = round(p.height * TW / p.width)
        p = p.resize((TW, h), Image.LANCZOS)
        p = p.filter(ImageFilter.UnsharpMask(radius=4, percent=60, threshold=2))
        p.save(f'{out}/shot{n:02d}.jpg', quality=92)
        print(n, p.size)
