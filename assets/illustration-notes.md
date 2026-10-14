# 插画说明

插画由内置 imagegen 生成，输出为一张四区同风格场景图。封面及分部扉页使用 PDF 视口显示对应区域，原始位图未修改。原始文件为 `illustrations.png`。

## 最终提示词

Use case: illustration-story. Create a single high-resolution 2 by 2 equal-panel illustration sheet for a Chinese personal-interest book about wine, tea and coffee. Four landscape panels separated by simple wide cream gutters, no text anywhere. All panels in one consistent restrained gouache editorial illustration style with fine paper texture, warm ivory ground, terracotta, forest green and dark brown, realistic recognizable objects, quiet natural lighting. TOP LEFT: opening still life of a modest wine glass with red wine, a small Chinese tea cup of pale tea, and a ceramic cup of black coffee, with grape cluster, tea sprig and a few coffee cherries; no labels or brands. TOP RIGHT: alcohol chapter illustration, amber spirit in tulip glass, a red wine glass and a small beer glass, grapes and barley on a wooden table, simple composition. BOTTOM LEFT: tea chapter illustration, green tea leaves on a branch, plain gaiwan and small cup on table, subtle mountains through a window, no historical claims or human figures. BOTTOM RIGHT: coffee chapter illustration, ripe red coffee cherries on a branch, roasted beans, simple pour-over dripper on ceramic cup, clean botanical detail. These are atmospheric illustrations rather than historical reconstructions or technical diagrams. Objects in each panel stay inside their own equal rectangular panel with generous padding. No lettering, no watermark, no decorative borders, no infographic labels.

## 使用边界

插画仅用于阅读情境。分类表、流程比较与年代证据表由编写者根据引用资料定义，未交给图像生成器决定内容。


# 图解修订版新增插画

新增图像由内置 imagegen 生成，仍以 PDF 视口显示各面板，原始位图未修改。章节图像用于阅读情境，配方与分类由正文和明确引用负责。

## menu-scenes.png 最终提示词

Create a high resolution editorial illustration sheet with exactly 4 equal landscape panels in a 2x2 grid, separated by wide ivory gutters. Intended as chapter body illustrations in a Chinese illustrated book about beer, cocktails, blended tea and coffee. Consistent clean realistic gouache illustration with gentle paper texture, warm ivory, forest green, amber and terracotta accents, simple uncluttered table compositions, clear object silhouettes, NO TEXT, NO LABELS, NO LOGOS. TOP LEFT: craft beer tasting flight with four small glasses showing pale golden lager, hazy golden IPA, amber ale, and dark stout, nearby barley and a hop cone, individual glass silhouettes and differing clarity clearly visible. TOP RIGHT: cocktail bartender workbench with three distinct finished cocktails (short amber old fashioned over a big ice cube, pale daiquiri in a coupe, a long clear highball with bubbles and citrus), shaker, jigger, citrus peel, uncluttered. BOTTOM LEFT: tea blending table with plain brewed tea, fruit tea glass with visible citrus, milk tea glass, small bowls of dry tea leaves and spices, aesthetically calm. BOTTOM RIGHT: cafe menu still life with espresso in a tiny cup, black filter coffee in a normal cup, a latte in glass showing milk coffee gradient, cold coffee in glass with ice. These are sensory illustrations, not exact recipe diagrams. Keep all objects fully within each panel and generous internal padding. Do not imply that colors prove drink identity. Composition frontal three-quarter view, no people, no decorative lettering.

## process-scenes.png 最终提示词

High resolution editorial illustration sheet with exactly four equal landscape panels in 2 by 2 grid separated by wide ivory gutters. Match a restrained realistic gouache book illustration style, cream paper texture, forest green and warm brown accents. No letters, labels, logos or watermarks. TOP LEFT: sensory learning still life, sliced citrus peel, ripe dark berries, small piece of toasted bread and cocoa powder, clean white cup, composed as four easily distinguished aroma references, no people. TOP RIGHT: archaeological still life, plain ancient-looking clay pot and stone mortar with barley, grapes and honey in separate modest vessels, neutral museum-table presentation, atmospheric interpretation not a reconstruction of a specific site. BOTTOM LEFT: rice fermentation still life, a bowl of steamed white rice, small rice grains, pale rice koji texture in separate wooden tray, tiny ceramic sake cup, carefully realistic non-grotesque natural texture. BOTTOM RIGHT: whisky and brandy maturation still life, an oak barrel lying horizontally in cellar, two small tulip glasses of amber liquid, faint grapes and barley at side, clear wood texture. Each panel is uncluttered with generous padding and recognizable objects confined within its rectangle. Flat educational composition, soft daylight, calm atmosphere. Do not render process arrows or scientific claims.


# 茶叶细节增补

`tea-fresh-details.png`：原叶四格教学示意，包括芽叶组合、嫩叶与较成熟叶、失水变软、鲜叶与干叶质感。

`tea-dry-wet-details.png`：两列三排的六类代表形态，按行依次为绿茶与白茶、黄茶与乌龙、红茶与普洱熟茶。每格左为干茶，右为叶底；PDF 用原始位图的视口显示各格，在位图之外排版中文标签，不改动原始像素。

