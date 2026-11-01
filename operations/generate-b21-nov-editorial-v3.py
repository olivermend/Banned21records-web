#!/usr/bin/env python3
"""BANNED 21 RECORDS November 2026: separate photographic editorial carousels and stories.
Uses independently licensed reference photos for archival artist imagery. No Canva uploads.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np, random, math, os, io, json
from pathlib import Path

ROOT=Path(os.environ.get('B21_OUTPUT','/mnt/data/B21_EDITORIAL_V3_FINAL'))
ROOT.mkdir(parents=True,exist_ok=True)
SRCD=Path(os.environ.get('B21_CACHE_DIR','/mnt/data/b21_editorial_preview_sources'))
FONTS={
 'display':'/usr/share/fonts/truetype/noto/NotoSansDisplay-ExtraCondensedBlack.ttf',
 'block':'/usr/share/fonts/truetype/noto/NotoSansDisplay-CondensedBlack.ttf',
 'sans':'/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
 'mono':'/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
 'serif':'/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
}
W=1080; H=1350
COL={'black':'#101012','paper':'#efe9d7','paper2':'#d7c8ac','pink':'#ef1a82','red':'#ea281c','yellow':'#eff000','cyan':'#27d8f0','orange':'#f06812','gold':'#ebc26b','blue':'#141736','green':'#41d596','white':'#fcf6e9'}
THEMES={
 'MADONNA':{'primary':'pink','secondary':'yellow','photo':'madonna','accent':'#ff0084','year':1984,'name':'MADONNA'},
 'DURAN':{'primary':'orange','secondary':'cyan','photo':'duran','accent':'#ff6d10','year':1983,'name':'DURAN DURAN'},
 'FREDDIE':{'primary':'gold','secondary':'red','photo':'freddie','accent':'#ebc26b','year':1991,'name':'FREDDIE MERCURY'},
 'SEXPISTOLS':{'primary':'pink','secondary':'yellow','photo':'sex','accent':'#ef1a82','year':1975,'name':'SEX PISTOLS'},
 'HUMANLEAGUE':{'primary':'pink','secondary':'cyan','photo':'human','accent':'#ef1a82','year':1981,'name':'THE HUMAN LEAGUE'},
}
CREDIT={
 'sex':'PHOTO: KOEN SUYK · CC0 · 1977',
 'madonna':'PHOTO: JOE WALLES · 1985',
 'duran':'PHOTO: SAMIRA KHAN · CC BY 2.0 · 2005',
 'freddie':'PHOTO: CARL LENDER · CC BY 2.0 · 1977',
 'human':'PHOTO: J. PARDOEN · CC BY 2.0 · 2014',
}
PHOTOS={}
for k in ['sex','madonna','duran','freddie','human']:
 p=SRCD/(k+'.jpg')
 if not p.exists(): raise RuntimeError('Missing source '+str(p))
 PHOTOS[k]=Image.open(p).convert('RGB')


def rgb(c):return tuple(bytes.fromhex(COL.get(c,c).removeprefix('#')))
def fnt(f,s):return ImageFont.truetype(FONTS[f],round(s))
def fit_font(text,width,nominal=80,minimum=26,f='block'):
 for x in range(nominal,minimum-1,-1):
  b=ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),text,font=fnt(f,x))
  if b[2]-b[0]<=width:return x
 return minimum

def TXT(im,text,x,y,size=64,color='paper',font='block',maxw=None,anchor=None,stroke=0,stroke_color='black',rotate=0, shadow=False):
 if maxw:size=fit_font(text,maxw,size,18,font)
 if not rotate:
  d=ImageDraw.Draw(im)
  if shadow:d.text((x+4,y+6),text,font=fnt(font,size),fill=rgb('black'),stroke_width=stroke,stroke_fill=rgb('black'),anchor=anchor)
  d.text((x,y),text,font=fnt(font,size),fill=rgb(color),stroke_width=stroke,stroke_fill=rgb(stroke_color),anchor=anchor)
 else:
  bbox=ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),text,font=fnt(font,size),stroke_width=stroke)
  tw=bbox[2]-bbox[0]+30;th=bbox[3]-bbox[1]+40
  img=Image.new('RGBA',(tw,th),(0,0,0,0)); d=ImageDraw.Draw(img)
  d.text((12-bbox[0],12-bbox[1]),text,font=fnt(font,size),fill=rgb(color),stroke_width=stroke,stroke_fill=rgb(stroke_color))
  img=img.rotate(rotate,Image.Resampling.BICUBIC,expand=True)
  im.paste(img,(int(x),int(y)),img)
 return size

def noise_texture(w,h,seed=1):
 rng=np.random.default_rng(seed)
 grain=rng.normal(0,14,(h,w,1)).astype(np.int16)
 a=np.clip(grain+128,0,255).astype('uint8')
 return Image.fromarray(np.repeat(a,3,axis=2),'RGB')

def make_base(name,h=H,seed=5):
 t=THEMES[name];bg=Image.new('RGB',(W,h),rgb('black'))
 rng=np.random.default_rng(seed)
 ar=np.asarray(bg).astype('int16'); g=rng.normal(0,6,(h,W,1));ar=np.clip(ar+g,0,255).astype('uint8'); im=Image.fromarray(ar)
 d=ImageDraw.Draw(im);rr=random.Random(seed)
 for n in range(450):
  x=rr.randint(0,W);y=rr.randint(0,h)
  if n%13==0:d.line((x,y,x+rr.randint(40,210),y+rr.randint(-2,2)),fill='#595950',width=1)
  elif n%3==0:d.point((x,y),fill='#76746e')
 # Some lively but structured ink splashes on edges
 for i in range(20):
  x=rr.choice([rr.randint(-80,120),rr.randint(W-120,W+80)])
  y=rr.randint(150,h-120); rad=rr.randint(2,15)
  d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=rgb(t['primary']))
 return im

def rip_mask(size,seed=1,jag=10):
 w,h=size;rr=random.Random(seed)
 p=[]
 for x in range(0,w+1,18):p.append((x,rr.randint(1,jag)))
 for y in range(0,h+1,18):p.append((w-rr.randint(1,jag),y))
 for x in range(w,-1,-18):p.append((x,h-rr.randint(1,jag)))
 for y in range(h,-1,-18):p.append((rr.randint(1,jag),y))
 mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).polygon(p,fill=255);return mask

def paper(im,box,color='paper',seed=1,jag=10,angle=0,shadow=True):
 x,y,w,h=map(int,box)
 if w<3 or h<3:return
 p=Image.new('RGBA',(w,h),rgb(color)+(255,)); m=rip_mask((w,h),seed,jag)
 tex=noise_texture(w,h,seed+91)
 # subtle worn paper surface
 p=Image.blend(p.convert('RGB'),tex,.08).convert('RGBA');p.putalpha(m)
 if angle:p=p.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if shadow:
  sh=Image.new('RGBA',p.size,(0,0,0,0));sh.putalpha(p.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v:int(v*.5)))
  im.paste(sh,(x+9,y+12),sh)
 im.paste(p,(x,y),p)

def crop_cover(im,w,h,focus=(.50,.44)):
 sw,sh=im.size
 sc=max(w/sw,h/sh);ow=int(sw*sc);oh=int(sh*sc)
 res=im.resize((ow,oh),Image.Resampling.LANCZOS)
 left=int((ow-w)*focus[0]);top=int((oh-h)*focus[1]);left=max(0,min(left,ow-w));top=max(0,min(top,oh-h))
 return res.crop((left,top,left+w,top+h))

def photo_frame(im,source,box,seed=1,contrast=1.1,colorize=None,focus=(.5,.5),tint=None):
 x,y,w,h=map(int,box);r=crop_cover(source,w,h,focus)
 if contrast:r=ImageEnhance.Contrast(r).enhance(contrast)
 if colorize:
  g=ImageOps.grayscale(r);r=ImageOps.colorize(g,black=rgb('black'),white=rgb(colorize))
 if tint:
  ov=Image.new('RGB',r.size,rgb(tint));r=Image.blend(r,ov,.10)
 mask=rip_mask((w,h),seed,jag=14)
 # subtle printable roughness
 rr=np.random.default_rng(seed);arr=np.asarray(r).astype('int16');arr=np.clip(arr+rr.normal(0,5,(h,w,1)),0,255).astype('uint8');r=Image.fromarray(arr)
 shadow=Image.new('RGBA',(w,h),(0,0,0,100));shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(15)).point(lambda v:int(v*.55)))
 im.paste(shadow,(x+12,y+14),shadow)
 im.paste(r,(x,y),mask)
 return (x,y,w,h)

def tape(im,x,y,w=145,h=34,color='paper2',angle=16,alpha=160):
 p=Image.new('RGBA',(w,h),rgb(color)+(alpha,));p=p.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 im.paste(p,(x,y),p)

def speckles(im,seed=1,count=100,color='paper'):
 rr=random.Random(seed);d=ImageDraw.Draw(im)
 for i in range(count):
  x=rr.randrange(0,W);y=rr.randrange(0,im.height);r=rr.randrange(1,4)
  d.ellipse((x,y,x+r,y+r),fill=rgb(color))

def paint_stripe(im,x1,y1,x2,y2,color='pink',width=14):
 d=ImageDraw.Draw(im);d.line((x1,y1,x2,y2),fill=rgb(color),width=width)
 for k in range(12):
  t=k/12; xx=x1*(1-t)+x2*t; yy=y1*(1-t)+y2*t
  d.line((xx-6,yy-5,xx+5,yy+5),fill=rgb(color),width=2)

def icon_star(im,x,y,r=45,color='yellow',outline=False):
 d=ImageDraw.Draw(im);points=[]
 for k in range(12):
  an=-math.pi/2+k*math.pi/6;rr=r if k%2==0 else r*.48
  points.append((int(x+rr*math.cos(an)),int(y+rr*math.sin(an))))
 if outline:d.line(points+[points[0]],fill=rgb(color),width=8)
 else:d.polygon(points,fill=rgb(color))

def crown(im,x,y,color='gold',scale=1):
 d=ImageDraw.Draw(im);p=[(0,90),(7,0),(66,52),(114,-12),(162,52),(230,0),(235,90)]
 xy=[(int(x+a*scale),int(y+b*scale)) for a,b in p];d.line(xy,fill=rgb(color),width=max(5,int(11*scale)),joint='curve')
 d.line((xy[0][0],xy[-1][1],xy[-1][0],xy[-1][1]),fill=rgb(color),width=max(6,int(12*scale)))

def brand(im,theme,idx,count=5,credit=True):
 d=ImageDraw.Draw(im);h=im.height
 d.rectangle((25,25,W-25,30),fill=rgb(THEMES[theme]['primary']))
 paper(im,(30,40,252,54),'paper',seed=50+idx,jag=5,shadow=False)
 TXT(im,'BANNED 21',43,46,31,'black','sans')
 TXT(im,'RECORDS',221,48,20,'black','sans')
 TXT(im,f'{idx:02d} / {count:02d}',845,50,24,'paper','mono')
 d.rectangle((30,h-72,W-30,h-67),fill=rgb(THEMES[theme]['primary']))
 TXT(im,'BANNED 21 RECORDS  //  MUSIC. MISCHIEF. ALWAYS 21.',39,h-62,18,'paper','mono',maxw=940)
 if credit:
  source=THEMES[theme]['photo']
  TXT(im,CREDIT[source],40,h-105,15,'paper2','mono',maxw=930)

def badge(im,text,box,color='yellow',fg='black',seed=1,angle=0,size=48,font='block'):
 x,y,w,h=map(int,box);paper(im,(x,y,w,h),color,seed=seed,jag=8,angle=angle)
 if angle: # keep title horizontal for readability
  y+=5
 sz=fit_font(text,w-30,size,18,font);TXT(im,text,x+14,y+max(0,(h-sz)//3),sz,fg,font)

def wordstack(im,lines,x,y,maxw,fontsize,ink='paper',font='display',lineheight=1.00):
 for line in lines:
  s=TXT(im,line,x,y,fontsize,ink,font,maxw=maxw)
  y+=int(s*lineheight)
 return y

# Base posters are intentionally different per musician, not a generic template.
def madonna_art(idx):
 im=make_base('MADONNA',seed=101+idx);d=ImageDraw.Draw(im)
 # Flash of pink wallpaper behind the portrait
 d.polygon([(610,35),(1080,15),(1080,1320),(720,1295),(578,930)],fill=rgb('pink'))
 d.polygon([(832,0),(980,0),(756,1250),(668,1330)],fill=rgb('red'))
 if idx==1:
  photo_frame(im,PHOTOS['madonna'],(382,115,648,945),seed=19,contrast=1.1,focus=(.47,.35),colorize='paper')
  paint_stripe(im,70,338,475,265,'pink',15)
  TXT(im,'MADONNA',50,176,140,'pink','display',rotate=90)
  badge(im,'LIKE A VIRGIN',(58,644,500,120),'paper','black',7,size=79)
  badge(im,'12 NOV 1984',(60,796,482,94),'pink','black',15,size=64)
  badge(im,'42 YEARS. STILL ICONIC.',(69,937,810,87),'yellow','black',19,size=55)
  TXT(im,'POP DIDN\'T ASK PERMISSION.',70,1103,45,'paper','block',maxw=920)
  icon_star(im,920,1045,72,'yellow',outline=True)
 elif idx==2:
  photo_frame(im,PHOTOS['madonna'],(115,112,862,690),seed=31,focus=(.52,.44),colorize='paper')
  badge(im,'THE SECOND ALBUM',(57,53,690,93),'pink','black',22,size=60)
  paper(im,(45,718,1008,430),'paper',seed=39)
  wordstack(im,['12 NOVEMBER','1984.'],85,769,905,115,'black','display')
  paint_stripe(im,560,924,950,980,'red',15)
  TXT(im,'THE YEAR POP CHANGED THE RULES.',85,1050,43,'black','block',maxw=900)
 elif idx==3:
  d.rectangle((35,118,1020,1172),outline=rgb('pink'),width=11)
  photo_frame(im,PHOTOS['madonna'],(390,220,650,730),seed=41,focus=(.47,.28),tint='pink')
  badge(im,'NILE RODGERS',(53,156,635,119),'yellow','black',33,size=86)
  wordstack(im,['THE','PRODUCER.'],55,450,580,115,'paper','display',1.0)
  badge(im,'CHIC LEGEND.',(69,951,570,86),'paper','black',34,size=59)
  TXT(im,'DISCO KNOW-HOW. POP FIREPOWER.',68,1085,38,'paper','mono',maxw=880)
  icon_star(im,970,1000,70,'yellow')
 elif idx==4:
  # four separate white rip strips, as actual physical paper collage
  badge(im,'FOUR US TOP 5 SINGLES',(55,95,940,120),'yellow','black',45,size=80)
  for j,(title,col) in enumerate([('LIKE A VIRGIN','paper'),('MATERIAL GIRL','pink'),('ANGEL','paper'),('DRESS YOU UP','pink')]):
   badge(im,title,(60+18*(j%2),255+j*180,915-48*(j%2),128),col,'black',51+j,size=84)
  photo_frame(im,PHOTOS['madonna'],(655,947,376,232),seed=54,focus=(.5,.4))
  TXT(im,'1984 / 1985',63,1083,61,'paper','display')
 elif idx==5:
  photo_frame(im,PHOTOS['madonna'],(210,90,840,1002),seed=62,focus=(.5,.35),colorize='paper')
  paper(im,(50,448,910,545),'black',seed=64)
  wordstack(im,['SHE','DIDN\'T','ASK.'],87,510,810,148,'pink','display')
  badge(im,'WHICH MADONNA TRACK?',(69,1017,925,96),'yellow','black',66,size=72)
  TXT(im,'STILL YOUR 1984 OBSESSION?',75,1163,38,'paper','mono',maxw=900)
 brand(im,'MADONNA',idx)
 return im

def duran_art(idx):
 im=make_base('DURAN',seed=201+idx);d=ImageDraw.Draw(im)
 # Tiger-inspired abstract stripes + surreal 80s sunset motif
 for j in range(9):d.polygon([(540+j*83,50),(570+j*86,50),(296+j*75,1200),(267+j*77,1200)],fill=rgb('orange') if j%2 else rgb('pink'))
 if idx==1:
  photo_frame(im,PHOTOS['duran'],(62,440,962,710),seed=10,contrast=1.28,focus=(.48,.53))
  wordstack(im,['DURAN','DURAN'],62,97,910,134,'paper','serif',1.11)
  badge(im,'SEVEN AND THE',(60,385,785,88),'yellow','black',16,size=71)
  badge(im,'RAGGED TIGER',(176,478,828,92),'yellow','black',17,size=72)
  badge(im,'21 NOV 1983  ·  43 YEARS',(60,1085,922,78),'pink','black',18,size=55)
 elif idx==2:
  photo_frame(im,PHOTOS['duran'],(170,120,830,765),seed=20,contrast=1.12,focus=(.47,.54))
  badge(im,'THE THIRD',(62,837,650,106),'paper','black',22,size=93)
  badge(im,'STUDIO ALBUM',(64,951,911,103),'yellow','black',25,size=79)
  TXT(im,'NOVEMBER 1983 / UK NEW ROMANTIC',70,1120,37,'paper','mono',maxw=940)
 elif idx==3:
  paper(im,(39,93,1005,1100),'paper',seed=31)
  badge(im,'TRACKS THAT STUCK',(70,128,905,102),'pink','black',33,size=75)
  for i,line in enumerate(['THE REFLEX','UNION OF THE SNAKE','NEW MOON ON MONDAY']):
   yy=280+i*222
   TXT(im,f'0{i+1}',85,yy+17,86,'red','display')
   sz=fit_font(line,766,83,35,'block')
   TXT(im,line,201,yy+22,sz,'black','block')
   paint_stripe(im,194,yy+139,945,yy+130,'red',9)
  TXT(im,'BIG SYNTHS. BIGGER HAIR.',84,1045,46,'black','block')
 elif idx==4:
  photo_frame(im,PHOTOS['duran'],(42,254,990,734),seed=38,contrast=1.3,focus=(.5,.5))
  wordstack(im,['SUITS.','SYNTHS.'],64,83,885,112,'paper','display')
  badge(im,'ABSOLUTE EIGHTIES.',(64,955,917,115),'yellow','black',42,size=79)
  TXT(im,'THE SOUND WAS LOUD. THE LOOK WAS LOUDER.',70,1120,33,'paper','mono',maxw=940)
  icon_star(im,986,206,72,'pink')
 elif idx==5:
  photo_frame(im,PHOTOS['duran'],(45,100,992,907),seed=49,contrast=1.18,focus=(.46,.56),tint='pink')
  paper(im,(61,649,947,434),'black',seed=51)
  wordstack(im,['WHAT','PLAYS','FIRST?'],82,691,897,122,'paper','display')
  badge(im,'TELL US YOUR DURAN DURAN PICK.',(62,1094,926,96),'cyan','black',54,size=51)
 brand(im,'DURAN',idx)
 return im

def freddie_art(idx):
 im=make_base('FREDDIE',seed=301+idx);d=ImageDraw.Draw(im)
 # red crown slash and gold print, softer than punk pieces
 if idx==1:
  photo_frame(im,PHOTOS['freddie'],(250,102,804,1005),seed=66,contrast=1.12,focus=(.55,.36))
  paper(im,(60,80,801,332),'black',seed=76)
  wordstack(im,['FREDDIE','MERCURY'],80,117,875,122,'red','display',1.01)
  crown(im,816,252,'gold',.8)
  badge(im,'24 NOV 1991',(64,1020,716,95),'paper','black',67,size=68)
  badge(im,'35 YEARS. THE MUSIC STAYS.',(63,1126,950,77),'gold','black',72,size=49)
 elif idx==2:
  photo_frame(im,PHOTOS['freddie'],(375,105,660,985),seed=81,contrast=1.2,focus=(.48,.45))
  wordstack(im,['THE','VOICE.'],70,140,760,136,'paper','display',.96)
  paint_stripe(im,92,474,610,421,'red',17)
  badge(im,'A FORCE ON STAGE',(55,903,860,96),'gold','black',82,size=79)
  TXT(im,'SINGER. SONGWRITER. PERFORMER.',71,1100,42,'paper','mono',maxw=930)
 elif idx==3:
  photo_frame(im,PHOTOS['freddie'],(55,93,977,840),seed=91,contrast=1.25,focus=(.48,.48))
  paper(im,(45,679,992,414),'black',seed=92)
  wordstack(im,['LIVE AID.','1985.'],77,749,875,125,'paper','display')
  badge(im,'AN UNFORGETTABLE PERFORMANCE',(52,1083,971,96),'gold','black',93,size=49)
 elif idx==4:
  # Presentation without false archival photo of Barcelona duet
  d.polygon([(300,160),(900,60),(1060,1240),(50,1120)],fill=rgb('red'))
  photo_frame(im,PHOTOS['freddie'],(435,168,600,748),seed=101,contrast=1.08,focus=(.5,.44),colorize='gold')
  badge(im,'BARCELONA',(46,132,833,114),'gold','black',102,size=105)
  paper(im,(51,863,968,258),'paper',seed=104)
  TXT(im,'MONTSERRAT CABALLÉ',80,897,67,'black','block',maxw=875)
  TXT(im,'TWO MUSICAL WORLDS.',84,987,52,'red','block')
  TXT(im,'ONE VOICE WITH NO LIMITS.',83,1087,40,'paper','mono',maxw=900)
 elif idx==5:
  photo_frame(im,PHOTOS['freddie'],(190,100,835,1050),seed=112,contrast=1.05,focus=(.46,.4),colorize='gold')
  paper(im,(55,495,956,491),'black',seed=113)
  wordstack(im,['35 YEARS.','STILL','HERE.'],77,521,868,116,'paper','display')
  badge(im,'THANK YOU, FREDDIE.',(65,1090,944,100),'gold','black',115,size=78)
 brand(im,'FREDDIE',idx)
 return im

def story(name):
 h=1920;im=make_base(name,h=h,seed=401 if name=='SEXPISTOLS' else 501);d=ImageDraw.Draw(im)
 source=PHOTOS[THEMES[name]['photo']]
 if name=='SEXPISTOLS':
  d.polygon([(0,150),(1080,20),(1080,1760),(0,1500)],fill=rgb('red'))
  photo_frame(im,source,(52,557,972,980),seed=131,contrast=1.23,focus=(.54,.47),colorize='paper')
  paper(im,(35,147,1010,330),'black',seed=132)
  wordstack(im,['SEX','PISTOLS'],65,150,910,187,'paper','display',.92)
  badge(im,'51 YEARS OF NOISE.',(48,505,947,102),'yellow','black',133,size=94)
  badge(im,'6 NOVEMBER 1975',(57,1510,930,89),'paper','black',134,size=69)
  TXT(im,'FIRST GIG: ST MARTIN\'S SCHOOL OF ART',61,1629,38,'paper','mono',maxw=955)
  TXT(im,'LONDON, NOT MANCHESTER.',61,1691,34,'yellow','mono',maxw=945)
  # 3 languages embedded in story, no caption
  TXT(im,'FIRST GIG. / PRIMER CONCIERTO. / LEHEN KONTZERTUA.',56,1764,26,'paper','sans',maxw=960)
 else:
  # neon-wave CRT poster, singer and retro television with pixel heart
  d.polygon([(0,180),(1055,100),(1070,1650),(85,1780)],fill=rgb('blue'))
  for j in range(15):d.line((50+j*78,380,120+j*75,1560),fill=rgb('cyan'),width=3)
  photo_frame(im,source,(76,658,918,850),seed=149,contrast=1.25,focus=(.45,.3),tint='pink')
  paper(im,(42,137,994,397),'black',seed=150)
  wordstack(im,['THE HUMAN','LEAGUE'],62,190,940,137,'paper','display',.94)
  badge(im,"DON'T YOU WANT ME?",(47,555,985,102),'pink','black',151,size=87)
  badge(im,'27 NOV 1981 · 45 YEARS',(52,1444,960,95),'cyan','black',152,size=69)
  badge(im,'5 WEEKS AT UK No.1',(59,1573,922,82),'paper','black',153,size=61)
  TXT(im,'THE UNLIKELY HIT. / EL ÉXITO IMPROBABLE.',58,1702,37,'paper','sans',maxw=946)
  TXT(im,'USTEKABEKO ARRAKASTA.',59,1760,35,'cyan','sans',maxw=935)
 brand(im,name,1,count=1)
 return im

META={'MADONNA':('12 NOVEMBER 1984','LIKE A VIRGIN'),'DURAN':('21 NOVEMBER 1983','SEVEN AND THE RAGGED TIGER'),'FREDDIE':('24 NOVEMBER 1991','FREDDIE MERCURY'),'SEXPISTOLS':('6 NOVEMBER 1975','SEX PISTOLS FIRST GIG'),'HUMANLEAGUE':('27 NOVEMBER 1981',"DON'T YOU WANT ME")}
paths=[]
for nm,fn in [('MADONNA',madonna_art),('DURAN',duran_art),('FREDDIE',freddie_art)]:
 for i in range(1,6):
  im=fn(i);p=ROOT/f'{nm}_{i:02d}.jpg';im.save(p,'JPEG',quality=92,subsampling=0,optimize=True);paths.append(p)
for nm in ['SEXPISTOLS','HUMANLEAGUE']:
 im=story(nm);p=ROOT/f'{nm}_STORY.jpg';im.save(p,'JPEG',quality=92,subsampling=0,optimize=True);paths.append(p)
# Proof-sheet for manual QA, not for scheduling/publication
thumbs=[]
for p in paths:
 im=Image.open(p).convert('RGB');im.thumbnail((225,300));a=Image.new('RGB',(250,335),(36,36,36));a.paste(im,((250-im.width)//2,0));ImageDraw.Draw(a).text((8,312),p.name,font=fnt('mono',15),fill=(255,255,255));thumbs.append(a)
proof=Image.new('RGB',(1250,math.ceil(len(thumbs)/5)*335),(10,10,10))
for k,t in enumerate(thumbs):proof.paste(t,(250*(k%5),335*(k//5)))
proof.save(ROOT/'_QA_CONTACT.jpg',quality=85)
json.dump({'files':[{'name':p.name,'w':Image.open(p).size[0],'h':Image.open(p).size[1],'bytes':p.stat().st_size} for p in paths],'meta':META,'credits':CREDIT},open(ROOT/'_QA_MANIFEST.json','w'),indent=2)
print('B21 EDITORIAL V3',len(paths),'images',sum(p.stat().st_size for p in paths),'bytes')