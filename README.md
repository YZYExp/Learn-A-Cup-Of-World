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
- AI 插画分为阅读情境与明确标注的教学示意；精确分类和流程由正文资料与人工定义的表图负责。

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

使用 Python 3.12，依赖见 `requirements.txt`。在项目目录运行 `python build_book.py`。PDF 为 A5 阅读开本，字体嵌入，页码连续，目录与书签可导航。

之后运行 `python export_chapters.py`，得到 24 组独立 PDF 与 Markdown 以及逐章阅读压缩包。20 章正文之外的读前说明和 3 个附录也单独成文件；每章 PDF 页脚标示本章页码与全书页码。

## 完整首版

2026年10月11日编写任务完成：57 页、20 章、约 1.8 万汉字、50 项资料。正文各章两页，另有读前说明、插画扉页、三页附录和书末参考资料。源码包保留完整 Git 历史、分章稿件、配图、字体许可与排版程序。

`research/editorial-check.md` 记录内容与版面校订；生成后 `output/layout-check.json` 记录逐页引用与空间检查。最终阅读版和整合的可编辑 Markdown 稿由排版程序生成。字体文件由 Google Fonts 的 Noto Sans SC 变体派生，许可见 `assets/OFL.txt`。

## 图解修订版

2026年10月12日根据阅读反馈修订：81 页，正文与附录约 2.4 万汉字，75 项参考资料。精酿、调酒、调茶和咖啡菜单分别扩展；新增 8 幅章内插画，连同原封面和分部页共有 12 个插画使用位置。正文增加结构与配方表，并将完整章节分别导出为 PDF 和 Markdown。

修订在 `revision-illustrated` 分支进行，保留首版提交和修订提交。阅读版仍采用当页引用；表格的自拟分组、经典配方来源及插画使用边界均在正文注明。

## 直接阅读与历史

- [全书 PDF（95 页）](books/杯中世界.pdf)
- [可编辑阅读稿](books/杯中世界可编辑稿.md)
- [24 份独立章节阅读稿](books/逐章阅读/)
- [原始 Git 历史与恢复方法](history/README.md)

克隆后先运行 `python -m pip install -r requirements.txt`，再执行上述重建命令。仓库包含重建所需字体及字体许可。

当前 GitHub 阅读 PDF 保留全部 95 页、正文、引用链接和导航，使用工程中的原始插画。独立章节 PDF 可用 `export_chapters.py` 重建。

2026年10月12日补充署名与开放许可：封面采用“策划与整理：YZ”，新增独立的署名与许可页，并同步全书与章节 PDF 的元数据、Markdown 和阅读包。新增一页后全书为 82 页，正文内容和 24 组章节结构保持原有编排。

原始 7 次写作提交已完整恢复到 `original-revision-illustrated` 分支，原始首版保留在 `original-main` 分支；原提交编号、作者、日期与父子关系不变。详见历史说明。

## 自动构建与 GitHub Pages

`.github/workflows/build-and-deploy.yml` 在分支推送、Pull Request 和手动触发时，从 `chapters/`、`research/` 和 `assets/` 重建全书与网页。只有默认分支的推送或手动运行会部署 GitHub Pages；其他分支与 PR 只构建、校验并上传产物。

首次启用时，在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。之后默认分支每次更新会自动部署，无需额外配置密钥。默认地址为 <https://yzyexp.github.io/Learn-A-Cup-Of-World/>，实际部署地址见 Actions 的 `github-pages` environment。

在 Actions 的 **Build book and deploy Pages** 运行详情下载：

- `cup-world-books`：全书 PDF、可编辑稿、24 组逐章 PDF/Markdown、逐章 ZIP 和排版检查记录。
- `cup-world-site`：可直接部署的静态网站，包含章节目录、逐章文字与表格、引用链接和 PDF/ZIP 下载。全部链接为相对路径，可部署到仓库子路径。

构建产物保留 30 天；已部署网页上的下载文件随网站持续可用。网页与 PDF 均来自本次源码构建，不依赖 `books/` 中保存的旧版本。网页版提供文字阅读及新增茶叶细节图板，完整插画及当页排版见 PDF。

本地生成和验证同样的产物：

```bash
python -m pip install -r requirements.txt
python build_book.py
python export_chapters.py
python build_site.py
python scripts/check_build.py
python -m http.server 8000 --directory site
```

打开 <http://localhost:8000/> 预览。`output/` 为 PDF 与逐章产物，`site/` 为部署目录，均不提交到 Git。校验会检查全书和逐章页数、书签、排版空间、压缩包完整性及所有网页本地链接；任一检查失败都会阻止部署。

## 茶类与叶片细节增补

2026年10月12日根据茶类覆盖与细节配图反馈，第十四章由 2 页扩充为 13 页，全书更新为 95 页、87 项资料。分别解读绿、白、黄、乌龙、红、黑茶的加工、代表形态与观察线索，补原叶、芽叶组合、干茶与叶底，并另讲普洱生熟、再加工茶与风味比较。

新增两张原始插画图板：原叶四格图与六类干湿对照六格图。PDF 使用原始图板视口，共 7 个新增教学配图位置；Markdown 嵌入完整图板并标明格子位置。图像标注为 AI 教学示意，不作为真实样本、同批原料对照实验或等级鉴定。

以下 `output/` 链接在本地重建后可用，在线构建产物见 Actions 下载与 Pages 阅读版。

- [第十四章独立 PDF](output/逐章阅读/14同一类植物的不同道路.pdf)
- [第十四章阅读稿](books/逐章阅读/14同一类植物的不同道路.md)
- [逐章 PDF 与配图阅读包](output/杯中世界逐章阅读.zip)

独立章节 Markdown 的新增配图置于同目录 `assets/`，阅读包包含图片。全书 Markdown 的图片使用 `../assets/` 相对路径。构建依赖仍见 `requirements.txt`；既有网站构建同步展示新增茶叶图板。
