"""Rebuild the zh-CN and en-US product-family pages with a new visual system."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = "202611261625"
HOME_MARKER = "<!-- BEGIN VP2 PRODUCT PAGE -->"
HOME_END = "<!-- END VP2 PRODUCT PAGE -->"
CTA_MARKER = "<!-- BEGIN VP2 CTA -->"
CTA_END = "<!-- END VP2 CTA -->"

PAGES = {
    "monitor": {
        "zh": {
            "file": "product/10032.html",
            "eyebrow": "注塑模具保护",
            "title": "IMX-790 模具监视器",
            "lead": "在每次合模之前完成模腔、镶件与脱模状态判断，把压模风险留在事故发生前。",
            "stats": [
                ("0.03s", "单次检测"),
                ("8 MP", "相机分辨率"),
                ("MES", "数据接口"),
            ],
            "features": [
                ("合模前判断", "统一确认模穴、模芯、残留件与滑块位置。", "PRE-CLOSE"),
                ("柔性 ROI", "矩形、椭圆与任意形状区域可按模具独立配置。", "REGION"),
                ("报警可追溯", "报警图像保留参数与 I/O 状态，支持一键导出。", "TRACE"),
            ],
        },
        "en": {
            "file": "product/10032.en-US.html",
            "eyebrow": "INJECTION MOLD PROTECTION",
            "title": "IMX-790 Mold Protection Monitor",
            "lead": "Verify cavities, inserts and ejection before every mold close, keeping crash risk out of the production cycle.",
            "stats": [
                ("0.03s", "Inspection decision"),
                ("8 MP", "Camera resolution"),
                ("MES", "Data interface"),
            ],
            "features": [
                ("Pre-close verification", "Check cavities, cores, residual parts and slide position as one decision.", "PRE-CLOSE"),
                ("Flexible ROI", "Configure rectangular, elliptical and free-form regions per mold.", "REGION"),
                ("Traceable alarms", "Retain images, parameters and I/O states with one-click export.", "TRACE"),
            ],
        },
        "family": "monitor",
        "image": "monitor-hero-studio.webp",
        "theme": "light",
    },
    "camera": {
        "zh": {
            "file": "product/smart-camera.html",
            "eyebrow": "边缘 AI 视觉",
            "title": "V3 Pro AI 视觉传感器",
            "lead": "把采集、识别与判断收进同一台工业相机，减少现场调试和外部计算链路。",
            "stats": [
                ("15s", "AI 自动找图"),
                ("3s", "参数生成"),
                ("IP65", "防护等级"),
            ],
            "features": [
                ("AI 自动曝光", "自动调整亮度、光源与曝光，快速获得可用图像。", "ACQUIRE"),
                ("样本驱动", "登记 OK / NG 样本后，由 AI 生成适合的检测条件。", "LEARN"),
                ("一体化成像", "变焦、光源与处理集成在紧凑的工业机身内。", "INTEGRATE"),
            ],
        },
        "en": {
            "file": "product/smart-camera.en-US.html",
            "eyebrow": "EDGE AI VISION",
            "title": "V3 Pro AI Vision Sensor",
            "lead": "Capture, recognition and judgment in one industrial camera, with less setup and a shorter computing chain.",
            "stats": [
                ("15s", "AI image search"),
                ("3s", "Setup generation"),
                ("IP65", "Ingress protection"),
            ],
            "features": [
                ("Adaptive exposure", "Balance lighting, illumination mode and exposure for a usable image.", "ACQUIRE"),
                ("Sample-driven setup", "Register OK and NG samples, then let AI generate the inspection recipe.", "LEARN"),
                ("Integrated imaging", "Zoom optics, lighting and processing in one compact industrial body.", "INTEGRATE"),
            ],
        },
        "family": "camera",
        "image": "camera-hero-studio.webp",
        "image_version": "202611261705",
        "theme": "dark",
    },
    "feeder": {
        "zh": {
            "file": "productlist/10029.html",
            "eyebrow": "柔性上料",
            "title": "视觉并联上料机器人",
            "lead": "视觉定位与并联机器人共享同一节拍，面向多品种、小批量的高速拾取、分拣与摆盘。",
            "stats": [
                ("±0.05 mm", "重复定位"),
                ("4500 件/h", "最高速度"),
                ("8", "标准型号"),
            ],
            "features": [
                ("AtomCV 定位", "自研视觉系统把抓取坐标转换成稳定的机器人路径。", "LOCATE"),
                ("Delta 结构", "轻量并联结构与高刚性运动，兼顾速度与精度。", "MOVE"),
                ("柔性上料", "振动盘、料仓与盘面可以随物料和产线定制。", "FEED"),
            ],
        },
        "en": {
            "file": "productlist/10029.en-US.html",
            "eyebrow": "FLEXIBLE FEEDING",
            "title": "Vision-Guided Parallel Feeding Robot",
            "lead": "Vision and motion share one cycle for high-speed picking, sorting and tray loading across mixed, smaller production runs.",
            "stats": [
                ("±0.05 mm", "Repeatability"),
                ("4500 pcs/h", "Max. speed"),
                ("8", "Standard models"),
            ],
            "features": [
                ("AtomCV positioning", "In-house vision turns part coordinates into a stable robot path.", "LOCATE"),
                ("Delta structure", "A lightweight parallel structure balances speed and positioning.", "MOVE"),
                ("Flexible feeding", "Bowls, hoppers and trays can be specified around the part and line.", "FEED"),
            ],
        },
        "family": "feeder",
        "image": "feeder-hero-studio.webp",
        "theme": "dark",
    },
    "sorter": {
        "zh": {
            "file": "productlist/10039.html",
            "eyebrow": "视觉筛选",
            "title": "Mic SXT 视觉筛选机",
            "lead": "从外观缺陷到尺寸判断，再把良品与不良品分流，让检测结果直接进入生产动作。",
            "stats": [
                ("60 件/min", "检测速度"),
                ("0.0007 mm", "检测精度"),
                ("360°", "多角度扫描"),
            ],
            "features": [
                ("全维度检测", "外观与关键尺寸在同一流程内完成。", "INSPECT"),
                ("多角度成像", "同步轮传动覆盖内外壁和细微表面。", "ROTATE"),
                ("自动分流", "良品与不同缺陷类型自动进入对应下料通道。", "SORT"),
            ],
            "variants": [
                ("Mic SXT", "摄像头件", "60 件/min", "0.0007 mm"),
                ("Mic DJ", "电机配件", "400 件/min", "0.001 mm"),
                ("Mic CC", "磁材", "8000 件/min", "0.001 mm"),
                ("Mic NK", "纽扣", "400 件/min", "0.001 mm"),
                ("Mic GJ", "硅塑胶", "400 件/min", "0.001 mm"),
                ("Mic JS", "金属件", "300 件/min", "0.001 mm"),
                ("Mic HXQ", "换向器", "400 件/min", "0.001 mm"),
            ],
            "specs": [
                ("适用范围", "摄像头模组、电机配件、磁材、纽扣、硅塑胶件、金属件与换向器。"),
                ("检测项目", "外观缺陷、关键尺寸、装配完整性与缺陷类型判断。"),
                ("成像方式", "同步轮或伺服旋转，支持 360° 内外壁及多角度扫描。"),
                ("检测速度", "Mic SXT 最高 60 件/min；其他机型按工件、上料方式与节拍确定。"),
                ("检测精度", "Mic SXT 最高 0.0007 mm；其他机型最高 0.001 mm。"),
                ("上料与分拣", "柔性上料、良品自动下料，不良品按缺陷类型进入独立通道。"),
                ("数据能力", "检测结果支持存储、查询与导出；MES 接口按项目配置。"),
                ("选型依据", "速度与精度取决于工件、治具、光照及参数设定，以样品验证和技术协议为准。"),
            ],
            "dossier_eyebrow": "SAMPLE VALIDATION",
            "dossier_title": "应用样件与配置记录。",
            "dossier_body": "下方样件图像用于判断上料、旋转、成像与分拣路径；最终配置以实际工件验证结果为准。",
        },
        "en": {
            "file": "productlist/10039.en-US.html",
            "eyebrow": "VISION SORTING",
            "title": "Mic SXT Vision Sorting Machine",
            "lead": "Take appearance and dimensional inspection through to automatic OK and defect sorting, so every decision becomes an action.",
            "stats": [
                ("60 ppm", "Inspection speed"),
                ("0.0007 mm", "Inspection accuracy"),
                ("360°", "Multi-angle scan"),
            ],
            "features": [
                ("Dimensional inspection", "Cosmetic checks and key dimensions in one inspection flow.", "INSPECT"),
                ("Multi-angle imaging", "Synchronous rotation exposes inner and outer surfaces.", "ROTATE"),
                ("Automatic sorting", "Good parts and defect categories leave through separate outputs.", "SORT"),
            ],
            "variants": [
                ("Mic SXT", "Camera parts", "60 ppm", "0.0007 mm"),
                ("Mic DJ", "Motor parts", "400 ppm", "0.001 mm"),
                ("Mic CC", "Magnetic materials", "8000 ppm", "0.001 mm"),
                ("Mic NK", "Buttons", "400 ppm", "0.001 mm"),
                ("Mic GJ", "Silicone and plastic", "400 ppm", "0.001 mm"),
                ("Mic JS", "Metal parts", "300 ppm", "0.001 mm"),
                ("Mic HXQ", "Commutators", "400 ppm", "0.001 mm"),
            ],
            "specs": [
                ("Applications", "Camera modules, motor parts, magnetic materials, buttons, silicone and plastic parts, metal parts and commutators."),
                ("Inspection tasks", "Cosmetic defects, critical dimensions, assembly completeness and defect classification."),
                ("Imaging", "Synchronous-pulley or servo rotation for 360-degree inner-wall, outer-wall and multi-angle scanning."),
                ("Speed", "Mic SXT up to 60 ppm; other models depend on the part, feeding method and required cycle."),
                ("Accuracy", "Mic SXT up to 0.0007 mm; other models up to 0.001 mm."),
                ("Feeding and sorting", "Flexible feeding, automatic good-part discharge and separate defect-category outputs."),
                ("Data", "Inspection records can be stored, queried and exported; MES integration is configured per project."),
                ("Validation", "Speed and accuracy depend on the part, fixture, lighting and parameter settings; final values are verified with samples and agreed in the technical protocol."),
            ],
            "dossier_eyebrow": "SAMPLE VALIDATION",
            "dossier_title": "Application samples and configuration record.",
            "dossier_body": "The sample images below guide feeding, rotation, imaging and sorting decisions. Final configuration is confirmed with the actual part.",
        },
        "family": "sorter",
        "image": "sorter-hero-studio.webp",
        "theme": "light",
    },
    "connector": {
        "zh": {
            "file": "productlist/10030.html",
            "eyebrow": "连接器在线检测",
            "title": "连接器在线检测设备",
            "lead": "面向连接器、端子与针脚的全自动外观和尺寸检测，从单料带到多料带生产保持同一判定标准。",
            "stats": [
                ("10 件/s", "最高检测速度"),
                ("±0.02 mm", "检测精度"),
                ("1–6", "CCD 配置"),
            ],
            "features": [
                ("全维度测量", "覆盖边缘间距、端子间距与圆形连接器尺寸。", "MEASURE"),
                ("多料带兼容", "单料带、双料带与多料带共用一套检测策略。", "ADAPT"),
                ("数据闭环", "检测结果支持存储、导出与趋势分析。", "TRACE"),
            ],
        },
        "en": {
            "file": "productlist/10030.en-US.html",
            "eyebrow": "CONNECTOR INLINE INSPECTION",
            "title": "Connector Inline Inspection Equipment",
            "lead": "Fully automatic appearance and dimensional inspection for connectors, terminals and pins across single- and multi-strip production.",
            "stats": [
                ("10 pcs/s", "Max. inspection speed"),
                ("±0.02 mm", "Inspection accuracy"),
                ("1–6", "CCD configuration"),
            ],
            "features": [
                ("Dimensional coverage", "Edge-to-edge spacing, terminal pitch and circular connector dimensions.", "MEASURE"),
                ("Multi-strip compatibility", "One inspection strategy for single-, double- and multi-strip parts.", "ADAPT"),
                ("Closed-loop data", "Results support storage, export and trend analysis.", "TRACE"),
            ],
        },
        "family": "inline",
        "image": "inline-connector-hero-studio.webp",
        "theme": "light",
    },
    "strip": {
        "zh": {
            "file": "productlist/10034.html",
            "eyebrow": "带料在线检测",
            "title": "Insert Molding 带料检测设备",
            "lead": "在冲压与注塑节拍之间完成料带检测，尺寸、缺料与外观异常无需离开生产线即可被识别。",
            "stats": [
                ("±0.02 mm", "检测精度"),
                ("10 件/s", "最高速度"),
                ("1–8", "CCD 配置"),
            ],
            "features": [
                ("高精度全检", "长度、位置度、内径与同心度按同一标准判断。", "MEASURE"),
                ("同步节拍", "检测速度可以与冲压机同步，不额外拉长周期。", "SYNC"),
                ("引导式操作", "标准化流程降低换型和现场配置门槛。", "OPERATE"),
            ],
        },
        "en": {
            "file": "productlist/10034.en-US.html",
            "eyebrow": "STRIP-FEED INSPECTION",
            "title": "Insert Molding Strip Inspection Equipment",
            "lead": "Inspect between the stamping and molding cycle so dimensional, missing-material and appearance errors are caught without leaving the line.",
            "stats": [
                ("±0.02 mm", "Inspection accuracy"),
                ("10 pcs/s", "Max. speed"),
                ("1–8", "CCD configuration"),
            ],
            "features": [
                ("High-precision inspection", "Length, position, bore and concentricity judged against one standard.", "MEASURE"),
                ("Synchronised cycle", "Inspection speed can follow the stamping press without adding cycle time.", "SYNC"),
                ("Guided operation", "Standardised workflows shorten changeover and commissioning.", "OPERATE"),
            ],
        },
        "family": "inline",
        "image": "inline-strip-hero-studio.webp",
        "theme": "light",
    },
    "plastic": {
        "zh": {
            "file": "productlist/10036.html",
            "eyebrow": "塑料件在线检测",
            "title": "塑料件在线检测设备",
            "lead": "产品脱离模具后立即完成多穴检测，把外观、缺料和尺寸异常赶在包装与流转之前识别。",
            "stats": [
                ("0.2s", "响应时间"),
                ("16 穴", "全域检测"),
                ("10 件/s", "单相机速度"),
            ],
            "features": [
                ("同步频闪", "高速相机与光源在脱模瞬间完成采集。", "CAPTURE"),
                ("环形照明", "多角度均匀照亮表面，提升微小缺陷可见度。", "ILLUMINATE"),
                ("AI 自适应", "针对不同塑料件的缺料与外观任务快速调整。", "LEARN"),
            ],
        },
        "en": {
            "file": "productlist/10036.en-US.html",
            "eyebrow": "PLASTIC PARTS INLINE INSPECTION",
            "title": "Plastic Parts Inline Inspection Equipment",
            "lead": "Inspect every cavity as the part leaves the mold, identifying appearance, short-shot and dimensional issues before packing.",
            "stats": [
                ("0.2s", "Response time"),
                ("16 cavities", "Full-area inspection"),
                ("10 pcs/s", "Per camera"),
            ],
            "features": [
                ("Synchronised capture", "High-speed imaging and strobe lighting expose the part at ejection.", "CAPTURE"),
                ("Ring illumination", "Uniform multi-angle light makes small defects easier to see.", "ILLUMINATE"),
                ("Adaptive AI", "Inspection conditions adapt to different plastic parts and short-shot tasks.", "LEARN"),
            ],
        },
        "family": "inline",
        "image": "inline-plastic-hero-studio.webp",
        "theme": "dark",
    },
}

PRODUCT_MENU = {
    "zh": [
        ("monitor", "模具监视器", "实时识别模具异常，降低压模风险与停机损失。", "product/10032.html"),
        ("camera", "视觉传感器", "边缘 AI 视觉传感器，兼顾速度、精度与部署灵活性。", "product/smart-camera.html"),
        ("sorter", "视觉筛选机", "面向多品类零件的外观与尺寸筛选，自动识别并分类。", "productlist/10039.html"),
        ("feeder", "柔性上料摆盘机", "视觉引导的高速上料与摆盘，适配多规格柔性生产。", "productlist/10029.html"),
        ("inline", "在线检测设备", "在线完成外观、尺寸与缺陷检测，并联动剔除与追溯。", "productlist/10030.html"),
    ],
    "en": [
        ("monitor", "Mold Protection Monitor", "Real-time mold protection that reduces crash risk and unplanned downtime.", "product/10032.en-US.html"),
        ("camera", "Vision Sensor", "Edge AI vision sensing with a balance of speed, accuracy and deployment flexibility.", "product/smart-camera.en-US.html"),
        ("sorter", "Vision Sorting Machine", "Appearance and dimensional sorting for mixed parts, with automatic recognition and classification.", "productlist/10039.en-US.html"),
        ("feeder", "Flexible Feeding System", "Vision-guided high-speed feeding and tray loading for flexible, multi-product production.", "productlist/10029.en-US.html"),
        ("inline", "Inline Inspection Equipment", "Inline appearance, dimensional and defect inspection connected to rejection and traceability.", "productlist/10030.en-US.html"),
    ],
}

DETAILS = {
    "monitor": {
        "zh": {
            "title": "从模腔状态到报警记录，完整覆盖每一次合模判断。",
            "body": "检测范围、软件逻辑与硬件接口围绕同一个生产节拍设计，既能发现异常，也能把异常转化为可执行的产线动作。",
            "groups": [
                (
                    "检测范围",
                    [
                        "合模前确认模穴、模芯与产品残留。",
                        "确认滑块位置、顶针折断和复位位置。",
                        "确认镶件是否到位、是否遗漏。",
                        "确认产品完全脱模、是否存在缺料。",
                        "确认产品尺寸、毛边和多穴产品残留。",
                        "确认多色产品的颜色组合是否正确。",
                        "支持安全门动作后自动复检。",
                        "可减少脱模剂使用和顶针顶出次数。",
                    ],
                ),
                (
                    "软件能力",
                    [
                        "全触摸屏控制，检测时间可低至 0.03 秒。",
                        "ROI 数量不受限制，灵敏度可独立调整。",
                        "AI 辅助获取图像与自动拍照时间。",
                        "支持矩形、椭圆和任意形状检测区域。",
                        "I/O 输出逻辑可按应用需求配置。",
                        "支持基准图添加和静态学习。",
                        "自动亮度矫正，降低环境光误报。",
                        "报警图像保留参数和 I/O 状态并可导出。",
                    ],
                ),
                (
                    "硬件与接口",
                    [
                        "最高支持 8 MP 黑白或彩色相机。",
                        "集成红外与白光双光源。",
                        "内置自动对焦镜头和景深整合。",
                        "5 个网口，可追加相机并预留 MES 接口。",
                        "6 路输出，包含报警、循环启动和顶针重顶。",
                        "内部隔离继电器可直接连接客户负载。",
                        "可选 SD 卡用于图像存储和程序升级。",
                    ],
                ),
            ],
            "media": [
                ("../cn/testimg/mjbh3.webp", "四相机与 ROI 检测界面", 820, 700),
                ("../cn/testimg/mjbh4.webp", "IMX-790 控制器与接口", 728, 524),
                ("../cn/testimg/mjbh7.webp", "V1 Pro 模具监视相机", 740, 540),
            ],
        },
        "en": {
            "title": "From mold state to alarm history, one complete close-cycle decision.",
            "body": "Inspection scope, software logic and hardware interfaces are designed around the same production rhythm, turning a detected anomaly into an actionable line response.",
            "groups": [
                (
                    "Inspection scope",
                    [
                        "Verify cavities, cores and residual parts before close.",
                        "Check slide position, broken ejector pins and reset position.",
                        "Confirm inserts are present and correctly positioned.",
                        "Verify complete ejection and detect short shots.",
                        "Check dimensions, flash and residual material in multi-cavity molds.",
                        "Verify colour combinations on multicolour parts.",
                        "Re-inspect automatically after the safety door operates.",
                        "Reduce release-agent use and ejector-pin re-stroke count.",
                    ],
                ),
                (
                    "Software",
                    [
                        "Full touchscreen control with inspection decisions as fast as 0.03 s.",
                        "Unlimited ROI count with independent sensitivity settings.",
                        "AI-assisted image acquisition and automatic capture timing.",
                        "Rectangular, elliptical and free-form inspection regions.",
                        "Configurable I/O output logic for each application.",
                        "Reference-image registration and static learning.",
                        "Automatic brightness correction to reduce ambient-light false alarms.",
                        "Alarm images retain parameters and I/O states and can be exported.",
                    ],
                ),
                (
                    "Hardware and I/O",
                    [
                        "Camera support up to 8 MP, monochrome or colour.",
                        "Integrated infrared and white dual lighting.",
                        "Built-in autofocus lens with in-house depth-of-field integration.",
                        "Five Ethernet ports with a reserved MES integration interface.",
                        "Six outputs including alarm, cycle start and ejector re-stroke.",
                        "Internally isolated relays connect directly to the customer load circuit.",
                        "Optional SD card for image storage and software updates.",
                    ],
                ),
            ],
            "media": [
                ("../cn/testimg/mjbh3.webp", "Four-camera and ROI inspection interface", 820, 700),
                ("../cn/testimg/mjbh4.webp", "IMX-790 controller and I/O interfaces", 728, 524),
                ("../cn/testimg/mjbh7.webp", "V1 Pro mold-monitoring camera", 740, 540),
            ],
        },
    },
    "connector": {
        "zh": {
            "title": "自动检测、尺寸判断与数据追溯，连接器全流程在线完成。",
            "body": "同一套检测平台覆盖连接器、端子、针脚与小型电子元器件，并支持单料带、双料带和多料带生产。",
            "groups": [
                (
                    "检测能力",
                    [
                        "全自动完成外观缺陷筛查与关键尺寸测量。",
                        "覆盖任意边缘间距、圆形连接器和端子间距。",
                        "兼容不同规格、不同类型的连接器。",
                        "检测结果可存储、查询、导出和趋势分析。",
                        "公差阈值可自定义，并自动判定合格状态。",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251212/6390114571828180473112177.webp", "单料带检测工位", 1600, 1124),
                ("../UserFiles/upload/image/20251212/6390114580247485748332846.webp", "双料带检测工位", 1600, 1125),
                ("../UserFiles/upload/image/20251212/6390114580251195803346938.webp", "多料带检测工位", 1600, 1125),
            ],
        },
        "en": {
            "title": "Inspection, dimensional judgment and traceability in one connector line.",
            "body": "One inspection platform covers connectors, terminals, pins and small electronic components across single-, double- and multi-strip production.",
            "groups": [
                (
                    "Inspection capability",
                    [
                        "Automatically screen cosmetic defects and measure critical dimensions.",
                        "Measure edge-to-edge spacing, circular connectors and terminal pitch.",
                        "Support connectors of different specifications and types.",
                        "Store, query, export and trend inspection results.",
                        "Set custom tolerance thresholds and judge conformity automatically.",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251212/6390114571828180473112177.webp", "Single-strip inspection station", 1600, 1124),
                ("../UserFiles/upload/image/20251212/6390114580247485748332846.webp", "Double-strip inspection station", 1600, 1125),
                ("../UserFiles/upload/image/20251212/6390114580251195803346938.webp", "Multi-strip inspection station", 1600, 1125),
            ],
        },
    },
    "strip": {
        "zh": {
            "title": "把尺寸、变形和缺料判断放进冲压节拍。",
            "body": "设备在冲压后直接检测料带，不增加额外生产周期。",
            "groups": [
                (
                    "核心能力",
                    [
                        "检测长度、高度、位置度、直径、内径和同心度。",
                        "识别变形、缺料、毛刺及外观缺陷。",
                        "检测速度可与冲压机同步。",
                        "结果实时可视化，参数与图像同步呈现。",
                        "标准流程与引导界面降低操作门槛。",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251212/6390112902333584171953095.webp", "Insert Molding 带料检测设备", 1600, 1255),
            ],
        },
        "en": {
            "title": "Put dimensional, deformation and short-shot judgment inside the stamping cycle.",
            "body": "The equipment inspects the strip directly after stamping without adding another production cycle.",
            "groups": [
                (
                    "Core capability",
                    [
                        "Measure length, height, position, diameter, bore and concentricity.",
                        "Identify deformation, missing material, burrs and cosmetic defects.",
                        "Synchronise inspection speed with the stamping press.",
                        "Display results, parameters and images in real time.",
                        "Guided workflows reduce setup and operating complexity.",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251212/6390112902333584171953095.webp", "Insert Molding strip inspection equipment", 1600, 1255),
            ],
        },
    },
    "plastic": {
        "zh": {
            "title": "产品脱模后立即完成多穴检测，不把缺陷带到下一步。",
            "body": "高速成像、同步频闪与 AI 判断在脱模瞬间联动。",
            "groups": [
                (
                    "检测能力",
                    [
                        "高速相机与同步频闪光源完成瞬时全检。",
                        "支持 16 穴产品全域检测。",
                        "多角度环形光源覆盖微小瑕疵和缺料。",
                        "AI 算法适配不同塑料件检测任务。",
                        "不良品可由机械手自动分类分拣。",
                        "检测数据实时对接 MES，支持追溯。",
                        "模块化结构可调节距离、高度和间距。",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251230/6390268539790000497674567.webp", "塑料件脱模在线检测画面", 1600, 900),
            ],
        },
        "en": {
            "title": "Inspect every cavity at ejection, before a defect reaches the next step.",
            "body": "High-speed imaging, synchronized strobe lighting and AI judgment work together at the moment the part leaves the mold.",
            "groups": [
                (
                    "Inspection capability",
                    [
                        "High-speed camera and synchronized strobe perform immediate full inspection.",
                        "Check all 16 cavities across the complete part area.",
                        "Multi-angle ring lighting exposes small flaws and short shots.",
                        "AI algorithms adapt to different plastic-part inspection tasks.",
                        "A robot can automatically classify and sort nonconforming parts.",
                        "Inspection data connects to MES for traceability.",
                        "Modular mounting adjusts distance, height and spacing.",
                    ],
                ),
            ],
            "media": [
                ("../UserFiles/upload/image/20251230/6390268539790000497674567.webp", "Inline inspection at plastic-part ejection", 1600, 900),
            ],
        },
    },
    "sorter": {
        "zh": {
            "title": "从多角度成像到自动分流，检测结果直接进入生产动作。",
            "body": "同一平台围绕上料、旋转、成像、判断与分拣组织流程，不同工件通过治具、光源和算法完成适配。",
            "groups": [
                (
                    "检测与判断",
                    [
                        "外观缺陷筛查与关键尺寸测量在同一节拍内完成。",
                        "同步轮或伺服旋转覆盖内外壁与微小表面特征。",
                        "按 OK、NG 与具体缺陷类型输出判断结果。",
                        "检测记录支持查询、导出与趋势分析。",
                    ],
                ),
                (
                    "上料与分拣",
                    [
                        "柔性上料系统适配不同形态和尺寸的零件。",
                        "良品自动下料，可对接后续包装工序。",
                        "不良品按缺陷类别进入独立下料通道。",
                        "治具、相机与光源可按工件组合配置。",
                    ],
                ),
                (
                    "项目适配",
                    [
                        "速度、精度与节拍以实际样品验证结果为准。",
                        "MES、剔除与产线接口按项目需求配置。",
                        "参数和检测模型可保存，便于换型与复用。",
                    ],
                ),
            ],
            "media": [
                ("../cn/testimg/lm1.webp", "Mic SXT 摄像头件检测工位", 685, 640),
                ("../cn/testimg/lm7.webp", "Mic DJ 电机配件检测工位", 690, 700),
                ("../cn/testimg/lm5.webp", "Mic JS 金属件检测工位", 690, 692),
            ],
        },
        "en": {
            "title": "From multi-angle imaging to automatic sorting, every result becomes a production action.",
            "body": "One platform organizes feeding, rotation, imaging, judgment and sorting. Tooling, lighting and algorithms are configured around the part.",
            "groups": [
                (
                    "Inspection and judgment",
                    [
                        "Cosmetic screening and critical dimensions complete in one cycle.",
                        "Synchronous-pulley or servo rotation exposes inner walls and fine surface features.",
                        "Results distinguish OK, NG and specific defect categories.",
                        "Inspection records support query, export and trend analysis.",
                    ],
                ),
                (
                    "Feeding and sorting",
                    [
                        "Flexible feeding accommodates different part shapes and sizes.",
                        "Good parts discharge automatically for downstream packaging.",
                        "Defects enter separate output channels by defect category.",
                        "Fixtures, cameras and lighting can be combined around the workpiece.",
                    ],
                ),
                (
                    "Project integration",
                    [
                        "Speed, accuracy and cycle time are verified with the actual sample.",
                        "MES, rejection and line interfaces are configured per project.",
                        "Recipes and inspection models can be stored and reused across changeovers.",
                    ],
                ),
            ],
            "media": [
                ("../cn/testimg/lm1.webp", "Mic SXT camera-part inspection station", 685, 640),
                ("../cn/testimg/lm7.webp", "Mic DJ motor-part inspection station", 690, 700),
                ("../cn/testimg/lm5.webp", "Mic JS metal-part inspection station", 690, 692),
            ],
        },
    },
}

LANG_SUFFIXES = [
    ("zh-CN", "", "简体中文"),
    ("en-US", ".en-US", "English (US)"),
    ("en-SG", ".en-SG", "English (SG)"),
    ("ja-JP", ".ja-JP", "日本語"),
    ("vi-VN", ".vi-VN", "Tiếng Việt"),
    ("th-TH", ".th-TH", "ไทย"),
    ("id-ID", ".id-ID", "Bahasa Indonesia"),
    ("ms-MY", ".ms-MY", "Bahasa Melayu"),
    ("ko-KR", ".ko-KR", "한국어"),
    ("ru-RU", ".ru-RU", "Русский"),
    ("es-MX", ".es-MX", "Español (MX)"),
    ("es-ES", ".es-ES", "Español (ES)"),
]


def e(value: str) -> str:
    return html.escape(value, quote=True)


def language_links(file: str, lang: str) -> str:
    path = Path(file)
    stem = path.name
    for suffix in (".en-US.html", ".html"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    links = []
    for code, suffix, label in LANG_SUFFIXES:
        current = ' aria-current="page"' if code == lang else ""
        links.append(
            f'<a href="{e(stem + suffix + ".html")}" hreflang="{code}" '
            f'lang="{code}"{current}>{e(label)}</a>'
        )
    return "".join(links)


def header(lang: str, file: str, title: str, family: str) -> str:
    zh = lang == "zh-CN"
    home = "../index.html" if zh else "../index.en-US.html"
    contact = "../contact.html" if zh else "../contact.en-US.html"
    products_label = "产品" if zh else "Products"
    tech = ("技术", "../index.html#technology") if zh else ("Technology", "../index.en-US.html#technology")
    apps = ("应用", "../index.html#applications") if zh else ("Applications", "../index.en-US.html#applications")
    contact_label = "联系" if zh else "Contact"
    quote = "获取报价" if zh else "Request a quote"
    menu = "菜单" if zh else "Menu"
    product_links = "".join(
        f'<a href="../{e(target)}"{" aria-current=\"page\"" if key == family else ""}>'
        f"<span>{e(label)}</span><small>{e(description)}</small></a>"
        for key, label, description, target in PRODUCT_MENU["zh" if zh else "en"]
    )
    return f"""
