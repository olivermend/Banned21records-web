#!/usr/bin/env python3
"""BANNED 21 RECORDS | November 2026: 15 feed panels + two Stories.
Editorial archive collage; photographs are used as one coherent printed panel,
never cut-out people pasted across unrelated backgrounds.
Images sourced from Wikimedia Commons (credits and licenses in manifest).
"""
import os, io, random, math, textwrap, urllib.request, json, pathlib
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter, ImageFont

PREVIEW=os.environ.get('B21_PREVIEW')=='1'
OUT=pathlib.Path(os.environ.get('B21_OUTPUT','assets/social/editorial-2026/b21-nov-2026-v2'))
OUT.mkdir(parents=True, exist_ok=True)
SRC=pathlib.Path(os.environ.get('B21_CACHE_DIR','/tmp/b21-nov26-src')); SRC.mkdir(parents=True,exist_ok=True)
W,H=1080,1350
CREAM=(244,237,219); INK=(14,13,14); RED=(236,42,35); ACID=(225,238,39); HOT=(250,43,132); CYAN=(75,230,238); GOLD=(211,174,111); FADED=(181,172,156)
FONT_ROOT='/usr/share/fonts/truetype/noto'
HEAD=f'{FONT_ROOT}/NotoSans-CondensedBlack.ttf'
NARROW=f'{FONT_ROOT}/NotoSans-ExtraCondensedBlack.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
HAND='/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
for name in ['HEAD','NARROW']:
 if not os.path.exists(globals()[name]):globals()[name]='/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'

SOURCES={
 'sex':('https://upload.wikimedia.org/wikipedia/commons/1/1e/Sex_Pistols_in_Paradiso.jpg',
         'Koen Suyk / Nationaal Archief; CC0; photo Jan 1977','https://commons.wikimedia.org/wiki/File:Sex_Pistols_in_Paradiso.jpg'),
 'madonna':('https://upload.wikimedia.org/wikipedia/commons/5/53/MadonnaVirginTour.jpg',
         'Bill Lanphier; CC BY 3.0; photo 1985','https://commons.wikimedia.org/wiki/File:MadonnaVirginTour.jpg'),
 'duran':('https://upload.wikimedia.org/wikipedia/commons/f/f6/Duran_Duran.jpg',
         'Samira Khan; CC BY 2.0; Toronto concert, 5 April 2005','https://commons.wikimedia.org/wiki/File:Duran_Duran.jpg'),
 'freddie':('https://upload.wikimedia.org/wikipedia/commons/0/02/Queen_-_Freddie_Mercury.jpg',
         'Carl Lender; CC BY 2.0; photo Nov 1977','https://commons.wikimedia.org/wiki/File:Queen_-_Freddie_Mercury.jpg'),
 'human':('https://upload.wikimedia.org/wikipedia/commons/6/67/Philip_Oakey_2014.jpg',
         'Jeffrey Pardoen; CC BY 2.0; Philip Oakey of The Human League, 11 July 2014','https://commons.wikimedia.org/wiki/File:Philip_Oakey_2014.jpg')
}
LOCAL={
 'sex':'/mnt/data/a_gritty_punk_rock_concert_collage_scene_high_con.png',
 'madonna':'/mnt/data/wide_vintage_collage_retro_poster_style_scene_gri.png',
 'duran':'/mnt/data/wide_stylized_retro_1980s_synthwave_collage_poste.png',
 'freddie':'/mnt/data/a_gritty_punk_rock_concert_collage_scene_high_con.png',
 'human':'/mnt/data/wide_stylized_retro_1980s_synthwave_collage_poste.png'
}

