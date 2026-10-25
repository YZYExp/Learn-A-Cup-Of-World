# 杯中世界

面向个人兴趣的中文图解读本，介绍酒、茶、咖啡的起源、制作与风味。目前全书 232 页、20 个正文章节、读前说明与 3 个附录，引用 169 项资料，含 87 处配图。

**策划与整理：YZ**。工艺、组成与数量图解由项目绘图脚本定义。

## 阅读

- [在线逐章阅读](https://yzyexp.github.io/Learn-A-Cup-Of-World/)
- [Release 全书 PDF](https://github.com/YZYExp/Learn-A-Cup-Of-World/releases)
- [24 份章节 Markdown 源稿](chapters/)

发布版本时，Release 只附一个 `杯中世界.pdf`。网页按章阅读并链接 Release；不再默认生成、上传或在 Git 中保存逐章 PDF、阅读 ZIP 及重复的整合稿。首个 Release 发布后，其构建流程会自动附上 PDF。

## 开放许可

书稿、项目自制图表与 AI 插画采用 **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)**；构建脚本采用 **[MIT](licenses/MIT.txt)**；字体遵循 **[SIL OFL 1.1](assets/OFL.txt)**。

许可适用于 YZ 有权许可且依法受保护的部分，第三方引用与链接目标不纳入本项目授权。署名、许可范围及图像来源说明见 [NOTICE.md](NOTICE.md)，内容许可全文见 [LICENSE](LICENSE)。

## 书稿与配图

1. 共同基础：原料与加工、感官、早期历史。
2. 酒：啤酒、葡萄酒、气泡与加强酒、米酒、白酒、主要烈酒及调饮。
3. 茶：历史、六类茶、75 条常见茶名介绍、鲜叶与干湿细节、冲泡与调茶。
4. 咖啡：历史、物种与品种、处理、烘焙、冲煮与菜单。
5. 带回日常：保存、标签、预算、饮用边界与个人记录。

图号、图题、图注与图例写在 `chapters/*.md`，封面和分部页说明写在 [frontmatter/illustrations.md](frontmatter/illustrations.md)。图片保留读图必需的名称、坐标、数值与箭头；大多数是典型例子，少量外观反例提醒分类边界。引用位于对应正文附近，PDF 保留当页资料与可点击链接。

`assets/` 保存实际配图、原始插画及字体；`research/` 保存引用、覆盖与校订记录。可重建的矢量 PDF 图稿、全书 PDF、合稿、章节导出和网页写入已忽略的构建目录，不进入 Git。

## 本地重建

使用 Python 3.12：

```bash
python -m pip install -r requirements.txt
python scripts/render_figures.py
python build_book.py
python export_chapters.py
python scripts/check_build.py --book-only
```

得到 `output/杯中世界.pdf`、可编辑合稿、24 份章节 Markdown、导航清单和排版检查记录。`export_chapters.py` 只生成文字导出与导航信息；构建输出中只有一个全书 PDF，没有逐章 PDF 和 ZIP。

图注改动直接编辑 Markdown；更改图形关系时再修改绘图数据或脚本并重绘。修订 AI 图板后须保留提示词与审校记录，再重建对应章内图。`<!-- figure-height: 160 -->` 这类注释只控制 PDF 中图片的最大高度。

需要本地构建网页时：

```bash
python build_site.py
python scripts/check_build.py
python -m http.server 8000 --directory site
```

网页版采用 MkDocs Material，提供导航、章内目录、中文搜索、图例和脚注。章节地址沿用 `chapters/07.html` 等路径。校验检查 PDF 页数、书签、脚注空间、章节覆盖、Markdown 图片路径，以及网页配图顺序、图片对应关系和本地链接。

## CI 与发布

[build-and-deploy.yml](.github/workflows/build-and-deploy.yml) 在推送、PR 和手动运行时重绘配图、构建并校验全书和网页。普通构建只上传小型检查报告及网页预览，保留 7 天；网页产物不含 PDF 或阅读压缩包。只有默认分支更新会部署 Pages。

[release-book.yml](.github/workflows/release-book.yml) 在 GitHub Release 发布时检出该版本的 tag，重建并校验，最后上传唯一的全书 PDF。无需额外配置密钥。发布时使用包含此流程的 tag，并在仓库 Releases 界面发布版本。

首次部署 Pages 时，在仓库 Settings → Pages → Build and deployment 中将 Source 设为 GitHub Actions。

## 历史与仓库体积

[CHANGELOG.md](CHANGELOG.md) 按内容与工程里程碑整理既有提交；[history/README.md](history/README.md) 记录原始历史分支、体积审计和后续历史清理方法。

原始写作提交保留在 `original-main` 与 `original-revision-illustrated` 远端分支，移除了重复的 bundle 文件与一次性恢复 workflow。本次删除当前目录中的成品，不改写已发布提交；旧大文件仍存在于旧历史中。若只需要最新书稿，可在合并后浅克隆：

```bash
git clone --depth 1 --single-branch https://github.com/YZYExp/Learn-A-Cup-Of-World.git
```

缩减完整历史需要另行协调 Git 历史重写，普通 PR 不能删除旧提交里的对象。审计与具体处理步骤已放入历史说明。

## “洗法”增补（2026年10月13日）

修订后全书为131页、97项资料、47处图像使用位置。第十二章补脂洗／油洗与乳洗／奶洗；第十五章补洗茶、润茶与干醒／湿醒的语境、可选冲泡对照及农残说法的边界；第十七章补水洗与机械去黏液、半水洗名称歧义、湿刨脱壳时机，以及厌氧发酵与后续处理路线的组合。附录二提供跨章速查。

新增三幅工序图，图题与图例直接写在章内Markdown。十项新资料就近列出；[覆盖与资料边界](research/washing-coverage.md)记录核实和取舍。沿用当前源码与成品分离约定，Release仅发布全书PDF，网页按章阅读。

## 配图扩充（2026年10月15日）

新增 24 个教学插画面板与 9 幅图解，覆盖全部 20 个正文章节及笔记附录；其中一幅香气参照图替换旧情境图。全书从 47 处配图增至 79 处，重排为 163 页。原料、器具、干湿形态与烘焙外观用于观察；茶类分岔、咖啡果实分层、蒸馏与冲煮关系由脚本绘制。

六张原始图板、实际章内 PNG、可编辑图注与重绘代码均保存在仓库。提示词见 [新增插画记录](research/expanded-illustration-manifest.json)，逐章覆盖和核对结果见 [配图扩充检查](research/illustration-expansion.md)。图注与对应图片保持同页，生成插画不作为真实样本或设备操作依据。

## 咖啡章节扩展（2026年10月25日）

第十六至十八章补充植株传播、物种与品种、产地标签、烘焙路标与排气，加入可实际练习的手冲步骤、研磨和水质观察、浓度与萃取算例、意式粉液比、冰手冲用水、冷萃记录与低因原料选择。咖啡三章从24个内容页增至42页，章内配图从14处增至20处。

新增5幅可重绘图解与1幅研磨外观AI教学插画；15项新增资料保留就近引用。全书重建为183页，保留单一全书PDF和24份章节Markdown的交付方式。引用解析支持三位编号，校验同时检查正文引用与对应PDF页下注。范围、图文审查与验证见[咖啡扩展记录](research/coffee-expansion.md)，插画提示词见[研磨插画记录](research/coffee-illustration-manifest.json)。构建命令保持不变。

## 茶章节扩写与形态修订（2026年10月24日）

第十三至十五章新增约 4,850 个汉字、14 个阅读单元，补充茶史证据、六类茶逐类实例、普洱标签与家庭冲泡调整。重绘三张茶图板，替换鲜叶、六类干湿、外形与器具等 11 处章内配图；重点修正芽叶连接、白毫长度、揉卷乌龙与泡后叶片形态，并改用重瓣茉莉花示意。新增图 15-7，用三条独立路径说明冲泡调整起点。

全书重排为 177 页。茶部 50 页已检查缩略图，并放大检查鲜叶、乌龙与新图解页面；图片、图注和页下注校验通过。[覆盖与审校记录](research/tea-coverage.md)及[本轮图板提示词](research/tea-revision-2026-10-24.json)随源码保存。

## 常见茶款图鉴（2026年10月25日）

第十四章增加 75 条实际短介绍，涵盖中国常见茶款、黑茶产品家族、花香及调香茶、日本茶、海外红茶产区，以及单列的花草谷物代用茶。每条说明产地或原料、制作特点、形态与典型风味；合并介绍的相邻名称按一条计，不把产区、品种和拼配冒充成新的基础茶类。

新增约 9,500 字与四种绿茶外形对照图，新增 57 项资料并就近引用。对齐上游咖啡三章扩展后，全书为 232 页、169 项资料、87 处配图；保留咖啡资料编号 98—112，茶款新资料使用 113—169。沿用上游三位数引用解析，并补充当页可点击链接校验。[逐款覆盖表](research/tea-catalog-coverage.json)、[资料核对](research/tea-catalog-evidence.md)、[配图记录](research/tea-catalog-illustration.json)与[编号映射](research/tea-reference-remap.json)保留在工程中。
