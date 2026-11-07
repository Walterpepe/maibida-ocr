$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$src=Join-Path $root 'product\10032.html'
$html=[IO.File]::ReadAllText($src)
$t=[ordered]@{
'迈必达IMX-790模具监视器支持多相机、AI图像采集和ROI检测，用于注塑模具保护、镶件到位、产品残留及脱模状态检测。'='The MAIBIDA IMX-790 Mold Monitor supports multiple cameras, AI image acquisition and ROI inspection for injection mold protection, insert placement, residual-part and ejection-status checks.'
'昆山迈必达智能设备有限公司专注机器视觉光源与工业在线检测设备，集研发、生产、销售于一体，为制造业提供视觉检测、模具监视、智能筛选与自动化上料一体化解决方案。'='Kunshan Maibida Intelligent Equipment Co., Ltd. develops, manufactures and supplies machine vision lighting and inline inspection equipment, delivering integrated vision inspection, mold monitoring, intelligent sorting and automated feeding solutions.'
'支持搭载最高800万像素相机，集成一体化红外/白光双光源，可选择黑白&彩色模式，精准呈现图像细节；内置 12 倍可调自动对焦镜头，无需手动调节，即可快速锁定不同距离的拍摄目标，具有专利技术的景深整合技术，大幅提升操作效率；'='Supports cameras up to 8 MP with integrated infrared and white dual lighting, plus monochrome and color modes for detailed imaging. A built-in 12× adjustable autofocus lens quickly locks onto targets at different distances, while patented depth-of-field integration improves operating efficiency.'
'集中监控系统可实现模具监视器数据的集中采集及大数据看板功能，对模具监视器数据进行实时监控，并通过集中监控程序对接客户mes系统。'='The centralized monitoring system collects Mold Monitor data into a production dashboard, provides real-time status monitoring and connects with the customer MES through centralized monitoring software.'
'防止模具损坏、减少模具维修费用，保证产品交期，降低生产成本，提高生产效率'='Prevent mold damage, reduce repair costs, protect delivery schedules, lower production costs and improve efficiency.'
'参数设置、模板编辑、算法设置等都可设置独立的用户密码，避免无关人员误操作；'='Set separate user passwords for parameter configuration, template editing and algorithm settings to prevent unauthorized changes.'
'报警图片中保存参数配置、报警时IO输出状态等参数，并可一键导出报告至U盘。'='Alarm images retain configuration data and I/O output status; reports can be exported to a USB drive with one click.'
'具有自动亮度矫正功能，可避免自然光线条件下亮度强弱变化导致的误报；'='Automatic brightness correction reduces false alarms caused by changes in ambient light.'
'可手动进行添加基准图，在设置灵敏度设置页内进行静态学习基准图；'='Add reference images manually and perform static reference-image learning from the sensitivity settings page.'
'选配SD卡，SD卡可以用于存储图片，亦可进行程序升级和I/O逻辑配置更新；'='An optional SD card stores images and supports program upgrades and I/O logic configuration updates.'
'配备智能自动对焦功能，快速锁定目标主体，确保图像清晰锐利。'='Intelligent autofocus locks onto the target quickly for clear, sharp images.'
'支持矩形、椭圆及任意形状的检测区域，适应各种复杂模具；'='Supports rectangular, elliptical and free-form inspection regions for complex molds.'
'支持最高800万像素拍摄，可选择黑白或彩色模式，精准呈现图像细节。'='Supports imaging up to 8 MP in monochrome or color for precise image detail.'
'减少顶针顶出次数，提升注塑成型周期，'='Reduce ejector-pin strokes and shorten the injection molding cycle,'
'安全门开关消除报警、'='Clear alarms with the safety-door switch,'
'安全门动作自动复检'='automatically re-inspect after safety-door operation'
'合模前进行模穴、模芯、产品残留确认'='Check mold cavities, cores and residual parts before mold closing'
'滑块位置、顶针折断和复位位置确认'='Verify slide position, broken ejector pins and reset position'
'镶件是否到位和遗漏检测'='Detect missing or incorrectly positioned inserts'
'产品是否完全脱模、产品是否缺料检测'='Verify complete ejection and detect short shots'
'产品尺寸是否合格、产品毛边检测'='Check dimensions and detect flash or burrs'
'多穴产品是否缺失和残留检测'='Detect missing or residual parts in multi-cavity molds'
'多色产品混色是否正确检测'='Verify correct color combinations on multicolor parts'
'减少脱模剂使用，适用于脱模困难的产品'='Reduce release-agent use for difficult-to-eject parts'
'集成一体化双光源，红外光/白光可以满足更多场景应用。'='Integrated infrared and white dual lighting supports a wider range of applications.'
'根据客户生产场景提供多种安装方式。'='Multiple mounting options are available for different production environments.'
'每个检测区域可设置单独的灵敏度及检测面积；'='Set sensitivity and inspection area independently for each region.'
'检测逻辑中的IO输出可根据使用的需求更改；'='Configure I/O outputs in the inspection logic to match application requirements.'
'可独立调整ROI灵敏度，ROI数量不受限制；'='Adjust ROI sensitivity independently with no fixed limit on the number of ROIs.'
'AI获取图像及自动拍照时间;'='AI-assisted image acquisition and automatic capture timing;'
'IO输入：每路独立输入，接线自由方便；'='I/O inputs: independent channels for flexible, convenient wiring;'
'IO输出：增加至6路输出，增加报警外接输出、循环启动、顶针再顶出功能接口；'='I/O outputs: six outputs including external alarm, cycle start and ejector re-stroke interfaces;'
'IO直接内部隔离继电器，可直接连接客户负载电路；'='Internally isolated I/O relays connect directly to the customer load circuit;'
'增强锐度、HDR、对比度、亮度、饱和度、Gamma校正等'='Sharpness enhancement, HDR, contrast, brightness, saturation and gamma correction'
'色彩校正矩阵、彩色/黑白转换'='Color correction matrix and color/monochrome conversion'
'焦距调节、图像信号处理器'='Focal-length adjustment and image signal processor'
'自动对焦/手动触摸对焦'='Autofocus / manual touch focus'
'白色/红外光源（双光组合）'='White / infrared lighting (dual-light combination)'
'黑白/彩色（双色）'='Monochrome / color'
'最高支持800万'='Up to 8 MP'
'10–12X无极变倍'='10–12× continuous zoom'
'3D降噪'='3D noise reduction'
'自动曝光、自动白平衡'='Auto exposure and auto white balance'
'IMX-790模具监视器'='IMX-790 Mold Monitor'
'模具监视器用途及检测内容'='Mold Monitor Applications and Inspection Tasks'
'模具监视保护器检测内容'='Mold protection inspection tasks'
'模具监视保护器'='Mold Monitor and Protection System'
'注塑机模具保护  |  InsertMolding检测解决方案  |  镶件注塑检测方案  |  注塑机取出模外高速检测系统'='Injection Mold Protection | Insert Molding Inspection | Insert Placement Inspection | High-Speed Out-of-Mold Inspection'
'集中监控系统'='Centralized Monitoring System'
'动作监视流程'='Machine-Cycle Monitoring Workflow'
'V1PRO 模保相机'='V1 Pro Mold Monitoring Camera'
'高分辨率'='High Resolution'
'内置光源'='Built-in Lighting'
'自动对焦'='Autofocus'
'软件功能'='Software Features'
'硬件优势'='Hardware Advantages'
'图像质量调节'='Image Quality Adjustment'
'曝光与白平衡'='Exposure and White Balance'
'色彩处理'='Color Processing'
'光学与图像捕捉'='Optics and Image Capture'
'降噪与增强'='Noise Reduction and Enhancement'
'规格参数'='Specifications'
'sensor品牌'='Sensor Brand'
'分辨率'='Resolution'
'帧率'='Frame Rate'
'彩色支持'='Color Support'
'镜头'='Lens'
'对焦方式'='Focus Method'
'网口'='Ethernet Port'
'网络标准'='Network Standard'
'电源/功率'='Power Supply / Power'
'光源'='Lighting'
'项目'='Item'
'参数'='Specification'
'技术参数'='Technical Specifications'
'应用案例'='Application Examples'
'产品介绍'='Product Overview'
'产品参数'='Specifications'
'产品中心'='Products'
'模具监视器'='Mold Monitor'
'视觉传感器'='Vision Sensors'
'视觉筛选机'='Vision Sorting Machine'
'柔性上料摆盘机'='Flexible Feeding System'
'在线检测设备'='Inline Inspection Equipment'
'连接器在线检测设备'='Connector Inline Inspection Equipment'
'HDMI拉料检测设备'='HDMI Strip-Feed Inspection Equipment'
'塑料件在线检测设备'='Plastic Parts Inline Inspection Equipment'
'联系我们'='Contact Us'
'语言 / Language'='Language'
'降低生产成本'='Lower Production Costs'
'提高生产效率'='Improve Production Efficiency'
'千兆以太网'='Gigabit Ethernet'
'视频中心'='Video Center'
'MAIBIDA · 智造未来'='MAIBIDA · Intelligent Manufacturing for the Future'
'客户服务热线：'='Customer Service:'
'官方邮箱：'='Email:'
'昆山市经济技术开发区杜鹃路555号C2栋7层701号'='Room 701, 7/F, Building C2, No. 555 Dujuan Road, Kunshan Economic & Technological Development Zone, Jiangsu, China'
'昆山迈必达智能设备有限公司'='Kunshan Maibida Intelligent Equipment Co., Ltd.'
'© 2026 昆山迈必达智能设备有限公司 All Rights Reserved.'='© 2026 Kunshan Maibida Intelligent Equipment Co., Ltd. All Rights Reserved.'
'返回顶部'='Back to Top'
'尺寸安装图.png'='Dimension and installation drawing'
'技术参数.png'='Technical specifications'
'模保运转流程.png'='Mold Monitor operating workflow'
'中国'='China'
'苏ICP备'='Jiangsu ICP Registration'
}
foreach($e in ($t.GetEnumerator()|Sort-Object {$_.Key.Length} -Descending)){$html=$html.Replace($e.Key,$e.Value)}
$html=$html.Replace('•  全触摸屏控制，操作简单易用；处理速度快，根据区域的设定系统检测时间可达到0.03秒;','• Full touchscreen control with simple operation and inspection times as fast as 0.03 seconds, depending on ROI settings;')
$html=$html.Replace('•  体积轻巧，手持操作方便，主机配备5个Ethernet Port，根据生产需求灵活追加相机以及预留对接MES系统接口；','• Compact and easy to handle, with five Ethernet ports for additional cameras and a reserved MES integration interface;')
$html=$html.Replace('支持搭载最高800万像素相机，集成一体化红外/白光双Lighting，可选择黑白&amp;彩色模式，精准呈现图像细节；内置 12 倍可调AutofocusLens，无需手动调节，即可快速锁定不同距离的拍摄目标，具有专利技术的景深整合技术，大幅提升操作效率；','Supports cameras up to 8 MP with integrated infrared and white dual lighting and monochrome or color modes. The built-in 12× autofocus lens and patented depth-of-field integration improve setup speed and image consistency;')
$html=$html.Replace('Software Features•  全触摸屏控制，操作简单易用；处理速度快，根据区域的设定系统检测时间可达到0.03秒;•Adjust ROI sensitivity independently with no fixed limit on the number of ROIs.•AI获取图像及','MAIBIDA Mold Monitor software interface and ROI inspection tools')
$html=$html.Replace('Hardware Advantages•  体积轻巧，手持操作方便，主机配备5个Ethernet Port，根据生产需求灵活追加相机以及预留对接MES系统接口；•支持搭载最高800万像素相机，集成一体化红外/白光','MAIBIDA Mold Monitor controller, camera ports and integrated dual lighting')
$html=$html.Replace('V1 Pro Mold Monitoring CameraHigh ResolutionSupports imaging up to 8 MP in monochrome or color for precise image detail.Built-in LightingIntegrated infrared and white dual lighting supports a wider range of applications.自动对','V1 Pro mold monitoring camera with 8 MP imaging, dual lighting and autofocus')
$html=$html.Replace('Mold Monitor 在线检测 非标自动化 视觉检测 CCD在线检测 注塑机模具保护','Mold Monitor, mold protection, custom automation, machine vision inspection, injection molding')
$html=$html.Replace('"name": "首页"','"name": "Home"').Replace('"description":"工业视觉模具保护设备"','"description":"Industrial vision system for injection mold protection"').Replace('"name":"迈必达"','"name":"MAIBIDA"')
$html=$html.Replace('<b class="s3">检测内容</b>','<b class="s3">Inspection Tasks</b>')
$html=[regex]::Replace($html,'alt="Software Features[^"]*"','alt="MAIBIDA Mold Monitor software interface and ROI inspection tools"',1)
$html=[regex]::Replace($html,'alt="Hardware Advantages[^"]*"','alt="MAIBIDA Mold Monitor controller, camera ports and integrated dual lighting"',1)
$html=$html.Replace('<html lang="zh-CN">','<html lang="en-US">').Replace('content="zh_CN" property="og:locale"','content="en_US" property="og:locale"')
$html=[regex]::Replace($html,'<title>[\s\S]*?</title>','<title>IMX-790 Mold Monitor &amp; Mold Protection | MAIBIDA</title>',1)
$html=[regex]::Replace($html,'<meta content="[^"]*" name="description"','<meta content="Protect injection molds with the MAIBIDA IMX-790 Mold Monitor. Detect inserts, residual parts, ejection status and mold-closing risks in real time." name="description"',1)
$html=[regex]::Replace($html,'<meta content="[^"]*" name="keywords"','<meta content="mold monitor, mold protection, injection mold monitoring, prevent mold collision, IMX-790" name="keywords"',1)
$html=$html.Replace('https://www.maibida.com/product/10032.html','https://www.maibida.com/product/10032.en-US.html').Replace('../index.html','../index.en-US.html').Replace('../product/10032.html','../product/10032.en-US.html').Replace('../product/smart-camera.html','../product/smart-camera.en-US.html')
foreach($id in '10029','10030','10034','10036','10039'){$html=$html.Replace("../productlist/$id.html","../productlist/$id.en-US.html")}
$html=[regex]::Replace($html,'<a aria-current="page" class="active" href="\.\./product/10032\.en-US\.html" hreflang="zh-CN" lang="zh-CN">简体中文</a>','<a href="../product/10032.html" hreflang="zh-CN" lang="zh-CN">简体中文</a>')
$html=$html.Replace('<a href="../product/10032.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>','<a aria-current="page" class="active" href="../product/10032.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>')
[IO.File]::WriteAllText((Join-Path $root 'product\10032.en-US.html'),$html,[Text.UTF8Encoding]::new($false))
foreach($market in @(@{Code='en-SG';Og='en_SG';Name='Singapore';Label='English (Singapore)'},@{Code='en-AU';Og='en_AU';Name='Australia';Label='English (Australia)'})){
 $r=$html.Replace('en-US',$market.Code).Replace('en_US',$market.Og)
 $regionalDescription='MAIBIDA IMX-790 Mold Monitor for '+$market.Name+' manufacturers detects inserts, residual parts and ejection status to protect injection molds.'
 $r=[regex]::Replace($r,'<meta content="[^"]*" name="description"','<meta content="'+$regionalDescription+'" name="description"',1)
 $r=$r.Replace('aria-current="page" class="active" href="../product/10032.'+$market.Code+'.html" hreflang="'+$market.Code+'" lang="'+$market.Code+'">English (US)</a>','href="../product/10032.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>')
 $r=$r.Replace('<a href="../product/10032.'+$market.Code+'.html" hreflang="'+$market.Code+'" lang="'+$market.Code+'">'+$market.Label+'</a>','<a aria-current="page" class="active" href="../product/10032.'+$market.Code+'.html" hreflang="'+$market.Code+'" lang="'+$market.Code+'">'+$market.Label+'</a>')
 [IO.File]::WriteAllText((Join-Path $root ('product\10032.'+$market.Code+'.html')),$r,[Text.UTF8Encoding]::new($false))
}
Write-Output 'Created product/10032 English market pages'
