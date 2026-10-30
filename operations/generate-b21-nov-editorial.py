from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os, random, math, textwrap, json, zipfile
import numpy as np
OUT='assets/social/editorial-2026/b21-nov-2026'
os.makedirs(OUT,exist_ok=True)
W,H=1080,1350
PAPER=(240,234,216); DARK=(19,19,19); RED=(229,45,34); ACID=(229,240,30); WHITE=(249,246,236); HOT=(255,46,135); CYAN=(76,225,249); GOLD=(207,174,119)
FONT_HEAD='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FONT_IMPACT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FONT_TIGHT='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FONT_MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
FONT_REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
M='madonna'
D='duran'
rand=random.Random(990123)

def font(f,size):return ImageFont.truetype(f,size)
def tx(draw,xy,text,size,color=WHITE,f=FONT_HEAD,spacing=0,stroke=0,stroke_fill=None,anchor=None):
    draw.text(xy,text,font=font(f,size),fill=color,spacing=spacing,stroke_width=stroke,stroke_fill=stroke_fill,anchor=anchor)

def fit(draw,text,maxwidth,maxsize,minsize=20,f=FONT_HEAD):
    for s in range(maxsize,minsize-1,-1):
        if draw.textbbox((0,0),text,font=font(f,s))[2]<=maxwidth:return s
    return minsize

def base(bg=DARK,seed=1,h=H,noise=True):
    im=Image.new('RGB',(W,h),bg)
    d=ImageDraw.Draw(im)
    rr=random.Random(seed)
    if noise:
        arr=np.asarray(im).astype(np.int16).copy()
        rng=np.random.default_rng(seed)
        grain=rng.normal(0,8, (h,W,1))
        arr=np.uint8(np.clip(arr+grain,0,255))
        im=Image.fromarray(arr)
        d=ImageDraw.Draw(im)
        for i in range(int(h/6)):
            x=rr.randrange(W);y=rr.randrange(h)
            c=(200,190,174) if bg==DARK else (62,55,49)
            d.line((x,y,x+rr.randrange(3,70),y+rr.randrange(-3,4)),fill=c,width=1)
    return im

def tear(draw,coords,fill=RED,seed=1):
    x0,y0,x1,y1=coords
    rr=random.Random(seed);pts=[]
    for x in range(x0,x1+1,22):pts.append((x,y0+rr.randint(-7,7)))
    for y in range(y0,y1+1,19):pts.append((x1+rr.randint(-7,7),y))
    for x in range(x1,x0-1,-22):pts.append((x,y1+rr.randint(-7,7)))
    for y in range(y1,y0-1,-19):pts.append((x0+rr.randint(-7,7),y))
    draw.polygon(pts,fill=fill)

def brand(im,slug,idx,count,light=False):
    d=ImageDraw.Draw(im);h=im.height
    col=DARK if light else PAPER
    d.rectangle((47,37,1033,40),fill=RED)
    tx(d,(54,52),'BANNED',29,col,FONT_TIGHT);tx(d,(200,48),'21',35,RED,FONT_HEAD);tx(d,(248,52),'RECORDS',29,col,FONT_TIGHT)
    tx(d,(786,54),f'{idx:02d} / {count:02d}',28,col,FONT_MONO)
    d.rectangle((47,h-75,1033,h-72),fill=RED)
    tx(d,(55,h-61),'BILBAO  ·  EST. 2026',19,col,FONT_MONO)
    tx(d,(722,h-61),'BAD IDEAS. LOUD MUSIC.',18,col,FONT_MONO)

def photo_art(path,seed=1):
    im=base(DARK,seed)
    d=ImageDraw.Draw(im)
    color=RED if path=='madonna' else HOT
    alt=ACID if path=='madonna' else CYAN
    # Original B21-inspired ripped-paper graphic, drawn in full frame: no third-party photography.
    d.polygon([(535,80),(1180,0),(1180,1300),(700,1330),(600,1000),(740,735)],fill=color)
    d.polygon([(680,0),(1160,0),(1050,330),(650,460)],fill=alt)
    d.polygon([(760,430),(1200,235),(1210,890),(800,1170)],fill=(30,28,34))
    for a in range(12):
        x=610+a*57
        d.line((x,280,x-210,1270),fill=alt if a%3==0 else PAPER,width=4 if a%3 else 15)
    for center,radius in [((870,550),200),((910,900),122)]:
        cx,cy=center
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=alt,width=19)
        d.ellipse((cx-65,cy-65,cx+65,cy+65),fill=color)
    return im