<header class="vp2-header" data-vp2-header>
  <nav class="vp2-nav" aria-label="{e(title)}">
    <a class="vp2-brand" href="{home}" aria-label="MAIBIDA">
      <img src="../UserFiles/upload/image/20260130/6390537782787865841043014.webp" width="339" height="112" alt="MAIBIDA"/>
    </a>
    <div class="vp2-desktop-nav">
      <details class="vp2-product-menu">
        <summary>{e(products_label)}</summary>
        <div class="vp2-product-popover">{product_links}</div>
      </details>
      <a href="{tech[1]}">{e(tech[0])}</a>
      <a href="{apps[1]}">{e(apps[0])}</a>
      <a href="{contact}">{e(contact_label)}</a>
    </div>
    <div class="vp2-header-actions">
      <details class="vp2-language">
        <summary>{"语言" if zh else "Language"}</summary>
        <div class="vp2-language-popover">{language_links(file, lang)}</div>
      </details>
      <a class="vp2-quote" href="{contact}">{e(quote)}</a>
      <details class="vp2-mobile-menu">
        <summary aria-label="{e(menu)}"><span></span></summary>
        <div class="vp2-mobile-popover">
          <a href="{home}#products">{e(products_label)}</a>
          <a href="{tech[1]}">{e(tech[0])}</a>
          <a href="{apps[1]}">{e(apps[0])}</a>
          <a href="{contact}">{e(contact_label)}</a>
          <a href="{contact}">{e(quote)}</a>
          {language_links(file, lang)}
        </div>
      </details>
    </div>
  </nav>
