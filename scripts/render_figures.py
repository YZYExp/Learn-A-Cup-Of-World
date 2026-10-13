"""Render checked teaching relationships as vector PDFs and portable PNGs.

AI sheets are displayed through PDF viewports; their original pixels are kept.
All labels, relationships and quantities are defined here or in figure-plan.json.
"""
from pathlib import Path
import json
import math
import sys

import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from illustration_data import LEAF_PANELS
DEST = ROOT / 'assets/figures'
FONT = 'FigureSans'
pdfmetrics.registerFont(TTFont(FONT, str(ROOT / 'assets/NotoSansSC-Regular.ttf')))
W, H = 720, 430
INK, GRAY = '#25332C', '#61685F'
GREEN, BROWN, BLUE = '#DCE9D8', '#E8D5BD', '#DDEAF2'
RED, CREAM, YELLOW = '#E4B8B0', '#F0E5CE', '#F4DC91'


def lines(value, width, size):
    result, current = [], ''
    for char in value:
        if char == '\n':
            result.append(current); current = ''; continue
        if current and pdfmetrics.stringWidth(current + char, FONT, size) > width:
            result.append(current); current = char
        else:
            current += char
    return result + ([current] if current else [])


def text(c, value, x, y, size=21, width=680, align='left', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(FONT, size)
    for index, line in enumerate(lines(value, width, size)):
        method = c.drawCentredString if align == 'center' else c.drawString
        method(x, y-index*size*1.35, line)


def box(c, x, y, w, h, value='', color=GREEN, size=21):
    c.setFillColor(HexColor(color)); c.setStrokeColor(HexColor('#9EAA9D'))
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)
    if value:
        ls = lines(value, w-18, size)
        text(c, value, x+w/2, y+h/2+(len(ls)-1)*size*.675-size*.35,
             size, w-18, 'center')


def arrow(c, x1, y1, x2, y2, color=GRAY, dashed=False):
    c.setStrokeColor(HexColor(color)); c.setFillColor(HexColor(color)); c.setLineWidth(2.5)
    c.setDash(5, 4) if dashed else c.setDash()
    c.line(x1, y1, x2, y2); c.setDash()
    angle = math.atan2(y2-y1, x2-x1)
    p = c.beginPath(); p.moveTo(x2, y2)
    for sign in (-1, 1):
        p.lineTo(x2-9*math.cos(angle)+sign*5*math.sin(angle),
                 y2-9*math.sin(angle)-sign*5*math.cos(angle))
    p.close(); c.drawPath(p, fill=1, stroke=0)


def cup(c, x, y, w, h, segments, total=None):
    total = total or sum(amount for amount, color in segments)
    cursor = y
    for amount, color in segments:
        sh = h*amount/total
        c.setFillColor(HexColor(color)); c.rect(x+3, cursor+3, w-6, max(0, sh-1), fill=1, stroke=0)
        cursor += sh
    c.setStrokeColor(HexColor(GRAY)); c.setLineWidth(2)
    c.line(x, y+h+12, x, y); c.line(x, y, x+w, y); c.line(x+w, y, x+w, y+h+12)


def numbered(c, number, x, y):
    c.setFillColor(HexColor('#526852')); c.circle(x, y, 21, fill=1, stroke=0)
    text(c, str(number), x, y-7, 21, 40, 'center', '#FFFFFF')