def cover_img(path,title,main,date,sub,tag,idx,kind='red',overlay=True):
    im=photo_art(path)
    d=ImageDraw.Draw(im,'RGBA')
    # original art left side kept dark, transparent ink overlay
    for x in range(0,730,6):
        alpha=int(140*(1-x/730)**1.3)
        d.rectangle((x,0,x+6,H),fill=(12,11,13,alpha))
    d=ImageDraw.Draw(im)
    accent={'red':RED,'pink':HOT,'gold':GOLD}.get(kind,RED)
    tear(d,(54,194,578,283),accent,seed=idx+9)
    tx(d,(73,199),date,40,DARK,FONT_MONO)
    y=340
    for line in main:
        size=fit(d,line,950,121,54)
        tx(d,(60,y),line,size,PAPER,stroke=1,stroke_fill=DARK)
        y+=int(size*1.08)
    y=max(y+40,880)
    if tag:
        d.rounded_rectangle((65,y-13,420,y+50),8,fill=ACID)
        tx(d,(85,y-4),tag,38,DARK,FONT_TIGHT)
        y+=105
    for line in sub:
        size=fit(d,line,950,50,24,f=FONT_MONO)
        tx(d,(70,y),line,size,PAPER,FONT_MONO)
        y+=60
    brand(im,title,idx,5)
    return im

def text_slide(title,lines,sub,idx,kind='red',light=False,chip='',motif='star',seed=1):
    accent={'red':RED,'pink':HOT,'gold':GOLD}.get(kind,RED)
    im=base(PAPER if light else DARK,seed)
    d=ImageDraw.Draw(im)
    fg=DARK if light else PAPER
    # abstract unpretentious editorial grunge, strong geometric system
    if motif=='bars':
        for k in range(5):
            xx=820+k*61-130
            d.rectangle((xx,220,xx+33,1080-k*45),fill=accent if k%2==0 else (125,91,103))
    elif motif=='disc':
        d.ellipse((655,345,1260,950),fill=accent,outline=fg,width=15)
        for r in [280,230,180,120,65]:d.ellipse((960-r,650-r,960+r,650+r),outline=DARK if not light else PAPER,width=4)
    elif motif=='tape':
        d.rectangle((664,526,1160,898),outline=fg,width=16)
        d.ellipse((735,594,895,754),outline=accent,width=16)
        d.ellipse((940,594,1099,754),outline=accent,width=16)
    elif motif=='lightning':
        d.polygon([(850,350),(709,714),(814,709),(733,1140),(1056,599),(930,602),(1050,340)],fill=accent)
    elif motif=='star':
        for x,y,r in [(903,610,185),(800,865,130)]:
            pts=[]
            for j in range(10):
                a=j*math.pi/5-math.pi/2
                rr=r if j%2==0 else r*.4
                pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
            d.polygon(pts,fill=accent)
    elif motif=='mic':
        # monochrome, abstract stage microphone and stand, no likeness
        d.line((870,700,910,1110),fill=GOLD,width=27)
        d.line((910,1110,780,1195),fill=GOLD,width=16)
        d.line((910,1110,1050,1195),fill=GOLD,width=16)
        d.ellipse((705,398,1025,728),fill=GOLD)
        for yy in range(465,690,27):d.line((741,yy,986,yy),fill=DARK,width=8)
        d.rectangle((815,690,905,745),fill=GOLD)
    elif motif=='crown':
        d.polygon([(660,690),(700,380),(812,570),(910,335),(1024,570),(1080,375),(1100,740)],fill=GOLD)
        d.rectangle((655,735,1080,810),fill=GOLD)
    tear(d,(61,235,700,320),accent,seed)
    tx(d,(78,245),title,36,DARK,FONT_MONO)
    y=385
    for line in lines:
        sz=fit(d,line,935,110,45)
        tx(d,(62,y),line,sz,fg,FONT_HEAD,stroke=0)
        y+=min(130,sz*1.18)
    y=max(y+18,850)
    if chip:
        cw=min(884,max(390,d.textbbox((0,0),chip,font=font(FONT_MONO,26))[2]+50))
        d.rectangle((64,y,64+cw,y+60),fill=ACID if kind!='gold' else GOLD)
        tx(d,(82,y+13),chip,26,DARK,FONT_MONO)
        y+=105
    for line in sub:
        sz=fit(d,line,910,36,20,f=FONT_MONO)
        tx(d,(71,y),line,sz,fg,FONT_MONO)
        y+=56
    brand(im,title,idx,5,light=light)
    return im

