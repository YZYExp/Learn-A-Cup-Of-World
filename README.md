# 杯中世界

个人兴趣读本，主题为酒、茶、咖啡的起源、发展、制作与风味。

**策划与整理：YZ**。正文由 AI 编写，插画由 AI 生成；YZ 负责选题、需求设定与成稿整理。

## 开放许可

书稿、项目自制图表与 AI 插画采用 **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)**，允许分享、改编及商用，须保留署名、作品出处与许可链接并注明改动。构建与导出脚本采用 **[MIT](licenses/MIT.txt)**；字体沿用 **[SIL OFL 1.1](assets/OFL.txt)**。

许可仅适用于 YZ 有权许可且依法受保护的部分，不会为不受保护的纯 AI 内容额外产生著作权；第三方引用及链接目标不纳入本项目授权。完整范围、推荐署名与权利说明见 **[NOTICE.md](NOTICE.md)**；内容许可全文见 **[LICENSE](LICENSE)**。

## 成书原则

- 以短章连接历史、工艺与日常体验；不作品牌排名、价格推荐或资格考试教材。
- 酒类占主要篇幅，茶与咖啡各有完整入门章节，并通过风味、加工与文化形成共同线索。
- 考古证据与传说分开，现代商品类别不倒推到史前饮品。
- 文中资料编号对应当页页下注；页下注列机构、题名或短题名、可点击原文链接；书末列完整目录与检索日期。
- 自拟实验、类比与判断明确注明，不包装为引用来源的结论。
- AI 插画用于阅读情境与典型外观示意；精确工艺、组成与数量关系由本书绘制，并附图例。

## 结构

1. 共同基础：三类饮品的相似与差异、感官、早期历史。
2. 酒：啤酒、葡萄酒、气泡与加强酒、黄酒与清酒、白酒、威士忌、白兰地与朗姆、金酒伏特加龙舌兰、调饮。
3. 茶：历史、六大茶类、冲泡。
4. 咖啡：历史与品种、处理与烘焙、冲煮。
5. 带回日常：储存、标签与预算、饮用边界、个人笔记。

## 文件

`chapters/` 为按章拆分的可编辑稿件；`research/sources.json` 为参考资料；`build_book.py` 为全书排版程序；`export_chapters.py` 导出独立章节；`assets/` 为插画和字体；`output/` 为成品。

