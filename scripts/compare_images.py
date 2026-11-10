from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import json

folder=Path(__file__).resolve().parents[1]/'reports'
results=[]
for device,width,height in [('desktop',1440,900),('mobile',390,844)]:
    original=folder/f'{device}-original.png'
    static=folder/f'{device}-static.png'
    if not original.exists() or not static.exists():
        results.append({'device':device,'error':'One or both screenshots are missing'})
        continue
    a=Image.open(original).convert('RGB').crop((0,0,width,height))
    b=Image.open(static).convert('RGB').crop((0,0,width,height))
    diff=ImageChops.difference(a,b)
    mean=sum(ImageStat.Stat(diff).mean)/3/255
    composite=Image.new('RGB',(width*2,height))
    composite.paste(a,(0,0))
    composite.paste(b,(width,0))
    composite.save(folder/f'{device}-side-by-side.jpg',quality=85)
    diff.save(folder/f'{device}-diff.png')
    results.append({'device':device,'first_viewport_mean_absolute_pixel_difference':round(mean,4),'pixel_identical':mean==0})
(folder/'visual-diff.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