def freddie_style(im,idx,quote=False):
    d=ImageDraw.Draw(im)
    if idx==1:
        d.polygon([(700,350),(742,660),(830,410),(876,690),(976,470),(1047,700),(1047,760),(690,760)],fill=GOLD)
    return im

items={}
# Madonna 12 nov
slides=[]
slides.append(cover_img(M,'MADONNA',['LIKE A','VIRGIN.'],'12 NOV 1984', ['42 YEARS.','SAME CULTURAL AFTERSHOCK.'],'POP HISTORY',1,'red'))
slides.append(text_slide('THE SECOND ALBUM',['1984.','SECOND','ALBUM.'],['12 NOVEMBER 1984.','THE RECORD THAT CHANGED THE SCALE.'],2,'red',False,'42 YEARS ON','disc',42))
slides.append(cover_img(M,'MADONNA',['ONE','PRODUCER.'],'NILE RODGERS', ['CHIC LEGEND.','DISCO INTELLIGENCE.'],'BIG SOUND',3,'pink'))
slides.append(text_slide('THE SINGLES',['MATERIAL','GIRL.','ANGEL.'],['LIKE A VIRGIN.','DRESS YOU UP.'],4,'red',True,'4 US TOP 5 SINGLES','lightning',31))
slides.append(text_slide('B21 / POP HISTORY',['SHE','DIDN\'T','ASK.'],['THE EIGHTIES GOT A NEW RULEBOOK.','WHICH MADONNA TRACK STILL HITS?'],5,'red',False,'42 YEARS OF LIKE A VIRGIN','star',55))
items['madonna']=slides
# Duran Duran
slides=[]
slides.append(cover_img(D,'DURAN DURAN',['SEVEN AND','THE RAGGED','TIGER.'],'21 NOV 1983',['43 YEARS OF SYNTHS.','43 YEARS OF STYLE.'],'DURAN DURAN',1,'pink'))
slides.append(text_slide('21 NOVEMBER 1983',['THE THIRD','STUDIO','ALBUM.'],['DURAN DURAN.','THE WORLD TOUR WAS ALREADY CALLING.'],2,'pink',False,'43 YEARS','disc',80))
slides.append(text_slide('THE TRACKLIST',['THE','REFLEX.'],['UNION OF THE SNAKE.','NEW MOON ON MONDAY.'],3,'pink',True,'SINGLES OF AN ERA','lightning',81))
slides.append(cover_img(D,'DURAN DURAN',['SUITS.','SYNTHS.','DRAMA.'],'1983 - 2026',['WHEN THE LOOK WAS','AS LOUD AS THE MUSIC.'],'NEW ROMANTIC',4,'pink'))
slides.append(text_slide('B21 / MUSIC HISTORY',['ONE','VERY','LOUD','DECADE.'],['WHICH DURAN DURAN SONG','WOULD YOU PLAY FIRST?'],5,'pink',False,'43 YEARS ON','tape',82))
items['duran']=slides
# Freddie - elegant tribute, 5 panels
slides=[]
slides.append(text_slide('24 NOVEMBER 1991',['FREDDIE','MERCURY.'],['1946  -  1991.','35 YEARS. AN ENDURING VOICE.'],1,'gold',False,'REMEMBERING FREDDIE','mic',150))
slides.append(text_slide('AN EXTRAORDINARY VOICE',['NOT JUST','A FRONTMAN.'],['SONGWRITER. PERFORMER.','THE CREATIVE FORCE OF QUEEN.'],2,'gold',True,'A LEGACY BEYOND THE STAGE','crown',151))
slides.append(text_slide('WEMBLEY / 1985',['LIVE','AID.'],['ONE STAGE.','A PERFORMANCE FOR THE AGES.'],3,'gold',False,'13 JULY 1985','mic',152))
slides.append(text_slide('BEYOND QUEEN',['BARCELONA.'],['WITH MONTSERRAT CABALLE.','TWO WORLDS IN ONE VOICE.'],4,'gold',True,'1988','star',153))
slides.append(text_slide('FREDDIE MERCURY',['THE MUSIC','STAYS.'],['24 NOVEMBER 1991  -  2026.','THANK YOU, FREDDIE.'],5,'gold',False,'IN REMEMBRANCE','crown',154))
items['freddie']=slides