def render(c, f):
    mode = f['mode']
    if mode == 'lanes':
        for index, row in enumerate(f['rows']):
            top = 350-index*105
            text(c, row[0], 22, top, 21)
            for col, value in enumerate(row[1:]):
                x = 22+col*236
                box(c, x, top-74, 205, 57, value, (GREEN, BROWN, BLUE)[col], 20)
                if col < 2: arrow(c, x+210, top-46, x+230, top-46)
    elif mode in ('cards', 'chain', 'labels'):
        rows = f.get('cards', f.get('steps'))
        for i, row in enumerate(rows):
            x=22+i*236
            box(c, x, 110, 205, 210, '', (GREEN, BROWN, BLUE)[i])
            text(c, row[0], x+102, 264, 23, 183, 'center')
            text(c, row[1], x+102, 195, 21, 183, 'center')
            if mode=='chain' and i<2: arrow(c, x+208, 215, x+230, 215)
    elif mode == 'scene':
        panel = f['panel']; ix, iy = panel % 2, panel // 2
        # PDF clipping is a viewport, not an edit of the generated image.
        x0, y0, x1, y1 = (18+768*ix, 18+512*iy, 750+768*ix, 484+512*iy)
        x, y, w, h = 120, 87, 480, 290
        scale = w/(x1-x0)
        c.saveState(); p=c.beginPath(); p.rect(x,y,w,h); c.clipPath(p,stroke=0)
        c.drawImage(str(ROOT/'assets/counterexamples.png'), x-x0*scale,
                    y-(1024-y1)*scale, 1536*scale, 1024*scale)
        c.restoreState()
    elif mode == 'grape':
        for i,(dx,dy) in enumerate([(0,0),(25,0),(50,0),(12,-24),(37,-24),(25,-48)]):
            c.setFillColor(HexColor('#785779')); c.circle(333+dx,342+dy,16,fill=1,stroke=0)
        text(c,'深色葡萄',475,330,21,180)
        for i,(label,col) in enumerate([('先分开果汁与皮','#EAD899'),('较短皮接触','#DF9E9E'),('带皮进入发酵','#954B59')]):
            x=72+i*240
            arrow(c,360,277,x+42,236)
            text(c,label,x+42,208,20,220,'center')
            cup(c,x,78,84,90,[(1,col)])
            text(c,['白葡萄酒','桃红葡萄酒','红葡萄酒'][i],x+42,49,20,220,'center')
    elif mode == 'parallel':
        box(c,30,84,660,255,'','#F1F4EF')
        text(c,'同一酒醪',360,309,24,600,'center')
        for x,label in [(53,'米中淀粉'),(279,'可利用的糖'),(505,'酒精与\n二氧化碳')]:
            box(c,x,134,160,72,label,GREEN)
        arrow(c,217,170,274,170); arrow(c,443,170,500,170)
        box(c,181,235,153,47,'麴提供的酶',BROWN,20)
        box(c,410,235,148,47,'酵母',BROWN,20)
        arrow(c,257,229,247,196); arrow(c,485,229,472,196)
    elif mode == 'whisky':
        box(c,28,124,364,225,'',GREEN)
        text(c,'一家酒厂',210,315,25,330,'center')
        for i in range(3):
            x=69+i*104
            c.setFillColor(HexColor(BROWN));c.setStrokeColor(HexColor('#8C704D'))
            c.roundRect(x,170,72,90,18,fill=1,stroke=1)
            c.line(x+6,194,x+66,194);c.line(x+6,236,x+66,236)
            text(c,chr(65+i),x+36,142,20,70,'center')
        box(c,427,210,265,115,'8 年 + 12 年',BROWN,24)
        arrow(c,558,199,558,157)
        box(c,427,82,265,68,'年龄声明：8 年',BLUE,24)
    elif mode == 'recipes':
        recipes=[('Negroni',[(30,'金酒',BROWN),(30,'Campari',RED),(30,'甜红味美思',GREEN)]),
                 ('Dry Martini',[(60,'金酒',BROWN),(10,'干味美思',GREEN)]),
                 ('Margarita',[(50,'龙舌兰酒',BROWN),(20,'橙味利口酒','#D6BA91'),(15,'青柠汁',BLUE)])]
        for i,(name,parts) in enumerate(recipes):
            y=291-i*112; text(c,name,25,y+53,23)
            x=25; total=sum(p[0] for p in parts)
            for amount,label,col in parts:
                w=660*amount/total
                box(c,x,y,w-3,43,f'{amount} ml',col,21)
                text(c,label,x+w/2,y-24,19,w-8,'center');x+=w
    elif mode == 'dilution':
        cup(c,120,99,135,180,[(16,BROWN),(24,BLUE)],80)
        cup(c,465,99,135,180,[(16,BROWN),(64,BLUE)],80)
        text(c,'40 ml · 40% ABV',186,320,25,310,'center')
        text(c,'约 80 ml · 20% ABV',532,320,25,340,'center')
        arrow(c,284,224,430,224)
        text(c,'补水 40 ml',358,254,21,175,'center')
        text(c,'纯酒精 16 ml',186,62,23,300,'center')
        text(c,'纯酒精 16 ml',532,62,23,335,'center')
    elif mode == 'experiment':
        for i,t in enumerate([1,2,3]):
            x=104+i*235
            cup(c,x,175,75,95,[(1,'#D0BA77')])
            text(c,chr(65+i)+f'  {t} 分钟',x+37,315,25,190,'center')
    elif mode == 'teacups':
        for i,(name,amount,col,label) in enumerate([('奶茶',50,CREAM,'牛奶 50 ml'),('柑橘茶',5,YELLOW,'柑橘汁 5 ml'),('气泡茶',50,BLUE,'气泡水 50 ml')]):
            x=95+i*235
            text(c,name,x+47,337,25,210,'center')
            cup(c,x,122,95,170,[(100,GREEN),(amount,col)],150)
            text(c,'茶汤 100 ml',x+47,84,21,218,'center')
            text(c,label,x+47,53,21,218,'center')
    elif mode == 'seed':
        c.setFillColor(HexColor('#C96D63'));c.ellipse(38,164,209,329,fill=1,stroke=0)
        c.setFillColor(HexColor(CREAM));c.ellipse(54,180,193,313,fill=1,stroke=0)
        c.setFillColor(HexColor('#A4B887'))
        c.ellipse(78,206,120,281,fill=1,stroke=0);c.ellipse(127,206,169,281,fill=1,stroke=0)
        text(c,'咖啡果实',125,126,20,230,'center')
        for x,col,label in [(290,'#A4B887','生豆'),(465,'#79523E','烘焙豆')]:
            c.setFillColor(HexColor(col));c.ellipse(x,222,x+73,284,fill=1,stroke=0)
            c.setStrokeColor(HexColor('#EBE3D2'));c.line(x+34,232,x+40,274)
            text(c,label,x+36,186,23,130,'center')
        arrow(c,219,250,275,250);arrow(c,378,250,448,250);arrow(c,554,250,596,250)
        cup(c,619,216,69,68,[(1,'#79523E')]);text(c,'冲煮',653,186,23,120,'center')
        text(c,'处理与干燥',253,89,21,200,'center');text(c,'烘焙',422,89,21,180,'center')
    elif mode == 'axes':
        arrow(c,125,82,665,82);arrow(c,125,82,125,341)
        text(c,'杯中浓度：较高',126,362,22,400)
        text(c,'较低',38,93,20,80)
        text(c,'萃取率：较低 → 较高',406,45,22,540,'center')
        c.setFillColor(HexColor('#526852'));c.circle(415,280,8,fill=1,stroke=0)
        arrow(c,415,263,415,141,'#537893')
        text(c,'补水',450,205,20,240)
    elif mode == 'alcoholbars':
        for i,(name,amount,col) in enumerate([('啤酒 330 ml · 5%',13.0185,GREEN),('葡萄酒 150 ml · 12%',14.202,RED),('烈酒 30 ml · 40%',9.468,BROWN)]):
            y=279-i*102
            text(c,name,25,y+54,24)
            box(c,25,y,amount/15*565,39,'',col)
            text(c,f'{amount:.1f} 克',25+amount/15*565+12,y+10,23,120)
    else:
        raise ValueError('Unknown figure mode: '+mode)