</header>
"""


def product_block(slug: str, entry: dict, lang_key: str, lang: str) -> str:
    data = entry[lang_key]
    is_en = lang == "en-US"
    contact = "../contact.en-US.html" if is_en else "../contact.html"
    terms = "../terms.en-US.html" if is_en else "../terms.html"
    detail_title = data.get(
        "dossier_title",
        "Specifications, diagrams and integration notes."
        if is_en
        else "参数、结构与集成说明。",
    )
    detail_body = data.get(
        "dossier_body",
        "The complete engineering record remains available below for evaluation and selection."
        if is_en
        else "页面下方保留完整的规格、图表与集成信息，方便评估与选型。",
    )
    detail_eyebrow = data.get(
        "dossier_eyebrow",
        "ENGINEERING FILE" if is_en else "工程档案",
    )
    hero_cta = "Discuss this application" if is_en else "沟通应用需求"
    detail_cta = "View engineering details" if is_en else "查看工程细节"
    stats = "".join(
        f'<div class="vp2-stat"><strong>{e(value)}</strong><span>{e(label)}</span></div>'
        for value, label in data["stats"]
    )
    features = "".join(
        f'<article class="vp2-feature"><small>{e(tag)}</small>'
        f"<h3>{e(title)}</h3><p>{e(body)}</p></article>"
        for title, body, tag in data["features"]
    )
    variants_data = data.get("variants", [])
    variants = ""
    if variants_data:
        variant_cards = "".join(
            f'<article class="vp2-variant"><strong>{e(name)}</strong><span>{e(scope)}</span>'
            f'<p>{e(speed)} · {e(accuracy)}</p></article>'
            for name, scope, speed, accuracy in variants_data
        )
        variants = f"""
  <section class="vp2-variants">
    <div class="vp2-wrap">
      <div class="vp2-section-intro">
        <p class="vp2-eyebrow">{e("CONFIGURATIONS" if is_en else "可配置型号")}</p>
        <h2>{e("One platform, tuned to the part." if is_en else "同一平台，按工件定制。")}</h2>
      </div>
      <div class="vp2-variant-grid">{variant_cards}</div>
    </div>
  </section>