for key,sl in items.items():
    for i,im in enumerate(sl,1):
        path=f'{OUT}/{key.upper()}_{i:02d}.jpg'
        im.save(path,'JPEG',quality=91,optimize=True,subsampling=0)

# Vertical Stories: font strategies + 3 languages visible
for typ in ['sexpistols','humanleague']:
    im=base(DARK,202 if typ=='sexpistols' else 301,h=1920)
    d=ImageDraw.Draw(im)
    accent=RED if typ=='sexpistols' else HOT
    if typ=='sexpistols':
        tear(d,(40,275,1045,650),RED,919)
        tx(d,(70,297),'SEX',190,PAPER)
        tx(d,(70,469),'PISTOLS',181,PAPER)
        tx(d,(70,694),'FIRST EVER GIG.',93,PAPER)
        tx(d,(75,831),'06 NOV 1975',81,ACID,FONT_MONO)
        tx(d,(75,1015),'51 YEARS OF NOISE.',60,ACID)
        d.rectangle((63,1140,1000,1395),fill=PAPER)
        tx(d,(87,1170),'FIRST CONCERT.',55,DARK)
        tx(d,(87,1254),'PRIMER CONCIERTO.',50,DARK)
        tx(d,(87,1325),'LEHEN KONTZERTUA.',43,DARK)
        tx(d,(78,1522),"ST MARTIN'S SCHOOL OF ART",37,PAPER,FONT_TIGHT)
        tx(d,(78,1578),'LONDON · 1975',44,PAPER,FONT_MONO)
        tx(d,(78,1660),'BANNED 21 / PUNK HISTORY',27,ACID,FONT_MONO)
    else:
        # synthwave diagonal gradient bars + waveform
        for k in range(18):
            d.rectangle((780+k*11,260+k*22,802+k*11,1300+k*10),fill=(max(0,255-k*10),42,125+k*3))
        tear(d,(49,280,1000,590),HOT,502)
        tx(d,(69,307),"DON'T YOU",130,DARK)
        tx(d,(69,444),'WANT ME?',132,DARK)
        tx(d,(73,688),'THE HUMAN LEAGUE',66,PAPER)
        tx(d,(74,809),'27 NOV 1981',73,CYAN,FONT_MONO)
        tx(d,(72,950),'45 YEARS.',112,PAPER)
        d.rectangle((62,1160,1010,1450),fill=PAPER)
        tx(d,(83,1184),'THE UNLIKELY HIT.',46,DARK)
        tx(d,(83,1262),'EL ÉXITO IMPROBABLE.',42,DARK)
        tx(d,(83,1334),'USTEKABEKO ARRAKASTA.',36,DARK)
        tx(d,(80,1542),'5 WEEKS AT UK #1.',47,CYAN,FONT_HEAD)
        tx(d,(80,1647),'CHRISTMAS #1 · 1981',39,PAPER,FONT_MONO)
    d.rectangle((55,1795,1025,1801),fill=RED)
    tx(d,(60,1822),'BANNED',58,PAPER,FONT_TIGHT)
    tx(d,(300,1822),'21',61,RED,FONT_HEAD)
    tx(d,(404,1822),'RECORDS',58,PAPER,FONT_TIGHT)
    im.save(f'{OUT}/{typ.upper()}_STORY.jpg','JPEG',quality=91,optimize=True,subsampling=0)

# contact sheet for QA
paths=[f'{OUT}/{key.upper()}_{i:02d}.jpg' for key in items for i in range(1,6)]+[f'{OUT}/{k.upper()}_STORY.jpg' for k in ['sexpistols','humanleague']]
thumbs=[]
for p in paths:
    im=Image.open(p).convert('RGB')
    im.thumbnail((230,300))
    c=Image.new('RGB',(250,315),(62,62,62));c.paste(im,((250-im.width)//2,(315-im.height)//2));thumbs.append(c)
cols=5;rows=math.ceil(len(thumbs)/cols)
contact=Image.new('RGB',(cols*250,rows*315),(25,25,25))
for n,img in enumerate(thumbs):contact.paste(img,((n%cols)*250,(n//cols)*315))
contact.save(f'{OUT}/CONTACT_QA.jpg',quality=90)
with zipfile.ZipFile(f'{OUT}/B21_5_EFEMERIDES_NOV_2026.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in paths:z.write(p,os.path.basename(p))
print('DONE',len(paths),sum(os.path.getsize(p) for p in paths),'bytes')