def load_images():
 ret={}
 import urllib.parse,time
 for name,(url,credit,attribution) in SOURCES.items():
  if PREVIEW:
   ret[name]=Image.open(LOCAL[name]).convert('RGB');continue
  dest=SRC/(name+'.jpg')
  if not dest.exists():
   origin=url.removeprefix('https://')
   file_uri=url.rsplit('/',1)[-1]
   candidates=[
       url,
       'https://wsrv.nl/?url='+urllib.parse.quote(origin,safe=''),
       'https://wsrv.nl/?url='+urllib.parse.quote(url,safe=''),
       'https://images.weserv.nl/?url='+urllib.parse.quote(origin,safe=''),
       'https://images.weserv.nl/?url='+urllib.parse.quote(url,safe=''),
       'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+file_uri,
       'https://commons.wikimedia.org/wiki/Special:FilePath/'+file_uri]

   errors=[]
   for candidate in candidates:
    try:
     req=urllib.request.Request(candidate,headers={'User-Agent':'Mozilla/5.0 (B21EditorialBot/1.0)','Accept':'image/jpeg,image/*;q=0.9,*/*;q=0.6'})
     with urllib.request.urlopen(req,timeout=30) as response:data=response.read()
     if len(data)<5000:raise RuntimeError('too small: '+str(len(data)))
     test=Image.open(io.BytesIO(data));test.verify()
     dest.write_bytes(data)
     print('Downloaded',name,len(data),'bytes via',candidate.split('/')[2],flush=True)
     break
    except Exception as err:
     errors.append(str(err)[:190]);time.sleep(.5)
   if not dest.exists():raise RuntimeError('Could not download '+name+': '+str(errors))
  ret[name]=Image.open(dest).convert('RGB')
 return ret

PHOTOS=load_images()

def font(size,face=HEAD):return ImageFont.truetype(face,int(size))
def text_size(d,s,f=HEAD,size=60):
 b=d.textbbox((0,0),s,font=font(size,f));return b[2]-b[0],b[3]-b[1]
def fitting(d,s,maxw,size=90,minsize=22,face=HEAD):
 while size>minsize and text_size(d,s,face,size)[0]>maxw:size-=2
 return size

def txt(d,x,y,s,size=60,col=CREAM,f=HEAD,maxw=None):
 if maxw is not None:size=fitting(d,s,maxw,size,25,f)
 d.text((x,y),s,font=font(size,f),fill=col,stroke_width=0)
 return text_size(d,s,f,size)[1]

def paper_bg(seed,light=False,size=(W,H)):
 bg=CREAM if light else INK
 im=Image.new('RGB',size,bg);d=ImageDraw.Draw(im);r=random.Random(seed)
 dark=(42,37,36) if light else (190,181,164)
 for _ in range(4200):
  x=r.randrange(size[0]);y=r.randrange(size[1]);radius=r.randrange(1,4)
  d.ellipse((x,y,x+radius,y+radius),fill=dark if r.random()<.3 else (80,75,75) if light else (62,60,56))
 for _ in range(150):
  y=r.randrange(size[1]);x=r.randrange(size[0]);step=r.randint(10,100)
  d.line((x,y,x+step,y+r.randrange(-2,3)),fill=(170,164,157) if light else (47,44,44),width=1)
 return im

def ripped_poly(box,seed=1):
 x0,y0,x1,y1=box;r=random.Random(seed)
 pts=[]
 for x in range(x0,x1,19):pts.append((x,y0+r.randint(-9,9)))
 for y in range(y0,y1,19):pts.append((x1+r.randint(-9,9),y))
 for x in range(x1,x0,-19):pts.append((x,y1+r.randint(-9,9)))
 for y in range(y1,y0,-19):pts.append((x0+r.randint(-9,9),y))
 return pts

def blot(d,rect,color,seed):d.polygon(ripped_poly(rect,seed),fill=color)