Git 按规划、正文、插画排版、校订交付分阶段提交。远端仓库：[Learn-A-Cup-Of-World](https://github.com/YZYExp/Learn-A-Cup-Of-World)。

## 重建

使用 Python 3.12，依赖见 `requirements.txt`。在项目目录运行 `python build_book.py`。PDF 为 A5 阅读开本，字体嵌入，页码连续，目录与书签可导航。修改 `assets/figure-plan.json` 或绘图程序后，先运行 `python scripts/render_figures.py` 重绘教学图；原始 AI 图像保留不变。

之后运行 `python export_chapters.py`，得到 24 组独立 PDF 与 Markdown 以及逐章阅读压缩包。20 章正文之外的读前说明和 3 个附录也单独成文件；每章 PDF 页脚标示本章页码与全书页码。

## 完整首版

2026年10月11日编写任务完成：57 页、20 章、约 1.8 万汉字、50 项资料。正文各章两页，另有读前说明、插画扉页、三页附录和书末参考资料。源码包保留完整 Git 历史、分章稿件、配图、字体许可与排版程序。

`research/editorial-check.md` 记录内容与版面校订；生成后 `output/layout-check.json` 记录逐页引用与空间检查。最终阅读版和整合的可编辑 Markdown 稿由排版程序生成。字体文件由 Google Fonts 的 Noto Sans SC 变体派生，许可见 `assets/OFL.txt`。

## 图解修订版

2026年10月12日根据阅读反馈修订：81 页，正文与附录约 2.4 万汉字，75 项参考资料。精酿、调酒、调茶和咖啡菜单分别扩展；新增 8 幅章内插画，连同原封面和分部页共有 12 个插画使用位置。正文增加结构与配方表，并将完整章节分别导出为 PDF 和 Markdown。

修订在 `revision-illustrated` 分支进行，保留首版提交和修订提交。阅读版仍采用当页引用；表格的自拟分组、经典配方来源及插画使用边界均在正文注明。

## 直接阅读与历史

- [全书 PDF](books/杯中世界.pdf)
- [可编辑阅读稿](books/杯中世界可编辑稿.md)
- [24 份独立章节阅读稿](books/逐章阅读/)
- [逐章 PDF、Markdown 与配图阅读包](books/杯中世界逐章阅读.zip)
- [原始 Git 历史与恢复方法](history/README.md)

克隆后先运行 `python -m pip install -r requirements.txt`，再执行上述重建命令。仓库包含重建所需字体及字体许可。

当前 GitHub 阅读 PDF 保留正文、引用链接和导航，使用压缩的阅读插画；原始插画保留在工程中。独立章节 PDF 可用 `export_chapters.py` 重建。

2026年10月12日补充署名与开放许可：封面采用“策划与整理：YZ”，新增独立的署名与许可页，并同步全书与章节 PDF 的元数据、Markdown 和阅读包。新增一页后全书为 82 页，正文内容和 24 组章节结构保持原有编排。

原始 7 次写作提交已完整恢复到 `original-revision-illustrated` 分支，原始首版保留在 `original-main` 分支；原提交编号、作者、日期与父子关系不变。详见历史说明。

## 图例增补版（2026年10月12日）

与最新 `main` 的署名许可页及茶类扩展合并后，全书现为 120 页。新增 24 幅教学图，分布于全部 20 个正文章节；原有 12 处情境插画补充对象说明，加上原有咖啡组成图，加上远端已新增的 7 处原叶、干茶与叶底图，共 44 处图像使用位置。原来的分类与工艺表仍保留，未将它们计入这次配图增量。

大多数新增图讲解典型原料、工艺、组成和数量关系。仅 3 处有意使用外观容易误导的例子：深色啤酒未必更烈、同样透明的烈酒可以属于不同类别、冰咖啡未必是冷萃。反例不当作全书模板，也不保留事实性画错。

教学图注明图号、图题、字母对象、颜色、箭头与比例含义。AI 图不是实测样品或鉴定证据；假想标签、自拟小样与简化工序分别说明。`assets/figure-plan.json` 记录逐图用途、插入位置、图例与正文，`assets/scene-catalog.json` 管理原有情境图说明；生成提示词见 `assets/illustration-notes.md`。

可编辑稿和独立章节 Markdown 已嵌入实际图片；逐章 ZIP 包含图片文件，保留 `逐章阅读/` 与 `assets/` 两目录的位置即可阅读。分页引用和独立章节导航均保留。

只重建阅读包并验证，不生成网页：

```bash
python build_book.py
python export_chapters.py
python scripts/check_build.py --book-only
```

## 自动构建与 GitHub Pages

`.github/workflows/build-and-deploy.yml` 在分支推送、Pull Request 和手动触发时，从 `chapters/`、`research/` 和 `assets/` 重建全书与网页。只有默认分支的推送或手动运行会部署 GitHub Pages；其他分支与 PR 只构建、校验并上传产物。

首次启用时，在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。之后默认分支每次更新会自动部署，无需额外配置密钥。默认地址为 <https://yzyexp.github.io/Learn-A-Cup-Of-World/>，实际部署地址见 Actions 的 `github-pages` environment。

在 Actions 的 **Build book and deploy Pages** 运行详情下载：

- `cup-world-books`：全书 PDF、可编辑稿、24 组逐章 PDF/Markdown、逐章 ZIP 和排版检查记录。
- `cup-world-site`：可直接部署的静态网站，包含章节目录、逐章文字与表格、封面和分部插画、原有章内插画、新增 24 幅教学图及图例、茶叶细节图、咖啡组成示意、引用链接和 PDF/ZIP 下载。全部链接为相对路径，可部署到仓库子路径。

构建产物保留 30 天；已部署网页上的下载文件随网站持续可用。网页与 PDF 均来自本次源码构建，不依赖 `books/` 中保存的旧版本。网页版由 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 构建，提供章节导航、章内目录、中文搜索与脚注。章节地址仍为 `chapters/07.html` 等，不改变已有阅读链接。

网页直接读取 `chapters/` 中的配图标记，按正文顺序生成独立 WebP 配图并引用新增 PNG 教学图；六类茶的干茶与叶底分别显示在对应小节。与 PDF 共用原图区域定义，原图不变，浏览器显示普通图片，不依赖绝对定位或 CSS 裁切。主题和阅读样式使用带内容指纹的文件名，避免部署后旧缓存影响排版。`mkdocs.yml` 为主题配置，`work/web-docs/` 为自动生成的网页源文件。

本地生成和验证同样的产物：

```bash
python -m pip install -r requirements.txt
python build_book.py
python export_chapters.py
python build_site.py
python scripts/check_build.py
python -m http.server 8000 --directory site
```

打开 <http://localhost:8000/> 预览。`output/` 为 PDF 与逐章产物，`site/` 为部署目录，均不提交到 Git。校验会检查全书和逐章页数、书签、排版空间、压缩包完整性，并按原稿核对每张图片的顺序、所属小节和文件对应关系，以及图片替代文本、文件完整性、脚注锚点和网页本地链接；任一检查失败都会阻止部署。

## 茶类与叶片细节增补

2026年10月12日根据茶类覆盖与细节配图反馈，第十四章由 2 页扩充为 13 页，全书更新为 95 页、87 项资料。分别解读绿、白、黄、乌龙、红、黑茶的加工、代表形态与观察线索，补原叶、芽叶组合、干茶与叶底，并另讲普洱生熟、再加工茶与风味比较。

新增两张原始插画图板：原叶四格图与六类干湿对照六格图。PDF 使用原始图板视口，共 7 个新增教学配图位置；Markdown 嵌入完整图板并标明格子位置。图像标注为 AI 教学示意，不作为真实样本、同批原料对照实验或等级鉴定。

以下 `output/` 链接在本地重建后可用，在线构建产物见 Actions 下载与 Pages 阅读版。

- [第十四章独立 PDF](output/逐章阅读/14同一类植物的不同道路.pdf)
- [第十四章阅读稿](books/逐章阅读/14同一类植物的不同道路.md)
- [逐章 PDF 与配图阅读包](output/杯中世界逐章阅读.zip)

独立章节 Markdown 的新增配图置于同目录 `assets/`，阅读包包含图片。全书 Markdown 的图片使用 `../assets/` 相对路径。构建依赖见 `requirements.txt`；网页版在每个茶类小节单独展示对应细节图。


## Markdown 图注修订（2026年10月13日）

图号、图题、图注与图例直接写在 `chapters/*.md` 中，封面与分部页说明写在 `frontmatter/illustrations.md`。PDF、可编辑稿和 MkDocs 网页读取相同的 Markdown；改图注无需重绘图片。

24 幅教学图清除了重复章标题、图号、示意声明和解释性段落。比较插画不叠文字；图解保留对象名称、坐标、数值与箭头。原有情境插画、茶叶细节图和咖啡组成图也使用普通 Markdown 图片及图注，不再由构建程序拼写说明。

`<!-- figure-height: 160 -->` 这类注释只控制 PDF 中图片的最大高度，不显示为正文。绘图脚本和 CI 会重新生成图像，并检查图号、图题与说明没有被画进矢量图。全书仍为 120 页、24 组独立章节，资料与少量外观反例继续保留。
