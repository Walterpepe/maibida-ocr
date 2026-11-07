$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'index.html'
$html = [IO.File]::ReadAllText($source)

$translations = [ordered]@{
  '模具监视器与工业视觉检测设备厂家｜迈必达' = 'Mold Monitors & Machine Vision Inspection | MAIBIDA'
  '昆山迈必达智能设备有限公司专注模具监视器、CCD在线检测设备、视觉筛选机及工业机器视觉解决方案，支持注塑模具保护、连接器与塑料件在线检测。' = 'MAIBIDA supplies mold monitors, vision sensors and inline inspection equipment for mold protection, automated quality inspection and parts production.'
  '模具监视器  在线检测  非标自动化  视觉检测 CCD在线检测 注塑机模具保护' = 'mold monitor, machine vision inspection, inline inspection equipment, mold protection, industrial automation'
  '昆山迈必达智能设备有限公司 - 机器视觉光源与工业在线检测设备制造商' = 'MAIBIDA - Mold Monitors and Machine Vision Inspection Equipment'
  '昆山迈必达智能设备有限公司' = 'Kunshan Maibida Intelligent Equipment Co., Ltd.'
  '迈必达工业视觉检测设备' = 'MAIBIDA Machine Vision Inspection Equipment'
  '产品中心' = 'Products'
  '模具监视器' = 'Mold Monitor'
  '视觉传感器' = 'Vision Sensors'
  '视觉筛选机' = 'Vision Sorting Machines'
  '柔性上料摆盘机' = 'Flexible Feeding Systems'
  '在线检测设备' = 'Inline Inspection Equipment'
  '连接器在线检测设备' = 'Connector Inline Inspection Equipment'
  'HDMI拉料检测设备' = 'HDMI Strip-Feed Inspection Equipment'
  '塑料件在线检测设备' = 'Plastic Parts Inline Inspection Equipment'
  '语言 / Language' = 'Language'
  '工业机器视觉检测与自动化解决方案' = 'Machine Vision Inspection and Automation Solutions'
  '昆山迈必达智能设备有限公司专注模具监视器、AI视觉传感器、视觉筛选机、柔性上料摆盘机及在线检测设备，为注塑、连接器、电子元器件和精密零部件生产提供稳定、高效的机器视觉检测方案。' = 'MAIBIDA develops mold monitors, AI vision sensors, vision sorting machines, flexible feeding systems and inline inspection equipment for injection molding, connectors, electronic components and precision parts production.'
  '对模穴、模芯、镶件、顶针、产品残留和脱模状态进行实时监视，降低模具损坏风险。' = 'Monitor mold cavities, cores, inserts, ejector pins, residual parts and ejection status in real time to reduce the risk of mold damage.'
  '集成AI视觉能力与多种检测工具，适用于字符、外观、位置、数量及有无检测。' = 'Combine AI vision with multiple inspection tools for character, appearance, position, count and presence checks.'
  '面向多种工业零部件完成外观缺陷、尺寸检测和良品、不良品自动分拣。' = 'Inspect appearance and dimensions, then automatically sort conforming and nonconforming industrial parts.'
  '结合视觉定位与并联机器人，实现多规格产品的柔性上料、抓取、分拣和摆盘。' = 'Combine vision guidance with delta robots for flexible feeding, picking, sorting and tray loading across multiple product sizes.'
  '支持连接器、冲压料带、Insert Molding和塑料件的高速在线视觉检测。' = 'Enable high-speed inline vision inspection of connectors, stamped strips, insert-molded components and plastic parts.'
  '查看产品 →' = 'View Product →'
  '多场景视觉检测' = 'Inspection for Multiple Applications'
  '覆盖外观、尺寸、字符、位置、缺料、毛刺和装配状态检测。' = 'Inspect appearance, dimensions, characters, position, missing material, burrs and assembly status.'
  '柔性自动化集成' = 'Flexible Automation Integration'
  '根据产品规格、生产节拍和现场条件配置相机、光源与自动化机构。' = 'Configure cameras, lighting and automation around product specifications, cycle time and site conditions.'
  '生产数据可追溯' = 'Traceable Production Data'
  '支持检测结果、报警图片与生产数据保存，为质量分析提供依据。' = 'Store inspection results, alarm images and production data to support quality analysis and traceability.'
  '返回顶部' = 'Back to Top'
}

