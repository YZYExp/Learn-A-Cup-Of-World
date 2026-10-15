# 署名、来源与开放许可

**策划与整理：YZ**

YZ 负责选题、需求设定与成稿整理。书稿使用 AI 辅助编写，情境插画、原料与器具图、茶叶细节图为生成图像；工艺及数量图解由绘图脚本定义。生成图像是教学示意，没有对应的真实样本。原始图板与提示词保存在 `assets/` 与 `research/`，章内图例说明具体用途与简化边界。

## 许可范围

| 内容 | 许可 | 许可文件 |
| --- | --- | --- |
| 本项目书稿、阅读版 PDF 与 Markdown、项目说明、项目自制图表、AI 插画及参考资料的自编说明 | [CC BY 4.0（知识共享署名 4.0 国际许可协议）](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) | [LICENSE](LICENSE) |
| 本项目 Python 构建与导出脚本、工作流配置 | MIT | [licenses/MIT.txt](licenses/MIT.txt) |
| Noto Sans SC 字体及其派生文件 | SIL Open Font License 1.1 | [assets/OFL.txt](assets/OFL.txt) |
| 引用的第三方文字、作品、商标及链接目标资料 | 不纳入本项目授权；遵循各自权利与适用法律 | 见正文各页及 `research/sources.json` 中的出处 |

此范围适用于当前发布版本。历史分支和 Git 历史存档保留其原始状态；不能仅凭其中缺少许可文件推定第三方材料也已获授权。

## 书稿和插画如何使用

在 CC BY 4.0 适用的范围内，允许复制、分享、翻译、改编及商用。请保留署名、作品出处与许可链接，注明所作改动（包括之前已注明的改动），并保留随材料提供的版权、许可及免责声明。署名可以采用适合媒介的合理形式，但不得暗示 YZ 为你的使用背书。不得另加法律条款或技术措施，限制他人行使许可授予的权利。

推荐署名：

> 《杯中世界》，策划与整理：YZ；[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。[作品出处](https://github.com/YZYExp/Learn-A-Cup-Of-World)。如有改动，请注明。

上述文字是阅读说明，具体条款以 [CC BY 4.0 完整法律文本](LICENSE)为准；[官方简体中文说明](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)便于阅读。

## AI 内容与权利边界

YZ 仅就有权许可且依法受保护的部分提供授权。纯 AI 生成内容是否受著作权保护，取决于适用法律；选择 CC BY 4.0 或 MIT 不会让原本不受保护的内容自动产生著作权。对于不受保护的内容、公共领域材料及依法无需许可的使用，本项目不通过许可额外产生权利或施加限制。

第三方材料、人格权、商标权等并不因本项目开放而自动获得许可。许可方不就材料提供保证，具体免责与责任限制见对应许可全文。

相关原则见 Creative Commons 官方 FAQ 中的[公共领域与许可范围](https://creativecommons.org/faq/#may-i-apply-a-creative-commons-license-to-a-work-in-the-public-domain)和[第三方材料标注](https://creativecommons.org/faq/#may-i-apply-a-cc-license-to-my-work-if-it-incorporates-material-used-under-fair-use-or-another-exception-or-limitation-to-copyright)。

选择 CC BY 4.0 是因为本项目以知识书稿和教学图像为主，希望读者能自由分享、改编和商用，同时保留来源。脚本使用 MIT，便于复用构建工具；字体保留其既有许可。

`publication.json` 是构建程序使用的署名及许可元数据。全书封面、署名与许可页、整合 Markdown 与独立章节从中读取相同信息。
