# 迈必达网站 OCR 网页化重构

处理范围为 8 个正式页面：`index.html`、`product/` 下 2 页、`productlist/` 下 5 页。

本副本完成了以下工作：

- 汇总正式页面引用图片的 OCR 结果到 `ocr-text.txt`。
- 将 6 张主要参数表图片替换为可选择、可复制的语义化 HTML 表格。
- 将智能相机案例图的 16 个主标题改为 HTML 实体文字。
- 补齐视觉筛选机图片中的“适检产品”实体文字，并修正 OCR 浮层为可选择状态。
- 保留设备照片、软件界面截图、铭牌、日期码、技术图纸标注和 Logo 等图像本体文字，避免破坏图片结构或产生错误重绘。
- 新增 `cn/css/ocr-rebuild.css`，统一控制重构表格、标题和响应式显示。
- 将模具监视器页面的三张图示（成像对比、动作监视流程、集中监控系统架构）拆为可选中 HTML 实体文字、CSS 色块/边框与 SVG 箭头；照片中的原标签已清除，裁片保存在 `cn/images/ocr-diagrams/`，共用样式见 `cn/css/ocr-diagrams.css`。中文及 3 个英文版本同步，原有 HTML 表格、字号和位置未改动。
- 将 `product/10032*.html` 的「技术参数表」图片（23 行参数、蓝色标题条、斜线表头）改为语义化 `<table>`：文字全部为可选中 HTML，蓝色标题条、斜线、边框、底色用 CSS 复刻，8 张设备照片裁片保存在 `cn/images/ocr-spec/`，样式见 `cn/css/ocr-spec-table.css`，生成脚本为 `tools/rebuild-spec-table.py`。原图按 2066×1888 像素网格映射列宽与行高，字号随容器等比缩放；第二个标签页已有的 `ocr-table` 及外形尺寸图保持原样。

校验命令：

```powershell
node tools\verify-ocr-rebuild.js
```

`ocr-inventory.json` 保存页面、图片、替代文字及 OCR 文本的对应关系，便于后续在网站后台继续人工校订。