foreach ($entry in ($translations.GetEnumerator() | Sort-Object { $_.Key.Length } -Descending)) {
  $html = $html.Replace($entry.Key, $entry.Value)
}

$html = $html.Replace('<html lang="zh-CN">', '<html lang="en-US">')
$html = $html.Replace('content="zh_CN" property="og:locale"', 'content="en_US" property="og:locale"')
$html = $html.Replace('"inLanguage": "zh-CN"', '"inLanguage": "en-US"')
$html = $html.Replace('"availableLanguage": [
      "zh-CN"
     ]', '"availableLanguage": [
      "en-US"
     ]')
$html = $html.Replace('href="index.html"', 'href="index.en-US.html"')
$html = $html.Replace('href="product/10032.html"', 'href="product/10032.en-US.html"')
$html = $html.Replace('href="product/smart-camera.html"', 'href="product/smart-camera.en-US.html"')
$html = $html.Replace('href="productlist/10039.html"', 'href="productlist/10039.en-US.html"')
$html = $html.Replace('href="productlist/10029.html"', 'href="productlist/10029.en-US.html"')
$html = $html.Replace('href="productlist/10030.html"', 'href="productlist/10030.en-US.html"')
$html = $html.Replace('href="productlist/10034.html"', 'href="productlist/10034.en-US.html"')
$html = $html.Replace('href="productlist/10036.html"', 'href="productlist/10036.en-US.html"')
$html = [regex]::Replace($html, '<a aria-current="page" class="active" href="index\.en-US\.html" hreflang="zh-CN" lang="zh-CN">简体中文</a>', '<a href="index.html" hreflang="zh-CN" lang="zh-CN">简体中文</a>')
$html = $html.Replace('<a href="index.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>', '<a aria-current="page" class="active" href="index.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>')
$html = $html.Replace('<link href="https://www.maibida.com/index.html" rel="canonical"/>', '<link href="https://www.maibida.com/index.en-US.html" rel="canonical"/>')
$html = $html.Replace('https://www.maibida.com/index.html#', 'https://www.maibida.com/index.en-US.html#')
$html = $html.Replace('"url": "https://www.maibida.com/index.html"', '"url": "https://www.maibida.com/index.en-US.html"')
[IO.File]::WriteAllText((Join-Path $root 'index.en-US.html'), $html, [Text.UTF8Encoding]::new($false))

foreach ($market in @(
  @{Code='en-SG'; Og='en_SG'; Name='Singapore'},
  @{Code='en-AU'; Og='en_AU'; Name='Australia'}
)) {
  $regional = $html.Replace('en-US', $market.Code).Replace('en_US', $market.Og)
  $regional = $regional.Replace('aria-current="page" class="active" href="index.' + $market.Code + '.html" hreflang="' + $market.Code + '" lang="' + $market.Code + '">English (US)</a>', 'href="index.en-US.html" hreflang="en-US" lang="en-US">English (US)</a>')
  $label = if ($market.Code -eq 'en-SG') {'English (Singapore)'} else {'English (Australia)'}
  $regional = $regional.Replace('<a href="index.' + $market.Code + '.html" hreflang="' + $market.Code + '" lang="' + $market.Code + '">' + $label + '</a>', '<a aria-current="page" class="active" href="index.' + $market.Code + '.html" hreflang="' + $market.Code + '" lang="' + $market.Code + '">' + $label + '</a>')
  $regional = $regional.Replace('MAIBIDA supplies mold monitors, vision sensors and inline inspection equipment for mold protection, automated quality inspection and parts production.', 'MAIBIDA supplies mold monitors, vision sensors and inline inspection equipment for automated quality control in ' + $market.Name + ' manufacturing.')
  [IO.File]::WriteAllText((Join-Path $root ('index.' + $market.Code + '.html')), $regional, [Text.UTF8Encoding]::new($false))
}

Write-Output 'Created index.en-US.html, index.en-SG.html and index.en-AU.html'
