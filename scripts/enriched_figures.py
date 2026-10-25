# SPDX-License-Identifier: MIT
"""Object and process drawings for the expanded illustrated reader."""
from reportlab.lib.colors import HexColor


def render_enriched(c, figure, helpers):
    text, box, arrow, cup = (helpers[k] for k in ('text', 'box', 'arrow', 'cup'))
    green, brown, blue = '#DCE9D8', '#E8D5BD', '#DDEAF2'
    mode = figure['mode']

    def stroke(color='#61685F', width=2):
        c.setStrokeColor(HexColor(color)); c.setLineWidth(width)

    def fill(color):
        c.setFillColor(HexColor(color))

    def vessel(x, y, w, h, color=blue):
        fill(color); stroke()
        c.roundRect(x, y, w, h, 8, fill=1, stroke=1)

    if mode == 'conversion':
        for row, title in enumerate(('发酵中的转化', '冲泡中的提取')):
            y = 285 - row * 200
            text(c, title, 22, y + 102, 25)
            vessel(50, y - 20, 135, 92, green)
            vessel(465, y - 20, 135, 92, blue)
            for i in range(5):
                fill('#8C704D'); c.circle(72 + i * 22, y + 24, 7, fill=1, stroke=0)
            arrow(c, 200, y + 27, 440, y + 27)
            text(c, ('酵母参与', '水接触材料')[row], 320, y + 57, 22, 225, 'center')
            text(c, ('糖', '茶叶或咖啡粉')[row], 117, y - 54, 23, 210, 'center')
            text(c, ('酒精与二氧化碳', '水中溶出的成分')[row], 535, y - 54, 23, 295, 'center')
            if row == 0:
                for i in range(4):
                    fill('#A9C0A0'); c.circle(494 + i * 24, y + 21, 7, fill=1, stroke=0)
                for x, dy in ((493, 70), (536, 88), (573, 64)):
                    stroke('#78966E'); c.circle(x, y + dy, 7, fill=0, stroke=1)
            else:
                for i in range(5):
                    fill('#8C704D'); c.circle(491 + i * 22, y + 24, 7, fill=1, stroke=0)
        return True

    if mode == 'evidence_timeline':
        stroke('#526852', 3); c.line(78, 290, 638, 290)
        for x, date, place, evidence, color in (
            (100, '约 1.3 万年前', 'Raqefet 洞穴', '石臼遗存\n使用痕迹与实验', green),
            (360, '约公元前第七千纪', '河南贾湖', '陶器残留\n混合发酵饮品解释', brown),
            (620, '约公元前\n6000—5800 年', '格鲁吉亚', '化学与考古证据\n葡萄酿造线索', blue),
        ):
            fill('#526852'); c.circle(x, 290, 7, fill=1, stroke=0)
            text(c, date, x, 348, 18, 182, 'center')
            stroke(); c.line(x, 280, x, 248)
            box(c, x - 98, 103, 196, 138, '', color)
            text(c, place, x, 208, 22, 181, 'center')
            text(c, evidence, x, 163, 19, 180, 'center')
        return True

    if mode == 'distillation':
        vessel(35, 92, 165, 148, brown)
        cup(c, 63, 114, 107, 66, [(1, '#CAB67B')])
        text(c, '含酒精原料', 118, 64, 22, 204, 'center')
        text(c, '加热与\n汽化', 22, 282, 21, 90)
        arrow(c, 118, 183, 118, 235)
        stroke('#526852', 4); c.line(118, 240, 118, 320); c.line(118, 320, 337, 320)
        arrow(c, 218, 320, 304, 320, '#526852')
        text(c, '蒸气', 238, 354, 22, 150, 'center')
        vessel(338, 151, 196, 176)
        stroke('#A77C54', 4)
        points = [(337, 320), (372, 294), (498, 276), (372, 254), (498, 232), (372, 210), (498, 188), (547, 160)]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            c.line(x1, y1, x2, y2)
        text(c, '冷凝', 435, 355, 23, 170, 'center')
        text(c, '冷却区', 435, 117, 21, 180, 'center')
        arrow(c, 550, 158, 595, 158, '#A77C54')
        cup(c, 600, 92, 80, 85, [(1, '#DFDBC7')])
        text(c, '收集蒸馏液', 635, 64, 21, 174, 'center')
        return True

    if mode == 'cocktail_actions':
        rows = [
            ('代基里', ['量取；使糖溶解', '加冰摇和', '过滤入杯']),
            ('干马天尼', ['量取；加入冰', '搅拌', '过滤入杯']),
            ('尼格罗尼', ['饮用杯中加冰', '量取材料', '杯中轻搅']),
        ]
        for row, (name, steps) in enumerate(rows):
            y = 328 - row * 116
            text(c, name, 22, y + 40, 23)
            for i, label in enumerate(steps):
                x = 22 + 235 * i
                box(c, x, y - 35, 202, 54, label, (green, brown, blue)[i], 21)
                if i < 2:
                    arrow(c, x + 207, y - 7, x + 230, y - 7)
        return True

    if mode == 'tea_adjustment':
        for i, (question, action) in enumerate((
            ('太浓或太淡', '先改茶水比例'),
            ('偏苦或偏涩', '先改时间'),
            ('前后差异大', '先记展开与续泡'),
        )):
            x = 22 + i * 236
            box(c, x, 250, 205, 66, question, green, 23)
            arrow(c, x + 102, 241, x + 102, 194)
            box(c, x, 111, 205, 72, action, blue, 22)
        return True

    if mode == 'tea_routes':
        rows = [
            ('绿茶', ['杀青', '整形', '干燥']),
            ('白茶', ['萎凋', '干燥']),
            ('黄茶', ['杀青', '含闷黄的后续工序']),
            ('乌龙', ['萎凋与做青', '杀青与整形', '干燥等']),
            ('红茶', ['萎凋与揉切', '氧化', '加热干燥']),
            ('黑茶', ['已有初制加工', '微生物相关转变', '后续加工']),
        ]
        for row, (name, steps) in enumerate(rows):
            y = 360 - row * 64
            text(c, name, 18, y + 14, 23, 83)
            widths = [183] * 3 if len(steps) == 3 else [183, 394]
            x = 110
            for i, (label, width) in enumerate(zip(steps, widths)):
                box(c, x, y, width, 43, label, (green, brown, blue)[i], 21)
                if i < len(steps) - 1:
                    arrow(c, x + width + 3, y + 21, x + width + 22, y + 21)
                x += width + 27
        return True

    if mode == 'puerh_branch':
        box(c, 211, 314, 298, 62, '云南大叶种晒青原料', green, 24)
        for x, title, step in ((190, '生茶路线', '不经熟茶式人工渥堆'), (530, '熟茶路线', '经过人工渥堆')):
            arrow(c, 360, 310, x, 250)
            text(c, title, x, 261, 25, 260, 'center')
            box(c, x - 151, 167, 302, 61, step, brown, 23)
            arrow(c, x, 161, x, 125)
            box(c, x - 151, 51, 302, 65, '后续加工与成品形态', blue, 22)
        return True

    if mode == 'coffee_layers':
        # An idealized cross section; layer widths do not represent real thickness.
        cx, cy = 257, 215
        for rx, ry, color in ((174, 165, '#C96D63'), (150, 141, '#E8BA8F'), (119, 111, '#EAD899'), (97, 88, '#F0E5CE')):
            fill(color); stroke('#937B61', 1.5)
            c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, fill=1, stroke=1)
        fill('#A4B887')
        for x in (203, 274):
            c.ellipse(x - 29, 155, x + 29, 274, fill=1, stroke=0)
        stroke('#71845E', 2)
        c.line(205, 170, 205, 258); c.line(272, 170, 272, 258)
        anchors = [(399, 307), (366, 275), (367, 229), (339, 195), (278, 170)]
        names = ['果皮', '果肉', '黏液层', '羊皮层', '种子']
        for i, ((x, y), label) in enumerate(zip(anchors, names)):
            ty = 359 - i * 68
            stroke(); c.line(x, y, 454, ty); c.line(454, ty, 495, ty)
            text(c, label, 511, ty - 7, 24, 174)
        return True

    if mode == 'brewing_routes':
        # The blue arrows show water/coffee flow, not pressure or calibrated rate.
        for col, label in enumerate(('滤泡', '浸泡后分离', '意式浓缩')):
            x = 122 + col * 237
            text(c, label, x, 370, 24, 230, 'center')
            if col == 0:
                fill('#F0E5CE'); stroke()
                p = c.beginPath(); p.moveTo(x - 68, 273); p.lineTo(x + 68, 273); p.lineTo(x, 180); p.close()
                c.drawPath(p, fill=1, stroke=1)
                fill('#8C704D'); c.ellipse(x - 45, 244, x + 45, 265, fill=1, stroke=0)
                arrow(c, x, 328, x, 282, '#7293A8')
                arrow(c, x, 176, x, 129, '#7293A8')
                cup(c, x - 41, 47, 82, 69, [(1, '#CAB67B')])
            elif col == 1:
                vessel(x - 71, 166, 142, 150)
                for i in range(14):
                    fill('#8C704D'); c.circle(x - 48 + (i % 5) * 23, 183 + (i // 5) * 38, 6, fill=1, stroke=0)
                arrow(c, x, 158, x, 129, '#7293A8')
                stroke(); c.line(x - 55, 119, x + 55, 119)
                text(c, '滤网等分离', x, 82, 20, 216, 'center')
                text(c, '留下咖啡液', x, 39, 20, 216, 'center')
            else:
                vessel(x - 70, 183, 140, 75, brown)
                text(c, '咖啡粉层', x, 213, 21, 130, 'center')
                arrow(c, x, 327, x, 270, '#7293A8')
                text(c, '压力参与', x, 346, 20, 180, 'center')
                arrow(c, x, 175, x, 129, '#7293A8')
                cup(c, x - 37, 47, 74, 69, [(1, '#8C704D')])
        return True

    if mode == 'learning_cycle':
        for i, (title, task) in enumerate((('第一周', '描述一杯'), ('第二周', '查一个加工词'), ('第三周', '只改一项条件'), ('第四周', '回看记录'))):
            position = (0, 1, 3, 2)[i]
            x, y = 30 + (position % 2) * 360, 233 - (position // 2) * 189
            box(c, x, y, 300, 145, '', (green, brown, blue, '#F0E5CE')[i])
            text(c, title, x + 150, y + 99, 24, 270, 'center')
            text(c, task, x + 150, y + 48, 25, 270, 'center')
        arrow(c, 335, 302, 385, 302)
        arrow(c, 540, 227, 540, 195)
        # Week three is the lower right and week four is the lower left.
        arrow(c, 385, 113, 335, 113)
        return True
    return False