"""
    specs_data = data.get("specs", [])
    specifications = ""
    if specs_data:
        spec_rows = "".join(
            f"<tr><th scope=\"row\">{e(label)}</th><td>{e(value)}</td></tr>"
            for label, value in specs_data
        )
        specifications = f"""
  <section class="vp2-specifications" aria-labelledby="vp2-spec-title">
    <div class="vp2-wrap">
      <div class="vp2-spec-layout">
        <div class="vp2-section-intro">
          <p class="vp2-eyebrow">{e("ENGINEERING SPECIFICATIONS" if is_en else "工程规格")}</p>
          <h2 id="vp2-spec-title">{e("Scope, performance and selection boundaries." if is_en else "范围、性能与选型边界。")}</h2>
          <p>{e("Reference values describe the platform and the Mic SXT baseline. The final configuration is selected around the actual part and production requirement." if is_en else "参考值说明平台能力与 Mic SXT 基准配置；最终方案围绕实际工件与生产要求确定。")}</p>
        </div>
        <div class="vp2-spec-table-wrap">
          <table class="vp2-spec-table">
            <tbody>{spec_rows}</tbody>
          </table>
        </div>
      </div>
      <p class="vp2-spec-note">{e("Values depend on the workpiece, fixture, lighting, parameters and accepted technical protocol." if is_en else "参数受工件、治具、光照、设定与技术协议约束，详见销售条款与技术声明。")} <a href="{terms}">{e("Technical disclaimer" if is_en else "技术声明")}</a></p>
    </div>
  </section>