def photo_film(src,size,seed=1,cool=False):
 im=ImageOps.fit(src,size,method=Image.Resampling.LANCZOS,centering=(.5,.42))
 im=ImageEnhance.Contrast(im).enhance(1.26)
 gray=ImageOps.autocontrast(ImageOps.grayscale(im))
 tint=ImageOps.colorize(gray,black=(8,9,11),white=(234,222,192) if not cool else (178,230,235))
 im=Image.blend(im,tint,.55)
 r=random.Random(seed); d=ImageDraw.Draw(im,'RGBA')
 for _ in range(175):
  x=r.randrange(size[0]);y=r.randrange(size[1]);dy=r.randrange(3,47)
  d.line((x,y,x+r.randrange(-3,4),y+dy),fill=(247,238,219,r.randrange(5,43)),width=1)
 return im

def frame_photo(im,src,box,seed,mode='fill',cool=False,angle=0):
 x0,y0,x1,y1=box;w=x1-x0;h=y1-y0
 if mode=='contain':
  tile=ImageOps.contain(src,(w,h),method=Image.Resampling.LANCZOS)
  canv=Image.new('RGB',(w,h),INK);canv.paste(tile,((w-tile.width)//2,(h-tile.height)//2))
  tile=photo_film(canv,(w,h),seed,cool)
 else:tile=photo_film(src,(w,h),seed,cool)
 if angle:
  tile=tile.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
  im.paste(tile,(int((x0+x1-tile.width)/2),int((y0+y1-tile.height)/2)))
 else: im.paste(tile,(x0,y0))
 d=ImageDraw.Draw(im)
 for _ in range(5):
  xx=x0+random.Random(seed+_).randrange(0,max(1,w-80))
  d.line((xx,y0,xx+28,y0+4),fill=CREAM,width=3)
 return im

def note(im,s,rect,seed=1,bg=CREAM,fg=INK,rot=-4,size=40,face=HAND):
 x,y,w,h=rect
 sheet=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(sheet)
 d.polygon(ripped_poly((7,8,w-8,h-8),seed),fill=bg+(255,))
 lines=s.split('\n');yy=(h-len(lines)*size*1.18)/2
 for line in lines:
  fs=fitting(d,line,w-34,size,19,face)
  txw=text_size(d,line,face,fs)[0]
  d.text(((w-txw)//2,yy),line,font=font(fs,face),fill=fg)
  yy+=size*1.2
 sheet=sheet.rotate(rot,resample=Image.Resampling.BICUBIC,expand=True)
 im.paste(sheet,(x,y),sheet)

def header(im,n,idx,qty=5,light=False):
 d=ImageDraw.Draw(im);w,h=im.size;fg=INK if light else CREAM
 d.rectangle((48,38,w-48,43),fill=RED)
 txt(d,57,53,'BANNED',25,fg,HEAD);txt(d,205,47,'21',32,RED,HEAD);txt(d,260,53,'RECORDS',25,fg,HEAD)
 if qty==5:txt(d,w-183,54,f'{idx:02d} / 05',24,fg,MONO)
 d.rectangle((48,h-70,w-48,h-66),fill=RED)
 txt(d,56,h-59,'BILBAO  ·  EST. 2026',18,fg,MONO)
 txt(d,w-343,h-59,'BAD IDEAS. LOUD MUSIC.',17,fg,MONO)

def display_lines(d,lines,x,y,w,sz=110,color=CREAM,face=HEAD,leading=1.04):
 for line in lines:
  fsize=fitting(d,line,w,sz,30,face)
  txt(d,x,y,line,fsize,color,face);y+=max(65,int(fsize*leading))
 return y

# Design variations: each caption panel uses a single contiguous archive photograph
# as a coherent printed poster element, not a cut-out person pasted from another scene.

def scene(slug,idx,photo,title,lines,chip,detail,accent,seed):
 r=random.Random(seed)
 light=(idx in [2,4]); im=paper_bg(seed,light)
 d=ImageDraw.Draw(im)
 if idx==1:
  # Archival image under distressed ink, the subject stays recognisable.
  frame_photo(im,photo,(55,145,1025,1165),seed,cool=accent==CYAN)
  tint=Image.new('RGBA',(W,H),(0,0,0,0));td=ImageDraw.Draw(tint)
  td.polygon([(45,144),(580,140),(735,680),(520,1200),(45,1190)],fill=INK+(217,))
  td.rectangle((45,990,1026,1163),fill=INK+(169,))
  im=Image.alpha_composite(im.convert('RGBA'),tint).convert('RGB');d=ImageDraw.Draw(im)
  blot(d,(64,215,705,290),accent,seed);txt(d,84,226,chip,31,INK,MONO,maxw=592)
  yy=356;yy=display_lines(d,lines,64,yy,920,114,CREAM)
  note(im,detail,(83,957,890,126),seed+1,bg=CREAM,fg=INK,rot=-2,size=34,face=HEAD)
 elif idx==2:
  frame_photo(im,photo,(60,186,692,1095),seed,cool=accent==CYAN)
  d=ImageDraw.Draw(im);d.rectangle((55,180,699,1100),outline=accent,width=13)
  blot(d,(610,210,1009,1110),CREAM if not light else INK,seed+3)
  x=637;fg=INK if not light else CREAM
  txt(d,651,247,'// 02',35,accent,MONO)
  display_lines(d,lines,642,371,342,78,fg)
  # Printed fact slips, not flat geometric blocks.
  note(im,chip,(629,765,370,114),seed+4,bg=accent,fg=INK,rot=-5,size=26,face=MONO)
  note(im,detail,(630,899,390,190),seed+5,bg=CREAM if not light else (236,233,221),fg=INK,rot=3,size=24,face=HAND)
 elif idx==3:
  frame_photo(im,photo,(60,180,1020,1168),seed,cool=accent==CYAN)
  img=Image.new('RGBA',(W,H),(0,0,0,0));oi=ImageDraw.Draw(img)
  oi.rectangle((61,181,1018,1167),fill=(7,6,6,107))
  im=Image.alpha_composite(im.convert('RGBA'),img).convert('RGB');d=ImageDraw.Draw(im)
  blot(d,(82,245,970,335),accent,seed+7)
  txt(d,105,250,chip,40,INK,MONO,maxw=824)
  display_lines(d,lines,72,435,950,118,CREAM)
  note(im,detail,(95,949,850,140),seed+8,bg=CREAM,fg=INK,rot=4,size=34,face=HAND)
 elif idx==4:
  # Gallery spread with coherent photos from the same original, not human cut-outs.
  frame_photo(im,photo,(65,215,664,875),seed)
  frame_photo(im,photo,(235,874,1018,1165),seed+31)
  d=ImageDraw.Draw(im);d.rectangle((60,210,669,881),outline=accent,width=11)
  blot(d,(580,225,1016,880),CREAM if not light else INK,seed+5)
  fg=INK if not light else CREAM
  display_lines(d,lines,625,329,345,77,fg)
  note(im,chip,(628,778,355,102),seed+6,bg=accent,rot=-4,size=25,face=MONO)
  note(im,detail,(93,1010,860,116),seed+7,bg=CREAM,rot=2,size=28,face=HAND)
 else:
  frame_photo(im,photo,(55,147,1025,792),seed,cool=accent==CYAN)
  shade=Image.new('RGBA',(W,H),(0,0,0,0));sd=ImageDraw.Draw(shade)
  sd.rectangle((50,145,1029,796),fill=INK+(75,))
  im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB');d=ImageDraw.Draw(im)
  # full-height magazine clipping with a strong editorial question
  blot(d,(65,782,1019,1150),accent,seed+3)
  display_lines(d,lines,88,824,905,109,INK)
  note(im,detail,(102,1040,842,104),seed+4,bg=CREAM,rot=-2,size=30,face=HAND)
  txt(d,72,185,chip,32,CREAM,MONO,maxw=900)
 d=ImageDraw.Draw(im)
 # archival date tag prevents misleading that 1977 photo depicts an earlier historical show
 tag={'madonna':'ARCHIVE PHOTO / 1985','duran':'ARCHIVE PHOTO / 2005','freddie':'ARCHIVE PHOTO / 1977'}[slug]
 by=1235 if idx==5 else 1203
 if slug=='madonna':credit='PHOTO: BILL LANPHIER · CC BY 3.0 (EDITED)'
 elif slug=='duran':credit='PHOTO: SAMIRA KHAN · CC BY 2.0 (EDITED)'
 else:credit='PHOTO: CARL LENDER · CC BY 2.0 (EDITED)'
 d.rounded_rectangle((395,by,1020,by+30),3,fill=INK)
 txt(d,403,by+2,credit,16,CREAM,MONO,maxw=610)
 d.rounded_rectangle((66,by,390,by+30),3,fill=INK)
 txt(d,76,by+2,tag,19,CREAM,MONO,maxw=300)
 header(im,slug,idx,light=light)
 return im

POSTS={
 'MADONNA':{
 'slug':'madonna','accent':HOT,
 'slides':[
 (['LIKE A','VIRGIN.'],'12 NOV 1984','42 YEARS. SAME CULTURAL AFTERSHOCK.'),
 (['HER SECOND','STUDIO','ALBUM.'],'ALBUM 02','THE RECORD THAT MADE HEADLINES.'),
 (['NILE','RODGERS.'],'PRODUCED BY','CHIC DISCO BRAINS + POP AMBITION.'),
 (['FOUR US','TOP FIVE','SINGLES.'],'1984 TO 1985','LIKE A VIRGIN · MATERIAL GIRL · ANGEL · DRESS YOU UP.'),
 (['SHE DIDN\'T','ASK FOR','PERMISSION.'],'42 YEARS ON','WHICH MADONNA TRACK STILL HITS?')]
 },
 'DURAN':{
 'slug':'duran','accent':CYAN,
 'slides':[
 (['SEVEN AND','THE RAGGED','TIGER.'],'21 NOV 1983','43 YEARS OF SYNTHS, HAIR & DRAMA.'),
 (['THE','THIRD','ALBUM.'],'LP 03','NOVEMBER 21, 1983.'),
 (['THE','REFLEX.'],'SIDE A / TRACK 01','A BIG SINGLE FROM AN EVEN BIGGER ERA.'),
 (['UNION OF','THE SNAKE.'],'THE SINGLES','NEW MOON ON MONDAY. THE REFLEX.'),
 (['LOUD','LOOKS.','LOUDER','SYNTHS.'],'NEW ROMANTIC','WHICH DURAN DURAN SONG GOES ON FIRST?')]
 },
 'FREDDIE':{
 'slug':'freddie','accent':GOLD,
 'slides':[
 (['FREDDIE','MERCURY.'],'24 NOVEMBER 1991','1946–1991. 35 YEARS WITHOUT HIM.'),
 (['THE','VOICE.'],'REMEMBERING FREDDIE','AN EXTRAORDINARY SINGER.'),
 (['THE','ARTIST.'],'SONGWRITER / PERFORMER','A CREATIVE FORCE BEYOND GENRES.'),
 (['BEYOND','QUEEN.'],'BARCELONA / 1988','TOGETHER WITH MONTSERRAT CABALLÉ.'),
 (['THE MUSIC','STAYS.'],'THANK YOU, FREDDIE','35 YEARS ON. AN ENDURING LEGACY.')]
 }
}

def story(slug,title,date,lines,sub,accent,seed):
 w,h=1080,1920;im=paper_bg(seed,size=(w,h))
 photo=PHOTOS[slug];frame_photo(im,photo,(52,230,1028,1492),seed,cool=slug=='human')
 fade=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(fade)
 d.rectangle((50,220,1030,630),fill=(9,8,8,160))
 d.rectangle((50,1174,1030,1495),fill=(9,8,8,174))
 im=Image.alpha_composite(im.convert('RGBA'),fade).convert('RGB');d=ImageDraw.Draw(im)
 blot(d,(60,238,980,370),accent,seed+9)
 txt(d,88,254,title,58,INK,HEAD,maxw=850)
 txt(d,73,411,date,61,CREAM,MONO,maxw=930)
 yy=565;yy=display_lines(d,lines,69,yy,930,118,CREAM)
 note(im,sub,(73,1320,865,143),seed+1,bg=CREAM,rot=-3,size=42,face=HAND)
 blot(d,(48,1495,1034,1790),CREAM,seed+15)
 dd=ImageDraw.Draw(im)
 if slug=='sex':
  labels=['FIRST CONCERT.','PRIMER CONCIERTO.','LEHEN KONTZERTUA.']
 else:
  labels=['THE UNLIKELY HIT.','EL ÉXITO IMPROBABLE.','USTEKABEKO ARRAKASTA.']
 for j,line in enumerate(labels):txt(dd,76,1530+j*78,line,45-j*4,INK,HEAD,maxw=906)
 source_note=('PHOTO: K. SUYK · CC0 · 1977' if slug=='sex' else 'PHOTO: J. PARDOEN · CC BY 2.0 (EDITED) · 2014')
 txt(dd,75,1785,source_note,20,INK,MONO,maxw=900)
 dd.rectangle((65,1830,1014,1836),fill=RED)
 txt(dd,69,1848,'BANNED',42,CREAM,HEAD);txt(dd,300,1844,'21',52,RED,HEAD);txt(dd,386,1848,'RECORDS',42,CREAM,HEAD)
 return im

def make_all():
 created=[]
 for prefix,pack in POSTS.items():
  slug=pack['slug'];accent=pack['accent']
  for j,(lines,chip,detail) in enumerate(pack['slides'],1):
   p=OUT/f'{prefix}_{j:02d}.jpg';im=scene(slug,j,PHOTOS[slug],prefix,lines,chip,detail,accent,seed={'madonna':10,'duran':32,'freddie':70}[slug]+j)
   im.save(p,'JPEG',quality=88,subsampling=1,optimize=True);created.append(p)
 specs=[
   ('SEXPISTOLS_STORY.jpg',story('sex','SEX PISTOLS','06 NOV 1975',['51 YEARS OF','NOISE.'],"ST MARTIN'S SCHOOL OF ART · LONDON",RED,208)),
   ('HUMANLEAGUE_STORY.jpg',story('human','THE HUMAN LEAGUE','27 NOV 1981',["DON'T YOU",'WANT ME?'],'5 WEEKS AT UK NO. 1 / CHRISTMAS 1981',HOT,309)),
 ]
 for filename,im in specs:
  p=OUT/filename;im.save(p,'JPEG',quality=88,subsampling=1,optimize=True);created.append(p)
 # Metadata/citations kept next to reproducible generated sources, not uploaded into Metricool.
 manifest={'files':[p.name for p in created],'photo_sources':{k:{'url':v[0],'credit_and_license':v[1],'source_page':v[2]} for k,v in SOURCES.items()},'archive_photo_dates_do_not_match_historical_anniversary_dates':True}
 (OUT/'SOURCES_AND_QA.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 thumbs=[]
 for p in created:
  im=Image.open(p);im.thumbnail((250,320))
  c=Image.new('RGB',(270,340),(45,45,45));c.paste(im,((270-im.width)//2,(340-im.height)//2));thumbs.append(c)
 grid=Image.new('RGB',(1350,1360),(28,28,28))
 for i,im in enumerate(thumbs):grid.paste(im,((i%5)*270,(i//5)*340))
 if PREVIEW:grid.save(OUT/'CONTACT_REVIEW.jpg',quality=87)
 print('CREATED',len(created),'IMAGES',OUT,flush=True)

if __name__=='__main__':make_all()