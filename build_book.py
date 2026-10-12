"""Build an A5 Chinese reader with explicit page-local references."""
from pathlib import Path
import re, json, html
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Paragraph, Table, TableStyle, Flowable
from PIL import Image

ROOT = Path(__file__).resolve().parent
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
pages = []
for file in sorted((ROOT/'chapters').glob('*.md')):
    text = file.read_text()
    pieces = re.split(r'<!-- page: ([^|]+)\|([^|]+)\|(.+?) -->\s*', text)
    for i in range(1,len(pieces),4):
        ident,part,title,body = pieces[i:i+4]
        refs = set(re.findall(r'\[(\d\d)\]',body))
        for kind,extra in {'kinship':['15','34','37'],'evidence':['02','03','04'],'tea':['34']}.items():
            if '@diagram '+kind in body:refs.update(extra)
        refs=sorted(refs)
        for r in refs:
            assert r in sources, (file,r)
        pages.append(dict(ident=ident,part=part,title=title,body=body.strip(),refs=refs))

def rich(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    def ref(m):
        r=m.group(1)
        return f'<super><link href="{html.escape(sources[r]["url"],quote=True)}" color="#526852">[{r}]</link></super>'
    return re.sub(r'\[(\d\d)\]',ref,text)

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

ART={
 'craft':('menu-scenes.png',(18,15,750,474)),
 'cocktails':('menu-scenes.png',(786,15,1518,474)),
 'mixedtea':('menu-scenes.png',(18,499,750,1001)),
 'cafemenu':('menu-scenes.png',(786,499,1518,1001)),
 'senses':('process-scenes.png',(20,18,756,497)),
 'origins':('process-scenes.png',(781,18,1516,497)),
 'rice':('process-scenes.png',(20,515,756,1001)),
 'barrels':('process-scenes.png',(781,515,1516,1001)),
}

class ChapterArt(Flowable):
    def __init__(self,key,height):
        Flowable.__init__(self);self.key=key;self.height=float(height)+17;self.width=CW
    def draw(self):
        filename,rect=ART[self.key];img=ROOT/'assets'/filename
        iw,ih=Image.open(img).size
        x0,y0,x1,y1=[v*s for v,s in zip(rect,(iw/1536,ih/1024,iw/1536,ih/1024))]
        h=self.height-17;w=h*(x1-x0)/(y1-y0);x=(CW-w)/2;y=17
        scale=w/(x1-x0);c=self.canv
        c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0)
        c.drawImage(str(img),x-x0*scale,y-(ih-y1)*scale,iw*scale,ih*scale)
        c.restoreState();c.setFillColor(GRAY);c.setFont(FONT,7)
        c.drawCentredString(CW/2,3,'阅读情境插画  具体分类与制作以正文资料为准')

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
            c.setFont(FONT,7.4);c.drawCentredString(x+21,15,extra)
        c.setFont(FONT,7);c.setFillColor(GRAY);c.drawCentredString(CW/2,0,'只示意组成关系  色块不表示标准配方比例')

def figure_region(c,key,x,y,w):
    # A PDF viewport into an unmodified generated sheet, not a raster edit.
    img=ROOT/'assets/illustrations.png'
    iw,ih=Image.open(img).size
    normalized={'cover':(22/1536,17/1024,751/1536,497/1024),
       'wine':(786/1536,16/1024,1515/1536,497/1024),
       'tea':(22/1536,521/1024,751/1536,1003/1024),
       'coffee':(787/1536,521/1024,1515/1536,1003/1024)}[key]
    x0,y0,x1,y1=[a*b for a,b in zip(normalized,(iw,ih,iw,ih))]
    scale=w/(x1-x0); h=(y1-y0)*scale
    c.saveState(); p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0)
    c.drawImage(str(img),x-x0*scale,y-(ih-y1)*scale,iw*scale,ih*scale)
    c.restoreState()
    return h

def blocks(body):
    lines=body.splitlines(); result=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('@art '):
            _,key,height=line.split();result.append(('flow',ChapterArt(key,height)));i+=1;continue
        if line.startswith('@composition '):
            result.append(('flow',CompositionSketch()));i+=1;continue
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
    else:
        ps.append(Paragraph('本页为原创阅读说明或自拟观察方法，无新增外部事实引用。',STYLES['small']))
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
        title=next((l[2:] for l in page['body'].splitlines() if l.startswith('# ')),page['title'])
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
    c.setFillColor(INK);c.setFont(FONT,10)
    c.drawString(M,119,'从原料与加工开始，读懂一杯饮料。')
    c.drawString(M,99,'短章阅读  当页资料  日常观察')
    c.setFillColor(GRAY);c.setFont(FONT,8)
    c.drawString(M,55,'图解修订版  2026年10月')
    c.drawString(M,39,'AI 辅助写作与插画  资料出处见各页及书末')

