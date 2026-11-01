from pathlib import Path
p=Path("operations/generate-b21-nov-editorial-v3.py")
s=p.read_text(encoding="utf-8")
old="def fnt(f,s):return ImageFont.truetype(FONTS[f],round(s))"
new="""def fnt(f,s):
    from pathlib import Path
    options=[
        FONTS[f],
        '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    for candidate in options:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate,round(s))
    return ImageFont.load_default(size=round(s))"""
assert old in s
s=s.replace(old,new)
s=s.replace("JOE WALLES · 1985","BILL LANPHIER · CC BY 3.0 · 1985")
s=s.replace("LONDON, NOT MANCHESTER.","LONDON / 1975")
p.write_text(s,encoding="utf-8")
print("Font fallback and editorial credits patched for CI")