"""
    detail = DETAILS.get(slug, {}).get(lang_key)
    detail_section = ""
    if detail:
        groups = "".join(
            f'<article class="vp2-detail-group"><h3>{e(group_title)}</h3><ul>'
            + "".join(f"<li>{e(item)}</li>" for item in group_items)
            + "</ul></article>"
            for group_title, group_items in detail["groups"]
        )
        media = "".join(
            f'<figure><img src="{e(src)}?v={VERSION}" '
            f'width="{width}" height="{height}" '
            f'loading="lazy" decoding="async" alt="{e(label)}"/>'
            f"<figcaption>{e(label)}</figcaption></figure>"
            for src, label, width, height in detail["media"]
        )
        media_block = f'<div class="vp2-detail-gallery">{media}</div>' if media else ""
        detail_section = f"""
  <section class="vp2-detail">
    <div class="vp2-wrap">
      <div class="vp2-section-intro">
        <p class="vp2-eyebrow">{e("PRODUCT DETAILS" if is_en else "产品细节")}</p>
        <h2>{e(detail["title"])}</h2>
        <p>{e(detail["body"])}</p>
      </div>
      <div class="vp2-detail-grid">{groups}</div>
      {media_block}
    </div>
  </section>
"""
    image_version = entry.get("image_version", VERSION)
    return f"""
{HOME_MARKER}
{header(lang, data["file"], data["title"], entry["family"])}
<main class="vp2-main">
  <section class="vp2-hero vp2-theme-{entry['theme']}" aria-labelledby="vp2-product-title">
    <div class="vp2-hero-copy">
      <p class="vp2-eyebrow">{e(data["eyebrow"])}</p>
      <h1 id="vp2-product-title">{e(data["title"])}</h1>
      <p class="vp2-lead">{e(data["lead"])}</p>
      <div class="vp2-actions">
        <a class="vp2-button" href="{contact}">{e(hero_cta)}</a>
        <a class="vp2-text-action" href="#vp2-details">{e(detail_cta)}</a>
      </div>
    </div>
    <figure class="vp2-hero-media">
      <img src="../cn/images/redesign/products/{entry["image"]}?v={image_version}"
        width="1600" height="1200" loading="eager" decoding="async" alt="{e(data["title"])}"/>
    </figure>
    <div class="vp2-stats">{stats}</div>
  </section>
  <section class="vp2-benefits" aria-label="{e(data["title"])}">
    <div class="vp2-wrap"><div class="vp2-feature-grid">{features}</div></div>
  </section>
{detail_section}
{variants}
{specifications}
  <section class="vp2-dossier-head" id="vp2-details">
    <div class="vp2-wrap">
      <p class="vp2-eyebrow">{e(detail_eyebrow)}</p>
      <h2>{e(detail_title)}</h2>
      <p>{e(detail_body)}</p>
    </div>
  </section>