def contents(c):
    for chunk in [list(range(1,13)),list(range(13,21))+['A1','A2','A3']]:
        newpage(c);frame(c,'目录')
        c.setFillColor(black);c.setFont(FONT,19);c.drawString(M,H-69,'目录' if chunk[0]==1 else '目录 续')
        y=H-104;lastpart=None
        for v in chunk:
            ident=f'{v:02}' if isinstance(v,int) else v
            p=next(p for p in pages if p['ident']==ident)
            if p['part']!=lastpart:
                c.setFillColor(GRAY);c.setFont(FONT,9);c.drawString(M,y,p['part']);y-=25;lastpart=p['part']
            title=next(l[2:] for l in p['body'].splitlines() if l.startswith('# '))
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
    obj=Paragraph('AI 生成的阅读情境插画，不是历史复原、植物鉴定图或工艺操作图。',STYLES['small'])
    ww,hh=obj.wrap(CW,H);obj.drawOn(c,M,113-hh)

def bibliography(c):
    ordered=list(sources.values());y=0
    intro='首版资料检索于 2026 年 10 月 11 日，新增资料检索于 10 月 12 日。正文为原创改写与解释。行业材料用于工艺和术语，生产者配方用于展示其具体做法，不推广为全球标准；考古资料限定证据，自拟实验与类比另行注明。原文链接日后可能更新。'
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
    c.setTitle('杯中世界 酒 茶 咖啡的起源与风味');c.setAuthor('AI 辅助编写 个人兴趣读本')
    c.setSubject('饮品历史 工艺 风味与日常观察')
    cover(c);draw_content(c,pages[0],collect);contents(c)
    prev=None
    for page in pages[1:]:
        if page['ident']=='04' and prev!='04':opener(c,'wine','酒的世界','先问糖从哪里来，再沿着发酵、蒸馏与熟成认识主要酒类。')
        if page['ident']=='13' and prev!='13':opener(c,'tea','茶的世界','把一片叶子的加工，与它进入日常生活的历史放在一起。')
        if page['ident']=='16' and prev!='16':opener(c,'coffee','咖啡的世界','从果实中的种子，走到烘焙与冲煮；把“浓”拆成具体问题。')
        draw_content(c,page,collect);prev=page['ident']
    bibliography(c);c.save()
    return P

# Two passes populate table of contents without a pagination-dependent layout.
target=OUT/'杯中世界.pdf'
count=build(OUT/'first-pass.pdf')
count=build(target,collect=False)
(OUT/'first-pass.pdf').unlink()
(OUT/'layout-check.json').write_text(json.dumps(dict(total_pages=count,pages=diagnostics),ensure_ascii=False,indent=2))

allmd=['# 杯中世界\n\n酒 茶 咖啡的起源与风味\n\n个人兴趣读本 图解修订版\n']
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
    body=re.sub(r'@art (\w+) [\d.]+',lambda m:'（配图 '+m.group(1)+' 见 PDF 与写作工程中的图像资源）',body)
    body=body.replace('@composition coffee','| 成杯方向 | 组成关系 |\n| --- | --- |\n| 浓缩 | 咖啡基底 |\n| 美式 | 浓缩加水 |\n| 奶咖 | 浓缩加奶与相应奶泡 |\n\n仅示意组成，不表示标准比例。')
    allmd.append('\n---\n\n'+body+'\n\n本页资料：\n')
    for r in p['refs']:
        s=sources[r];allmd.append(f'- [{r}] {s["publisher"]}，《{s["title"]}》，{s["year"]}。[原文]({s["url"]})\n')
    if not p['refs']:allmd.append('本页为原创阅读说明或自拟观察方法。\n')
allmd.append('\n资料检索日期 2026年10月11日至12日。插画由 AI 生成；完整配图与当页排版见 PDF。\n')
(OUT/'杯中世界可编辑稿.md').write_text('\n'.join(allmd))
print(json.dumps(dict(pdf=str(target),pages=count,chapters=20,source_count=len(sources),body_pages=len(pages)),ensure_ascii=False))