def main():
    DEST.mkdir(exist_ok=True)
    scratch=ROOT/'work/figure-render';scratch.mkdir(parents=True,exist_ok=True)
    figures=json.loads((ROOT/'assets/figure-plan.json').read_text())
    assert len({f['id'] for f in figures})==len(figures)
    for f in figures:
        path=(scratch if f['mode']=='scene' else DEST)/(f['id']+'.pdf')
        c=canvas.Canvas(str(path),pagesize=(W,H),invariant=1)
        c.setTitle('图 '+f['id']+' '+f['title'])
        render(c,f)
        c.save()
        with fitz.open(path) as doc:
            if f['mode']=='scene':
                bounds=fitz.Rect(120,H-377,600,H-87)
            else:
                bounds=fitz.Rect()
                for _, rect, *_ in doc[0].get_bboxlog():
                    bounds |= fitz.Rect(rect)
                bounds=fitz.Rect(bounds.x0-12,bounds.y0-12,bounds.x1+12,bounds.y1+12)&doc[0].rect
            # Recompose this freshly drawn PDF at its content bounds.
            # Captions remain editable Markdown; no raster text is removed.
            fitted=fitz.open();page=fitted.new_page(width=bounds.width,height=bounds.height)
            page.show_pdf_page(page.rect,doc,0,clip=bounds)
            compact=scratch/(f['id']+'-compact.pdf');fitted.save(compact);fitted.close()
        if f['mode']!='scene':
            path.write_bytes(compact.read_bytes())
        with fitz.open(compact) as doc:
            zoom=1.5 if f['mode']=='scene' else 3
            doc[0].get_pixmap(matrix=fitz.Matrix(zoom,zoom)).save(DEST/(f['id']+'.png'))
    scenes=json.loads((ROOT/'assets/scene-catalog.json').read_text())
    views={key:(s['file'],s['rect']) for key,s in scenes.items()}
    views.update({'leaf-'+key:(filename,rect) for key,(filename,rect,_) in LEAF_PANELS.items()})
    for key, (filename,rect) in views.items():
        x0,y0,x1,y1=rect; width=720; scale=width/(x1-x0)
        height=(y1-y0)*scale
        path=scratch/('scene-'+key+'.pdf')
        c=canvas.Canvas(str(path),pagesize=(width,height))
        c.drawImage(str(ROOT/'assets'/filename),-x0*scale,
                    -(1024-y1)*scale,1536*scale,1024*scale)
        c.save()
        with fitz.open(path) as doc:
            filename=(key if key.startswith('leaf-') else 'scene-'+key)+'.png'
            doc[0].get_pixmap().save(DEST/filename)
    print(f'Rendered {len(figures)} teaching figures (PDF + PNG).')


if __name__=='__main__':
    main()
