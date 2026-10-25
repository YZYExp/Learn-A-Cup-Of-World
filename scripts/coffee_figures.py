# SPDX-License-Identifier: MIT
"""Reproducible teaching diagrams for the expanded coffee chapters.

Run directly, or call render_coffee() from the shared figure renderer.
PDF masters are build intermediates beside their portable PNG counterparts.
"""
from pathlib import Path
import math

import fitz
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/figures'
FONT = 'CoffeeFigureSans'
INK, GRAY = '#25332C', '#61685F'
GREEN, BROWN, BLUE = '#DCE9D8', '#E8D5BD', '#DDEAF2'
CREAM = '#F0E5CE'


def text(c, value, x, y, size=20, align='center', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(FONT, size)
    for n, line in enumerate(value.split('\n')):
        method = c.drawCentredString if align == 'center' else c.drawString
        method(x, y - n * size * 1.35, line)


def stroke(c, color=GRAY, width=2):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width)


def box(c, x, y, w, h, fill=GREEN):
    c.setFillColor(HexColor(fill)); stroke(c, '#9EAA9D', 1)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)


def arrow(c, x1, y1, x2, y2, color=GRAY):
    stroke(c, color, 2); c.setFillColor(HexColor(color))
    c.line(x1, y1, x2, y2)
    a = math.atan2(y2-y1, x2-x1)
    p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2-9*math.cos(a)+4*math.sin(a), y2-9*math.sin(a)-4*math.cos(a))
    p.lineTo(x2-9*math.cos(a)-4*math.sin(a), y2-9*math.sin(a)+4*math.cos(a))
    p.close(); c.drawPath(p, fill=1, stroke=0)


def bean(c, x, y, size=42, color='#A4B887', crack=False):
    c.saveState(); c.translate(x, y); c.rotate(-20)
    c.setFillColor(HexColor(color)); stroke(c, '#8C704D', 1.2)
    c.ellipse(-size*.38, -size*.5, size*.38, size*.5, fill=1, stroke=1)
    stroke(c, CREAM, 2)
    p = c.beginPath(); p.moveTo(0, -size*.4)
    p.curveTo(-size*.17, -size*.1, size*.15, size*.1, 0, size*.4)
    c.drawPath(p, stroke=1)
    if crack:
        c.line(-size*.05, size*.15, -size*.23, size*.27)
        c.line(size*.02, -size*.13, size*.23, -size*.2)
    c.restoreState()


def cup(c, x, y, w=100, h=110, fill=BROWN, level=.65):
    c.setFillColor(HexColor(fill))
    c.rect(x+4, y+4, w-8, (h-8)*level, fill=1, stroke=0)
    stroke(c); c.line(x, y+h, x, y); c.line(x, y, x+w, y)
    c.line(x+w, y, x+w, y+h)


def dripper(c, cx, y, wet=False, grounds=True, filled=False):
    """Fixed structure: dripper above a server, y is server baseline."""
    cup(c, cx-43, y, 86, 60, '#9D7657', .6 if filled else (.12 if grounds else 0))
    c.setFillColor(HexColor('#F5F2E9')); stroke(c)
    p=c.beginPath(); p.moveTo(cx-58,y+139); p.lineTo(cx+58,y+139)
    p.lineTo(cx+19,y+80); p.lineTo(cx-19,y+80); p.close()
    c.drawPath(p, fill=1, stroke=1)
    stroke(c, '#A9B9A1', 1.2)
    for dx in (-25,0,25):
        c.line(cx+dx,y+128,cx+dx*.35,y+88)
    if grounds:
        c.setFillColor(HexColor('#8C6749'))
        p=c.beginPath(); p.moveTo(cx-35,y+112); p.lineTo(cx+35,y+112)
        p.lineTo(cx+19,y+83); p.lineTo(cx-19,y+83); p.close()
        c.drawPath(p,fill=1,stroke=0)
        if wet:
            c.setFillColor(HexColor('#B18A62'))
            c.ellipse(cx-34,y+107,cx+34,y+119,fill=1,stroke=0)
    if filled:
        for yy in (75,66):
            c.setFillColor(HexColor('#9D7657')); c.circle(cx, y+yy, 2.5,fill=1,stroke=0)


def numbered(c, n, x, y):
    c.setFillColor(HexColor('#526852')); c.circle(x,y,15,fill=1,stroke=0)
    text(c,str(n),x,y-6,18,color='#FFFFFF')


def label_axes(c):
    box(c, 20, 172, 330, 220)
    box(c, 370, 172, 330, 220, BLUE)
    text(c, '物种：C. arabica',185,357,24)
    text(c, '阿拉比卡',185,322,22)
    arrow(c,185,305,185,273)
    text(c, '栽培品种举例',185,245,20)
    text(c, 'Typica · Bourbon · Gesha',185,205,19)
    text(c, '物种：C. canephora',535,357,23)
    text(c, '卡内弗拉',535,322,22)
    arrow(c,535,305,535,273)
    text(c, '罗布斯塔是常见生产称呼',535,245,20)
    text(c, '物种内仍有遗传与栽培差异',535,205,19)
    text(c,'一袋豆还可同时说明：',25,127,22,'left')
    for x,title,detail in ((20,'产地','国家／地区／庄园'),(256,'处理','水洗／日晒／蜜处理'),(492,'烘焙','日期／程度／用途')):
        box(c,x,24,208,77,CREAM)
        text(c,title,x+104,72,22)
        text(c,detail,x+104,42,17)