<div class="vp2-legacy">
{HOME_END}
"""


def cta_block(lang: str) -> str:
    is_en = lang == "en-US"
    contact = "../contact.en-US.html" if is_en else "../contact.html"
    eyebrow = "CHOOSE WITH EVIDENCE" if is_en else "用样品验证选型"
    title = "Send the part. We will define the inspection." if is_en else "发送样品，我们共同定义检测方案。"
    body = (
        "Share the material, target defect, tolerance and cycle speed. MAIBIDA will recommend the platform and integration path."
        if is_en
        else "提供材料、目标缺陷、公差与生产节拍。迈必达将根据实际样品给出平台与集成建议。"
    )
    button = "Talk to an engineer" if is_en else "联系工程团队"
    return f"""
{CTA_MARKER}
</div>
<section class="vp2-bottom-cta">
  <div class="vp2-wrap">
    <p class="vp2-eyebrow">{e(eyebrow)}</p>
    <h2>{e(title)}</h2>
    <p>{e(body)}</p>
    <a class="vp2-button" href="{contact}">{e(button)}</a>
  </div>
</section>
{CTA_END}
"""


def remove_marked(source: str, start: str, end: str) -> str:
    return re.sub(
        rf"\s*{re.escape(start)}.*?{re.escape(end)}",
        "",
        source,
        flags=re.S,
    )


def add_body_classes(source: str, slug: str, theme: str) -> str:
    match = re.search(r"<body\b([^>]*)>", source, re.I)
    if not match:
        raise RuntimeError("body element missing")
    attrs = match.group(1)
    class_match = re.search(r'\bclass="([^"]*)"', attrs, re.I)
    classes = class_match.group(1).split() if class_match else []
    for class_name in ("vp2-page", f"vp2-{slug}", f"vp2-theme-{theme}"):
        if class_name not in classes:
            classes.append(class_name)
    replacement = f'class="{" ".join(classes)}"'
    if class_match:
        attrs = attrs[: class_match.start()] + replacement + attrs[class_match.end() :]
    else:
        attrs += f" {replacement}"
    return source[: match.start()] + f"<body{attrs}>" + source[match.end() :]


def insert_block(source: str, block: str, slug: str) -> str:
    source = remove_marked(source, HOME_MARKER, HOME_END)
    if "<!-- top结束 -->" in source:
        return source.replace("<!-- top结束 -->", "<!-- top结束 -->" + block, 1)
    if slug == "camera":
        return source.replace('<main class="vision-page">', block + '<main class="vision-page">', 1)
    return source.replace('<div keyid="info">', block + '<div keyid="info">', 1)


def normalize_legacy_specs(source: str) -> str:
    """Remove obsolete model tabs and normalize visible legacy structure."""
    source = re.sub(
        r'\s*<div class="ny-navs[^"]*">.*?</div>',
        "",
        source,
        count=1,
        flags=re.S,
    )
    source = re.sub(
        r'\s*<script\b[^>]*>(?:(?!</script>).)*?\.ny-navs'
        r'(?:(?!</script>).)*?</script>',
        "",
        source,
        count=1,
        flags=re.S | re.I,
    )
    return re.sub(
        r'<h1(?![^>]*\bid="vp2-product-title")[^>]*>.*?</h1>',
        lambda match: match.group(0)
        .replace("<h1", "<h2", 1)
        .replace("</h1>", "</h2>", 1),
        source,
        flags=re.S | re.I,
    )


def remove_legacy_return_control(source: str) -> str:
    source = re.sub(
        r'\s*<div class="float-sild">.*?</div>',
        "",
        source,
        count=1,
        flags=re.S,
    )
    return re.sub(
        r"\s*<script>\s*function scrollToTop\(\)\s*\{.*?</script>",
        "",
        source,
        count=1,
        flags=re.S,
    )


def insert_cta(source: str, block: str) -> str:
    source = re.sub(
        rf"(?:\s*</div>)*\s*{re.escape(CTA_MARKER)}.*?{re.escape(CTA_END)}",
        "",
        source,
        flags=re.S,
    )
    return source.replace('<div class="foot">', block + '<div class="foot">', 1)


def add_assets(source: str) -> str:
    source = re.sub(
        r"\s*<!--\s*(?:/)?VP2 ASSETS\s*-->",
        "",
        source,
        flags=re.I,
    )
    source = re.sub(
        r'\s*<link[^>]*href="[^"]*vision-products\.css[^"]*"[^>]*>',
        "",
        source,
        flags=re.I,
    )
    source = re.sub(
        r'\s*<script[^>]*src="[^"]*vision-products\.js[^"]*"[^>]*></script>',
        "",
        source,
        flags=re.I,
    )
    assets = f"""
