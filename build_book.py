# SPDX-License-Identifier: MIT
"""Build an A5 Chinese reader with explicit page-local references."""
from pathlib import Path
import re, json, html
import shutil
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Paragraph, Table, TableStyle, Flowable
from PIL import Image
from illustration_data import FRONT_ART
from figure_markup import frontmatter_captions
from book_structure import CHAPTERS, BY_ID, chapter_text, chapter_title, chapter_link_id, validate_structure
import fitz

ROOT = Path(__file__).resolve().parent
PUBLICATION = json.loads((ROOT / 'publication.json').read_text(encoding='utf-8'))
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
W, H = 419.53, 595.28
M = 39
CW = W - 2*M
FONT = 'CupSans'
pdfmetrics.registerFont(TTFont(FONT, str(ROOT/'assets/NotoSansSC-Regular.ttf')))
INK = HexColor('#222222')
GRAY = HexColor('#626762')
LINE = HexColor('#D9D9D9')
ACCENT = HexColor('#526852')
STYLES = {
    'body': ParagraphStyle('body', fontName=FONT, fontSize=10.25, leading=16.3,
       textColor=INK, wordWrap='CJK', spaceAfter=8, splitLongWords=True),
    'caption': ParagraphStyle('caption', fontName=FONT, fontSize=8.3, leading=12.2,
       textColor=GRAY, wordWrap='CJK', spaceAfter=5),
    'small': ParagraphStyle('small', fontName=FONT, fontSize=7.6, leading=11,
       textColor=GRAY, wordWrap='CJK', splitLongWords=True),
    'head': ParagraphStyle('head', fontName=FONT, fontSize=18.5, leading=25,
       textColor=black, wordWrap='CJK', spaceAfter=16),
    'sub': ParagraphStyle('sub', fontName=FONT, fontSize=13.4, leading=19,
       textColor=black, wordWrap='CJK', spaceAfter=13),
    'table': ParagraphStyle('table', fontName=FONT, fontSize=9.1, leading=13.5,
       textColor=INK, wordWrap='CJK'),
    'bib': ParagraphStyle('bib', fontName=FONT, fontSize=8.9, leading=13.5,
       textColor=INK, wordWrap='CJK', spaceAfter=10, splitLongWords=True),
}
sources = {s['id']:s for s in json.loads((ROOT/'research/sources.json').read_text())}
FRONT_CAPTIONS = frontmatter_captions(ROOT)
pages = []
validate_structure()
for chapter in CHAPTERS:
    file = ROOT / chapter['source']
    text = chapter_text(chapter)
    pieces = re.split(r'<!-- page: ([^|]+)\|([^|]+)\|(.+?) -->\s*', text)
    for i in range(1,len(pieces),4):
        ident,part,title,body = pieces[i:i+4]
        refs = set(re.findall(r'\[(\d{2,3})\]',body))
        for kind,extra in {'kinship':['15','34','37'],'evidence':['02','03','04'],'tea':['34']}.items():
            if '@diagram '+kind in body:refs.update(extra)
        refs=sorted(refs, key=int)
        for r in refs:
            assert r in sources, (file,r)
        pages.append(dict(ident=ident,part=part,title=title,body=body.strip(),refs=refs))

def rich(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'\[([^\]]+)\]\(([^)\s]+\.md)\)',
                lambda m:f'<link href="#chapter-{chapter_link_id(m[2])}" color="#526852">{m[1]}</link>',text)
    def ref(m):
        r=m.group(1)
        return f'<super><link href="{html.escape(sources[r]["url"],quote=True)}" color="#526852">[{r}]</link></super>'
    return re.sub(r'\[(\d{2,3})\]',ref,text)

def para(text,style='body'):
    return Paragraph(rich(text),STYLES[style])

