# SPDX-License-Identifier: MIT
"""Export already built pages into independent chapter PDFs and Markdown files."""
from pathlib import Path
from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
import re,json
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import white,HexColor

ROOT=Path(__file__).resolve().parent
PUBLICATION=json.loads((ROOT/'publication.json').read_text(encoding='utf-8'))
OUT=ROOT/'output'
DEST=OUT/'逐章阅读'
DEST.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('ChapterSans',str(ROOT/'assets/NotoSansSC-Regular.ttf')))
source=PdfReader(OUT/'杯中世界.pdf')
layout=json.loads((OUT/'layout-check.json').read_text())
groups=defaultdict(list)
for p in layout['pages']:groups[p['chapter']].append(p)
chunks=re.split(r'\n---\n',(OUT/'杯中世界可编辑稿.md').read_text())[1:]
assert len(chunks)==len(layout['pages'])
mdgroups=defaultdict(list)
for p,chunk in zip(layout['pages'],chunks):mdgroups[p['chapter']].append(chunk.strip())
manifest=[]
for ident,items in groups.items():
    raw=(ROOT/'chapters'/f'{ident}.md').read_text()
    match=re.search(r'^# (.+)$',raw,re.M)
    title=match.group(1) if match else '读前的话'
    filename=re.sub(r'\s+','',title)
    if ident=='00':filename='00-'+filename
    writer=PdfWriter()
    for local,item in enumerate(items,1):
        page=source.pages[item['page']-1]
        w=float(page.mediabox.width);h=float(page.mediabox.height)
        buff=BytesIO();c=canvas.Canvas(buff,pagesize=(w,h))
        c.setFillColor(white);c.rect(35,h-29,w-155,16,fill=1,stroke=0)
        c.setFillColor(HexColor('#626762'));c.setFont('ChapterSans',7.3)
        c.drawString(39,h-24,'杯中世界 · '+PUBLICATION['credit'])
        c.setFillColor(white);c.rect(35,9,w-70,20,fill=1,stroke=0)
        c.setFillColor(HexColor('#626762'));c.setFont('ChapterSans',7.2)
        c.drawCentredString(w/2,19,f'本章 {local} / {len(items)}　全书第 {item["page"]} 页 · '+PUBLICATION['content_license'])
        c.linkURL(PUBLICATION['content_license_url'],(w/2+45,14,w-35,27),relative=0,thickness=0)
        c.setFont('ChapterSans',6.2);c.drawCentredString(w/2,8,PUBLICATION['ai_disclosure'])
        c.save();buff.seek(0);page.merge_page(PdfReader(buff).pages[0])
        writer.add_page(page)
    writer.add_outline_item(title,0)
    writer.add_metadata({'/Title':title+' 杯中世界图解修订版','/Author':PUBLICATION['metadata_credit'],
                         '/Subject':PUBLICATION['ai_disclosure']+' '+PUBLICATION['content_license'],
                         '/Keywords':'YZ, 策划与整理, AI 生成, '+PUBLICATION['content_license']})
    pdfpath=DEST/(filename+'.pdf')
    with pdfpath.open('wb') as f:writer.write(f)
    chaptertext='\n\n---\n\n'.join(mdgroups[ident])
    credit='> '+PUBLICATION['credit']+'。'+PUBLICATION['ai_disclosure']+'\n>\n> 许可：['+PUBLICATION['content_license']+']('+PUBLICATION['content_license_url']+')；[作品出处]('+PUBLICATION['source_url']+')。分享或改编时保留署名与许可链接，并注明改动；仅对有权许可且依法受保护的部分适用，第三方材料除外。\n\n'
    if chaptertext.startswith('# '):
        heading,_,remainder=chaptertext.partition('\n')
        chaptertext=heading+'\n\n'+credit+remainder.lstrip()
    else:chaptertext='# '+title+'\n\n'+credit+chaptertext
    (DEST/(filename+'.md')).write_text(chaptertext+'\n')
    manifest.append(dict(id=ident,title=title,pdf=pdfpath.name,markdown=filename+'.md',pages=len(items),full_book_pages=[i['page'] for i in items]))
(DEST/'阅读说明.txt').write_text('杯中世界 图解修订版\n\n20 个正文章节、读前说明和 3 个附录分别提供独立 PDF 与可编辑 Markdown。每个章节从独立页开始，PDF 页脚同时标出本章页码与全书页码；当页原文引用链接保留。Markdown 中的图片位置对应 PDF 的章内插画，文字与表格完整。\n\n全书 PDF 另行提供，含插画扉页、可点击目录和参考资料总目。\n')
with (DEST/'阅读说明.txt').open('a') as f:
    f.write('\n'+PUBLICATION['credit']+'\n'+PUBLICATION['ai_disclosure']+PUBLICATION['role_description']+'\n\n'+PUBLICATION['attribution']+'\n\n'+PUBLICATION['rights_boundary']+'\n\n'+PUBLICATION['third_party_notice']+'\n完整条款见随包提供的 LICENSE、NOTICE.md、licenses/MIT.txt 和 assets/OFL.txt。\n')
(OUT/'chapter-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with ZipFile(OUT/'杯中世界逐章阅读.zip','w',compression=ZIP_DEFLATED,compresslevel=7) as z:
    for f in sorted(DEST.iterdir()):z.write(f,'逐章阅读/'+f.name)
    for rel in ['LICENSE','NOTICE.md','licenses/MIT.txt','assets/OFL.txt','publication.json']:
        z.write(ROOT/rel,rel)
print(json.dumps(dict(chapter_files=len(manifest),pdfs=len(list(DEST.glob('*.pdf'))),markdown_files=len(list(DEST.glob('*.md'))),archive=str(OUT/'杯中世界逐章阅读.zip')),ensure_ascii=False))