<!-- VP2 ASSETS -->
<link rel="stylesheet" href="../cn/css/vision-products.css?v={VERSION}"/>
<!-- /VP2 ASSETS -->
"""
    source = source.replace("</head>", assets + "</head>", 1)
    source = source.replace(
        "</body>",
        f'<script src="../cn/js/vision-products.js?v={VERSION}" defer></script>\n</body>',
        1,
    )
    return source


def main() -> None:
    for slug, entry in PAGES.items():
        for lang_key in ("zh", "en"):
            lang = "zh-CN" if lang_key == "zh" else "en-US"
            path = ROOT / entry[lang_key]["file"]
            source = path.read_text(encoding="utf-8")
            source = remove_marked(source, CTA_MARKER, CTA_END)
            source = add_body_classes(source, slug, entry["theme"])
            source = re.sub(r'<h1 class="sr-h1">.*?</h1>', "", source, count=1, flags=re.S)
            source = insert_block(source, product_block(slug, entry, lang_key, lang), slug)
            source = normalize_legacy_specs(source)
            source = remove_legacy_return_control(source)
            source = insert_cta(source, cta_block(lang))
            source = add_assets(source)
            source = source.rstrip() + "\n"
            path.write_text(source, encoding="utf-8")
            print(f"built {entry[lang_key]['file']}")


if __name__ == "__main__":
    main()