两图均由内置 imagegen 生成并经视觉核对，完整提示词见 `../research/tea-illustration-manifest.json`。它们帮助辨认形态和提出观察问题，不是植物鉴定、真实样本证据或同批鲜叶分流加工实验。图中比例与色彩不是检测数据。

# 图例增补版：教学图与偶尔出现的外观反例

2026年10月12日新增 24 幅章内教学图，按信息需求分布于 20 个正文章节。20 幅关系、工艺、组成或数量图由 `scripts/render_figures.py` 明确定义；4 幅使用生成插画的视口并叠加可核对标签，其中红茶图为典型加工情境，其余 3 幅为偶尔出现的外观反例。所有原始生成图保持不变，未进行像素编辑。

逐图题名、插入位置、文字图例与引用正文见 `figure-plan.json`；原有情境图的对象说明见 `scene-catalog.json`。图例区分材料颜色、类别、阅读关系、数量比例和不按比例的示意，假想样例不称为真实产品或检测结果。

## counterexamples.png 提示词

Create one high-resolution 1536x1024 2x2 editorial gouache illustration sheet with exactly four equal landscape panels, separated by broad ivory gutters, for a Chinese nonfiction book teaching that beverage appearance cannot determine category. Warm cream paper, restrained forest green, brown and amber, physically realistic vessels, frontal three-quarter perspective. No text, no labels, no logos, no numbers, no watermark. TOP LEFT: two identical straight small beer tasting glasses at the same fill height, left very dark stout with a pale foam head, right clear pale gold IPA with a pale foam head, plain neutral background and nothing else. Do not imply alcohol strength visually. TOP RIGHT: two identical small tulip spirit tasting glasses, both filled with equally colorless transparent liquid to the same height, left intended as unflavored gin and right unflavored vodka; they should look indistinguishable. No botanicals in the glasses or next to them. BOTTOM LEFT: a fresh green tea shoot resting on an ivory saucer on left, a small ceramic dish of dark dried black-tea leaves in middle, and a small transparent glass cup of amber-red black tea on right. The green fresh leaf and dark processed leaf must be separate, same plant transformed through processing, no arrows or text. BOTTOM RIGHT: two identical straight tumblers, same quantity of dark amber-brown black coffee, equal ice cubes, no milk, no foam, no straws; left represents hot-brewed coffee chilled over ice, right cold brew served with ice, visibly indistinguishable. Clean simple teaching composition and generous padding within each panel. These are AI teaching illustrations, not photographs of real samples, not exact recipes, not visual authentication guides. Match the existing warm editorial gouache illustrations of a beverage knowledge book.

## 核对结果与边界

四个面板的对象数量、位置和可见材料已检查。烈酒面板实际生成的是带短脚玻璃杯；文字改为同形无色烈酒杯，不将器具形状当成类别证明。咖啡图没有奶；原有菜单情境图的右侧冰飲可见奶纹理，图注如实写作“带奶纹理冰饮”，不再让画面暗示只有黑咖啡。

啤酒 4.2% 与 6.5% 为构造标签，依据既有 BJCP 风格范围选择，图像不证明真实酒精度。红茶图说明三个观察对象，不用叶形进行茶树或茶类鉴定。数量图使用正文明确给出的毫升量、ABV 和算式；没有数值刻度的图不承担定量测量。


# 2026年10月13日：图注与图像分开

24 幅教学图重新从绘图代码生成，清除图内的图号、长标题、通用示意声明和解释性段落。比较插画直接显示原图视口，不叠加 A/B 名称；身份和左右对应关系写在章内 Markdown 中。卡片图去掉重复建议和无必要的编号，工艺图保留关系标签，数量图保留数值与单位。

全部章内配图使用标准 Markdown 图片链接，紧邻的图号、图题、图注与图例为可编辑文本。封面与分部页说明另存 `frontmatter/illustrations.md`。图像输出仅按内容边界排版，原始 AI 插画文件保持不变；茶叶细节图分别导出为无叠字视口。

# 2026年10月15日：原料、器具与工序扩充

六张 `expanded-*.png` 原始图板由内置 imagegen 生成，共 24 个面板。完整提示词见 `../research/expanded-illustration-manifest.json`。原始位图保持不变，绘图程序通过 PDF 视口导出章内 PNG；图题、名称对应和图例不叠在生成画面上。

面板涵盖麦芽与酒花、葡萄皮肉、蒸米与米麴、杜松与龙舌兰、瓶与承压罐、壶式蒸馏器、桶板、茶叶外形与吸水展开、茶具、咖啡果实与烘焙、冲煮器具、奶咖、调饮器具、保存与记录。一幅新的香气参照图替换原有闻香情境图，其余为新增位置。

九幅关系图由 `scripts/enriched_figures.py` 定义，包括转化与提取、考古线索、蒸馏原理、调酒动作、六类茶路线、普洱生熟分岔、咖啡果实分层、冲煮水流及四周探索。图内只留必要的名称与箭头；事实说明与引用留在相邻 Markdown。

核对时发现，干茶四碟面板的最后一碟实际为条索而非提示词中的颗粒；奶咖面板有拉花与装饰；仪表部分有刻线但没有读数。正文按实际画面描述，不把这些差异强行解释为事实。龙舌兰与谷物没有统一大小比例，米麴外观不能鉴定菌种，壶式蒸馏器不能据此施工，奶咖与烘焙外观不规定全球标准。