def table(rows):
    n=len(rows[0])
    widths = [CW*.25,CW*.36,CW*.39] if n==3 else [CW*.30,CW*.70]
    cells=[[Paragraph(html.escape(cell),STYLES['table']) for cell in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([
       ('BACKGROUND',(0,0),(-1,0),HexColor('#E9EEEA')),
       ('GRID',(0,0),(-1,-1),.4,LINE),
       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
       ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
       ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    return t


class TeachingFigure(Flowable):
    def __init__(self,path,height=None):
        Flowable.__init__(self)
        self.path=(ROOT/'chapters'/path).resolve()
        assert self.path.is_relative_to(ROOT/'assets/figures'), self.path
        iw,ih=Image.open(self.path).size
        self.width=CW;self.height=min(float(height),CW*ih/iw) if height else CW*ih/iw
        self.image_width=self.height*iw/ih
    def draw(self):
        self.canv.drawImage(str(self.path),(CW-self.image_width)/2,0,self.image_width,self.height)

class CompositionSketch(Flowable):
    def __init__(self):Flowable.__init__(self);self.width=CW;self.height=92
    def draw(self):
        c=self.canv
        for i,(name,extra,col) in enumerate([('浓缩','咖啡基底',None),('美式','咖啡加水','#DEEAF0'),('奶咖','咖啡加奶','#F0E5D2')]):
            x=26+i*112;y=28
            c.setFillColor(HexColor('#865936'));c.rect(x,y,42,14 if col else 45,fill=1,stroke=0)
            if col:c.setFillColor(HexColor(col));c.rect(x,y+14,42,31,fill=1,stroke=0)
            c.setStrokeColor(GRAY);c.rect(x,y,42,45,fill=0,stroke=1)
            c.setFont(FONT,9);c.setFillColor(INK);c.drawCentredString(x+21,78,name)


def figure_region(c,key,x,y,w):
    # A PDF viewport into an unmodified generated sheet, not a raster edit.
    filename,rect=FRONT_ART[key]
    img=ROOT/'assets'/filename
    iw,ih=Image.open(img).size
    x0,y0,x1,y1=[v*s for v,s in zip(rect,(iw/1536,ih/1024,iw/1536,ih/1024))]
    scale=w/(x1-x0); h=(y1-y0)*scale
    c.saveState(); p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0)
    c.drawImage(str(img),x-x0*scale,y-(ih-y1)*scale,iw*scale,ih*scale)
    c.restoreState()
    return h

def blocks(body):
    lines=body.splitlines(); result=[];i=0;figure_height=None
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        height_marker=re.fullmatch(r'<!-- figure-height: ([\d.]+) -->',line)
        if height_marker:
            figure_height=height_marker.group(1);i+=1;continue
        if line.startswith('**图 ') or line.startswith('**图例。**'):
            result.append(('flow',para(line,'caption')));i+=1;continue
        figure=re.fullmatch(r'!\[([^\]]+)\]\(([^)]+)\)',line)
        if figure:
            result.append(('flow',TeachingFigure(figure.group(2),figure_height)));figure_height=None;i+=1;continue
        if line=='@table':
            rows=[];i+=1
            while lines[i].strip()!='@endtable':
                rows.append(lines[i].split('|'));i+=1
            result.append(('flow',table(rows)));i+=1;continue
        if line.startswith('@diagram '):
            kind=line.split()[1]
            if kind=='kinship':
                rows=[['饮品','材料与主要变化','饮用前的呈现'],
                 ['酒','糖的准备 发酵\n部分再蒸馏熟成','温度 稀释或调配'],
                 ['茶','叶子加工\n控制氧化及其他变化','以水冲泡或煮饮'],
                 ['咖啡','果实处理\n种子干燥与烘焙','研磨后冲煮']]
            elif kind=='evidence':
                rows=[['年代线索','地点与研究解释'],
                 ['约一万三千年前','Raqefet 洞穴\n石臼遗存与谷物酿造解释 [04]'],
                 ['约公元前第七千纪','河南贾湖\n米 蜂蜜与水果混合饮品 [02]'],
                 ['约公元前 6000—5800 年','格鲁吉亚\n葡萄酒相关证据 [03]']]
            elif kind=='tea':
                rows=[['茶类','入门观察方向'],['绿茶','较早控制酶相关变化'],
                 ['白茶 黄茶','分别关注萎凋干燥与闷黄'],['乌龙 红茶','关注氧化与其他工序的安排'],
                 ['黑茶','关注微生物相关加工过程']]
            result.append(('flow',table(rows)));i+=1;continue
        if line.startswith('# '):
            result.append(('flow',para(line[2:],'head')));i+=1;continue
        if line.startswith('## '):
            result.append(('flow',para(line[3:],'sub')));i+=1;continue
        ps=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','@')):
            ps.append(lines[i].strip());i+=1
        result.append(('flow',para(''.join(ps))))
    return result

def short_publisher(s):
    return {'01':'NIDCD','02':'McGovern 等 · PNAS','03':'McGovern 等 · PNAS',
     '07':'AHA 美国家庭酿酒协会','08':'Brewers Association',
     '20':'SWA 苏格兰威士忌协会','21':'SWA 苏格兰威士忌协会','22':'SWA 苏格兰威士忌协会',
     '04':'Liu 等 · JAS Reports','14':'Frontiers in Microbiology','18':'Foods',
     '19':'Journal of Ethnic Foods','23':'BNIC','24':'Smithsonian','28':'CRT',
     '30':'IBA','31':'UNESCO','32':'V&A','33':'英国国家档案馆','34':'Food Chemistry X',
     '35':'NCA','36':'WCR','37':'ICO','38':'Foods','39':'SCA','40':'SCA',
     '41':'NCA','42':'WCR','43':'NIAAA','44':'FDA','45':'Lu 等 · Scientific Reports',
     '46':'NIAAA','49':'James A. Benn','50':'PDG · LBNL',
     '64':'UKTIA','67':'NCA','68':'NCA','69':'NCA','70':'SCA'}.get(s['id'],s['publisher'].split(' ')[0])

def foot_objects(refs):
    ps=[]
    if refs:
        for r in refs:
            s=sources[r]
            value=f'[{r}] {short_publisher(s)} · {s["short"]} · {s["year"]}　<a href="{html.escape(s["url"],quote=True)}" color="#526852">原文</a>'
            ps.append(Paragraph(html.escape(value) if False else value,STYLES['small']))
    return ps

toc={}
diagnostics=[]
P=0
def frame(c,part):
    c.setFillColor(GRAY);c.setFont(FONT,7.3)
    c.drawString(M,H-24,'杯中世界')
    c.drawRightString(W-M,H-24,part)
    c.setStrokeColor(LINE);c.setLineWidth(.4);c.line(M,H-31,W-M,H-31)
    c.setFont(FONT,8);c.drawCentredString(W/2,19,str(P))

def newpage(c):
    global P
    if P:c.showPage()
    P+=1

def draw_content(c,page,collect):
    newpage(c); frame(c,page['part'])
    ident=page['ident']
    if ident not in toc and collect:toc[ident]=P
    if ident not in seen:
        seen.add(ident);c.bookmarkPage('chapter-'+ident)
        title=chapter_title(BY_ID[ident])
        c.addOutlineEntry(title,'chapter-'+ident,level=0,closed=False)
    foots=foot_objects(page['refs'])
    heights=[p.wrap(CW,100)[1] for p in foots]
    foot_total=sum(heights)+3*max(0,len(foots)-1)
    bottom=39+foot_total+19
    y=H-49
    content_bottom=y
    for kind,obj in blocks(page['body']):
        ww,hh=obj.wrap(CW,H)
        if y-hh<bottom-0.1:
            raise ValueError(f'Page overflow chapter {ident} / {page["title"]}: y={y:.1f} need={hh:.1f} bottom={bottom:.1f}')
        content_bottom=y-hh
        obj.drawOn(c,M,content_bottom);y-=hh+(obj.getSpaceAfter() if isinstance(obj,Paragraph) else 10)
    if foots:
        c.setStrokeColor(LINE);c.line(M,bottom-9,W-M,bottom-9)
    fy=bottom-18
    for obj,hh in zip(foots,heights):
        obj.drawOn(c,M,fy-hh);fy-=hh+3
    diagnostics.append(dict(page=P,chapter=ident,title=page['title'],refs=page['refs'],body_bottom=round(content_bottom,2),footnote_top=round(bottom,2),gap=round(content_bottom-bottom,2)))

def cover(c):
    newpage(c);c.setFillColor(HexColor('#F8F5EE'));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(black);c.setFont(FONT,34);c.drawString(M,H-91,'杯中世界')
    c.setFont(FONT,15);c.drawString(M,H-124,'酒 茶 咖啡的起源与风味')
    c.setFont(FONT,10);c.setFillColor(GRAY);c.drawString(M,H-153,'个人兴趣阅读与学习')
    figure_region(c,'cover',M,174,CW)
    note=para(FRONT_CAPTIONS['cover'],'caption')
    ww,hh=note.wrap(CW,H);note.drawOn(c,M,164-hh)
    c.setFillColor(INK);c.setFont(FONT,10)
    c.drawString(M,119,'从原料与加工开始，读懂一杯饮料。')
    c.drawString(M,99,'短章阅读  当页资料  日常观察')
    c.setFillColor(GRAY);c.setFont(FONT,8)
    c.setFont(FONT,10);c.drawString(M,76,PUBLICATION['credit'])
    c.setFont(FONT,8);c.drawString(M,55,'图解修订版  2026年10月  ·  '+PUBLICATION['content_license'])

def publication_notice(c):
    newpage(c);frame(c,'署名与许可')
    c.bookmarkPage('publication-notice')
    c.addOutlineEntry('署名与许可','publication-notice',level=0,closed=False)
    y=H-63
    sections=[
        ('head','署名与许可'),
        ('sub',PUBLICATION['credit']),
        ('sub',PUBLICATION['content_license']+' · '+PUBLICATION['content_license_name']),
        ('body',PUBLICATION['license_summary']),
        ('body',PUBLICATION['rights_boundary']),
        ('small',PUBLICATION['third_party_notice']),
    ]
    for style,text in sections:
        q=para(text,style);_,hh=q.wrap(CW,H)
        assert y-hh>50, 'Publication notice overflow'
        q.drawOn(c,M,y-hh);y-=hh+STYLES[style].spaceAfter+6
    for label,url in [('许可全文',PUBLICATION['content_license_url']+'legalcode'),
                      ('作品出处',PUBLICATION['source_url'])]:
        q=Paragraph(html.escape(label)+'：<a href="'+html.escape(url,quote=True)+'" color="#526852">'+html.escape(url)+'</a>',STYLES['small'])
        _,hh=q.wrap(CW,H);assert y-hh>40, 'Publication links overflow'
        q.drawOn(c,M,y-hh);y-=hh+8

def contents(c):
    chunks=[]; chunk=[]; y=H-104; lastpart=None
    for chapter in (item for item in CHAPTERS if item['kind'] != 'frontmatter'):
        required=27+(25 if chapter['part']!=lastpart else 0)
        if y-required<89:
            chunks.append(chunk);chunk=[];y=H-104;lastpart=None
        chunk.append(chapter);y-=27+(25 if chapter['part']!=lastpart else 0);lastpart=chapter['part']
    if chunk:chunks.append(chunk)
    for index,chunk in enumerate(chunks):
        newpage(c);frame(c,'目录')
        c.setFillColor(black);c.setFont(FONT,19);c.drawString(M,H-69,'目录' if index==0 else '目录 续')
        y=H-104;lastpart=None
        for chapter in chunk:
            ident=chapter['id']
            p=next(p for p in pages if p['ident']==ident)
            if p['part']!=lastpart:
                c.setFillColor(GRAY);c.setFont(FONT,9);c.drawString(M,y,p['part']);y-=25;lastpart=p['part']
            title=chapter_title(chapter)
            c.setFillColor(INK);c.setFont(FONT,10)
            c.drawString(M,y,title);c.drawRightString(W-M,y,str(toc.get(ident,' ')))
            c.linkRect('', 'chapter-'+ident, (M,y-4,W-M,y+12),relative=0,thickness=0)
            y-=27
        c.setFillColor(GRAY);c.setFont(FONT,8)
        c.drawString(M,57,'点击章节标题可跳转；左侧 PDF 书签也可导航。')
        c.drawString(M,41,'参考资料总目见全书最后；正文引用在相关页下方。')

def opener(c,key,title,subtitle):
    newpage(c);frame(c,title)
    c.setFillColor(black);c.setFont(FONT,24);c.drawString(M,H-91,title)
    obj=para(subtitle);ww,hh=obj.wrap(CW,H);obj.drawOn(c,M,H-119-hh)
    figure_region(c,key,M,152,CW)
    obj=para(FRONT_CAPTIONS[key],'caption')
    ww,hh=obj.wrap(CW,H);obj.drawOn(c,M,113-hh)

def bibliography(c):
    ordered=list(sources.values());y=0
    dates=sorted({s['accessed'] for s in sources.values()})
    intro=f'资料检索日期：{dates[0]} 至 {dates[-1]}。行业资料用于解释工艺与术语，生产者配方展示具体做法；考古结论按证据范围表述。原文链接可能更新。'
    def start():
        nonlocal y
        newpage(c);frame(c,'参考资料')
        c.setFillColor(black);c.setFont(FONT,18);c.drawString(M,H-66,'参考资料')
        y=H-91
    start()
    q=para(intro);ww,hh=q.wrap(CW,H);q.drawOn(c,M,y-hh);y-=hh+18
    for s in ordered:
        text=f'[{s["id"]}] {html.escape(s["publisher"])} · {html.escape(s["year"])} · {html.escape(s["type"])}<br/>{html.escape(s["title"])}<br/><a href="{html.escape(s["url"],quote=True)}" color="#526852">{html.escape(s["url"])}</a>'
        q=Paragraph(text,STYLES['bib']);ww,hh=q.wrap(CW,H)
        if y-hh<40:start()
        q.drawOn(c,M,y-hh);y-=hh+11

def build(path,collect=True):
    global P,seen
    P=0;seen=set();diagnostics.clear()
    c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=1)
    c.setTitle('杯中世界 酒 茶 咖啡的起源与风味');c.setAuthor(PUBLICATION['metadata_credit'])
    c.setSubject('饮品历史 工艺 风味与日常观察；'+PUBLICATION['content_license'])
    c.setKeywords('YZ, 策划与整理, '+PUBLICATION['content_license'])
    cover(c);publication_notice(c);draw_content(c,pages[0],collect);contents(c)
    prev=None
    for page in pages[1:]:
        key=BY_ID[page['ident']].get('opener')
        if key and prev!=page['ident']:
            title,subtitle={'wine':('酒的世界','先问糖从哪里来，再沿着发酵、蒸馏与熟成认识主要酒类。'),
                            'tea':('茶的世界','把一片叶子的加工，与它进入日常生活的历史放在一起。'),
                            'coffee':('咖啡的世界','从果实中的种子，走到烘焙与冲煮；把“浓”拆成具体问题。')}[key]
            opener(c,key,title,subtitle)
        draw_content(c,page,collect);prev=page['ident']
    bibliography(c);c.save()
    return P

# Two passes populate table of contents without a pagination-dependent layout.
target=OUT/'杯中世界.pdf'
count=build(OUT/'first-pass.pdf')
count=build(target,collect=False)
(OUT/'first-pass.pdf').unlink()
# Compress the PDF's raster payload for a practical reading/download size.
# Original PNGs and vector figure masters remain untouched in assets/.
optimized=OUT/'optimized.pdf'
with fitz.open(target) as doc:
    doc.rewrite_images(dpi_threshold=310,dpi_target=270,quality=88,bitonal=False)
    doc.save(optimized,garbage=4,deflate=True)
optimized.replace(target)
(OUT/'layout-check.json').write_text(json.dumps(dict(total_pages=count,pages=diagnostics),ensure_ascii=False,indent=2))

allmd=['# 杯中世界\n\n酒 茶 咖啡的起源与风味\n\n酒、茶、咖啡图解读本\n\n![封面主题插画](assets/figures/scene-cover.png)\n\n'+FRONT_CAPTIONS['cover']+'\n']
allmd.append('\n**'+PUBLICATION['credit']+'**\n')
allmd.append('\n## 署名与许可\n\n['+PUBLICATION['content_license']+' · '+PUBLICATION['content_license_name']+']('+PUBLICATION['content_license_url']+')\n\n'+PUBLICATION['license_summary']+'\n\n'+PUBLICATION['rights_boundary']+'\n\n'+PUBLICATION['third_party_notice']+'\n\n作品出处：'+PUBLICATION['source_url']+'\n\n推荐署名：'+PUBLICATION['attribution']+'\n')
for p in pages:
    body=p['body']
    def mdtable(m):
        rows=m.group(1).strip().splitlines()
        n=len(rows[0].split('|'))
        return '\n'.join(['| '+rows[0]+' |','| '+' | '.join(['---']*n)+' |']+['| '+r+' |' for r in rows[1:]])
    body=re.sub(r'@table\n(.*?)\n@endtable',mdtable,body,flags=re.S)
    md_diagrams={
     'kinship':'饮品|材料与主要变化|饮用前的呈现\n酒|糖的准备 发酵 部分再蒸馏熟成|温度 稀释或调配\n茶|叶子加工 控制氧化及其他变化|以水冲泡或煮饮\n咖啡|果实处理 种子干燥与烘焙|研磨后冲煮',
     'evidence':'年代线索|地点与研究解释\n约一万三千年前|Raqefet 洞穴 石臼遗存与谷物酿造解释 [04]\n约公元前第七千纪|河南贾湖 米 蜂蜜与水果混合饮品 [02]\n约公元前 6000—5800 年|格鲁吉亚 葡萄酒相关证据 [03]',
     'tea':'茶类|入门观察方向\n绿茶|较早控制酶相关变化\n白茶 黄茶|分别关注萎凋干燥与闷黄\n乌龙 红茶|关注氧化与其他工序的安排\n黑茶|关注微生物相关加工过程'}
    for k,v in md_diagrams.items():
        rows=v.splitlines();n=len(rows[0].split('|'))
        value='\n'.join(['| '+rows[0]+' |','| '+' | '.join(['---']*n)+' |']+['| '+r+' |' for r in rows[1:]])
        body=body.replace('@diagram '+k,value)
    body=body.replace('../assets/','assets/')
    body=re.sub(r'\[([^\]]+)\]\(([^)\s]+\.md)\)',
                lambda m:f'[{m[1]}](逐章阅读/{chapter_link_id(m[2])}.md)',body)
    allmd.append('\n---\n\n'+body+('\n\n本页资料：\n' if p['refs'] else '\n'))
    for r in p['refs']:
        s=sources[r];allmd.append(f'- [{r}] {s["publisher"]}，《{s["title"]}》，{s["year"]}。[原文]({s["url"]})\n')
access_dates=sorted({s['accessed'] for s in sources.values()})
allmd.append(f'\n资料检索日期 {access_dates[0]} 至 {access_dates[-1]}。出处与链接见各页资料；分页排版见 PDF。\n')
(OUT/'杯中世界可编辑稿.md').write_text('\n'.join(allmd))
if (OUT/'assets/figures').exists():
    shutil.rmtree(OUT/'assets/figures')
(OUT/'assets/figures').mkdir(parents=True,exist_ok=True)
for image in (ROOT/'assets/figures').glob('*.png'):
    shutil.copy2(image,OUT/'assets/figures'/image.name)
for name in ('tea-fresh-details.png','tea-dry-wet-details.png'):
    shutil.copy2(ROOT/'assets'/name,OUT/'assets'/name)
# Export the existing composition diagram with exactly the PDF's labels.
cp=ROOT/'assets/figures/composition-coffee.pdf'
cc=canvas.Canvas(str(cp),pagesize=(CW,92),invariant=1);CompositionSketch().drawOn(cc,0,0);cc.save()
with fitz.open(cp) as doc:
    bounds=fitz.Rect()
    for _, rect, *_ in doc[0].get_bboxlog():
        bounds |= fitz.Rect(rect)
    bounds=fitz.Rect(bounds.x0-5,bounds.y0-5,bounds.x1+5,bounds.y1+5)&doc[0].rect
    fitted=fitz.open();page=fitted.new_page(width=bounds.width,height=bounds.height)
    page.show_pdf_page(page.rect,doc,0,clip=bounds)
    page.get_pixmap(matrix=fitz.Matrix(4,4)).save(ROOT/'assets/figures/composition-coffee.png')
    fitted.close()
shutil.copy2(ROOT/'assets/figures/composition-coffee.png',OUT/'assets/figures/composition-coffee.png')
print(json.dumps(dict(pdf=str(target),pages=count,chapters=sum(c['kind']=='chapter' for c in CHAPTERS),source_count=len(sources),body_pages=len(pages)),ensure_ascii=False))