def roasting(c):
    positions=(88,267,446,625)
    data=(('生豆','#A4B887','尚未烘焙'),('脱水与转黄','#C5B77D','水分减少'),('褐变','#A1774D','香气反应发展'),('一爆及后续','#6E4C38','结构与风味继续变化'))
    for i,(x,(name,color,detail)) in enumerate(zip(positions,data)):
        text(c,name,x,359,22)
        bean(c,x,265,91 if i==3 else 76,color,i==3)
        text(c,detail,x,171,18)
        if i<3: arrow(c,x+54,265,positions[i+1]-53,265)
        if i==1:
            for dx in (-22,0,22):
                stroke(c,'#9AA9AD',1.5)
                c.bezier(x+dx,319,x+dx-8,330,x+dx+8,337,x+dx,347)
        if i==3:
            for dx,dy in ((-60,20),(58,12),(45,62)):
                stroke(c,'#A77C54',2)
                c.line(x+dx,265+dy,x+dx*1.13,265+dy*1.13)
    box(c,28,44,664,84,CREAM)
    text(c,'阶段会重叠；箭头不表示固定时间或温度',360,98,22)
    text(c,'是否继续加深烘焙，取决于原料、设备与风味目标',360,66,19)


def pour_over(c):
    # Read left-to-right on the first row, then left-to-right below.
    for n,cx,y in ((1,185,300),(2,535,300),(3,185,45),(4,535,45)):
        numbered(c,n,cx-142,y+168)
        dripper(c,cx,y,wet=n>1,grounds=n>1,filled=n>2)
        if n==1:
            text(c,'润湿滤纸，倒掉润纸水',cx,y+166,19)
            text(c,'加入 15 g 咖啡粉',cx,y-29,19)
        else:
            title={2:'累计注水 45 g',3:'累计注水 150 g',4:'累计注水 240 g'}[n]
            text(c,title,cx,y+166,21)
            arrow(c,cx,y+154,cx,y+128,'#537893')
            text(c,{2:'开始计时，润湿粉层并闷蒸',3:'继续注水；不是另加 150 g',4:'完成注水，等待滴滤结束'}[n],cx,y-29,18)
    arrow(c,319,390,385,390)
    arrow(c,319,135,385,135)
    text(c,'示例配方：所有累计量均从首次注水算起',360,552,20)


def extraction(c):
    # Left and right cups contain the same mass of dissolved solids.
    for x,liquid,tds,level in ((152,'200 g','1.35%',.65),(568,'250 g','1.08%',.85)):
        cup(c,x-57,164,114,143,'#A57A56',level)
        for dx,dy in ((-25,20),(0,45),(25,70)):
            c.setFillColor(HexColor('#526852'));c.circle(x+dx,168+dy,5,fill=1,stroke=0)
        text(c,liquid+' 咖啡液',x,333,23)
        text(c,'浓度 '+tds,x,128,23)
        text(c,'溶解固形物 2.7 g',x,93,21)
    arrow(c,233,246,487,246,'#537893')
    text(c,'分离粉渣后',360,302,21)
    text(c,'补水 50 g',360,269,23,color='#537893')
    text(c,'两杯都来自同一份 15 g 干粉',360,385,24)
    box(c,42,22,636,45,GREEN)
    text(c,'萃取率均为 2.7 ÷ 15 × 100% = 18%',360,36,22)


def iced_pour(c):
    dripper(c,151,174,wet=True,filled=True)
    arrow(c,151,342,151,305,'#537893')
    text(c,'热水 150 g',151,367,24)
    text(c,'咖啡粉 15 g',151,135,22)
    # Ice is placed in a server; its mass belongs to the recipe water budget.
    cup(c,501,188,135,135,'#B7CFDB',.48)
    for x,y in ((518,209),(551,230),(587,206)):
        c.saveState();c.translate(x,y);c.rotate(15)
        box(c,-12,-12,24,24,BLUE);c.restoreState()
    text(c,'预放冰 90 g',568,367,24)
    text(c,'冰在分享壶中接住热咖啡',568,135,19)
    arrow(c,248,249,474,249)
    text(c,'热提取后降温',360,281,21)
    box(c,26,27,668,68,CREAM)
    text(c,'配方总水：150 + 90 = 240 g',360,65,24)
    text(c,'粉会留水；成杯量不等于 240 g，冰也未必全部融化',360,37,18)


FIGURES = {
    '16-3': (label_axes, 430),
    '17-5': (roasting, 430),
    '18-7': (pour_over, 580),
    '18-8': (extraction, 430),
    '18-9': (iced_pour, 430),
}


def render_coffee_figure(c, figure):
    """Draw one figure; return its page height for standalone callers."""
    pdfmetrics.registerFont(TTFont(FONT,str(ROOT/'assets/NotoSansSC-Regular.ttf')))
    draw,height=FIGURES[figure['id']]
    draw(c)
    return height


def render_coffee():
    DEST.mkdir(parents=True,exist_ok=True)
    for figure_id,(draw,height) in FIGURES.items():
        path=DEST/(figure_id+'.pdf')
        c=canvas.Canvas(str(path),pagesize=(720,height),invariant=1)
        c.setTitle('Coffee teaching diagram '+figure_id)
        render_coffee_figure(c, {'id': figure_id});c.save()
        with fitz.open(path) as doc:
            doc[0].get_pixmap(matrix=fitz.Matrix(3,3)).save(DEST/(figure_id+'.png'))
    print(f'Rendered {len(FIGURES)} coffee teaching figures (PDF + PNG).')


if __name__ == '__main__':
    render_coffee()
