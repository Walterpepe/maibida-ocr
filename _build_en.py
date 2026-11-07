# -*- coding: utf-8 -*-
"""
micromat-site 英文版生成管线
- 扫描站点所有 HTML（不含 en/）
- 镜像到 en/，重写资源/链接路径
- 翻译可见文本（导航/页脚/按钮/meta/标题/正文）
- 在中英文页面顶部各插入语言切换下拉
"""
import os, re, sys, io, shutil, html as ihtml
from pathlib import Path

ROOT = Path(r"D:\WorkBuddy20260919\2026-10-29-21-31-27\micromat-site")
EN   = ROOT / "en"

# ============== 工业领域核心术语表（必须精准）==============
TERMS = {
    # 模具监视保护器相关
    "模具监视保护器": "Mold Monitor & Protector",
    "模具保护器": "Mold Protector",
    "模具监视器": "Mold Monitor",
    "注塑机": "Injection Molding Machine",
    "注塑模具": "Injection Mold",
    "注塑": "Injection Molding",
    "镶件注塑": "Insert Molding",
    "InsertMolding": "Insert Molding",
    "顶针": "Ejector Pin",
    "顶出": "Ejection",
    "合模": "Mold Closing",
    "开模": "Mold Opening",
    "锁模": "Mold Clamping",
    "模内": "In-Mold",
    "模外": "Out-of-Mold",
    "高速检测": "High-Speed Inspection",

    # 视觉/检测
    "视觉传感器": "Vision Sensor",
    "智能相机": "Smart Camera",
    "工业相机": "Industrial Camera",
    "机器视觉": "Machine Vision",
    "视觉检测": "Vision Inspection",
    "在线检测": "Inline Inspection",
    "CCD在线检测": "CCD Inline Inspection",
    "CCD": "CCD",
    "AOI": "AOI (Automated Optical Inspection)",
    "光学分拣": "Optical Sorting",
    "六面光学分拣机": "6-Sided Optical Sorting Machine",
    "光学筛选机": "Optical Sorting Machine",
    "自动光学检测": "Automated Optical Inspection",
    "缺陷检测": "Defect Inspection",
    "尺寸检测": "Dimensional Inspection",
    "外观检测": "Appearance Inspection",
    "表面缺陷": "Surface Defect",
    "图像识别": "Image Recognition",
    "图像采集": "Image Acquisition",
    "图像处理": "Image Processing",
    "算法": "Algorithm",
    "AI算法": "AI Algorithm",
    "深度学习": "Deep Learning",
    "嵌入式": "Embedded",
    "像素": "Pixel",
    "万像素": "MP",
    "150万": "1.5MP",
    "200万": "2MP",
    "500万": "5MP",
    "800万": "8MP",
    "1200万": "12MP",
    "2000万": "20MP",
    "分辨率": "Resolution",
    "焦距": "Focal Length",
    "镜头": "Lens",
    "自动对焦": "Auto Focus",
    "景深": "Depth of Field",
    "视野": "Field of View (FOV)",
    "FOV": "FOV",

    # 光源
    "机器视觉光源": "Machine Vision Lighting",
    "光源": "Light Source / Illumination",
    "条形光源": "Bar Light",
    "环形光源": "Ring Light",
    "面光源": "Backlight / Area Light",
    "同轴光源": "Coaxial Light",
    "点光源": "Spot Light",
    "红外光": "Infrared (IR) Light",
    "白光": "White Light",
    "紫外光": "UV Light",
    "补光": "Fill Light",
    "LED": "LED",

    # 上料/分拣
    "柔性上料": "Flexible Feeding",
    "振动盘": "Vibratory Bowl Feeder",
    "柔性振动盘": "Flexible Vibratory Feeder",
    "上料": "Feeding",
    "下料": "Unloading",
    "供料": "Material Feeding",
    "送料": "Feeding",
    "分拣": "Sorting",
    "分选": "Sorting",
    "摆盘": "Tray Arrangement",
    "拾取": "Pick-and-Place",
    "抓取": "Gripping",
    "机械手": "Robotic Arm",
    "机器人": "Robot",
    "并联机器人": "Delta Robot",
    "串联机器人": "Articulated Robot",
    "SCARA": "SCARA Robot",

    # 工件
    "连接器": "Connector",
    "端子": "Terminal",
    "PIN针": "Pin",
    "插针": "Pin",
    "塑料件": "Plastic Part",
    "塑胶件": "Plastic Part",
    "金属件": "Metal Part",
    "五金件": "Hardware Part",
    "冲压件": "Stamped Part",
    "注塑件": "Injection-Molded Part",
    "压铸件": "Die-Cast Part",
    "工件": "Workpiece",
    "产品": "Product",
    "零件": "Component / Part",
    "HDMI": "HDMI",
    "USB": "USB",
    "Type-C": "USB Type-C",
    "FPC": "FPC",
    "PCB": "PCB",
    "PCBA": "PCBA",

    # 软件/系统
    "软件功能": "Software Features",
    "硬件优势": "Hardware Advantages",
    "技术参数": "Specifications",
    "应用案例": "Application Cases",
    "集中监控": "Centralized Monitoring",
    "数据采集": "Data Acquisition",
    "看板": "Dashboard",
    "报表": "Report",
    "导出": "Export",
    "导入": "Import",
    "用户管理": "User Management",
    "权限管理": "Permission Management",
    "密码": "Password",
    "登录": "Login",
    "设置": "Settings",
    "配置": "Configuration",
    "模板": "Template",
    "基准图": "Reference Image",
    "标准图": "Standard Image",
    "灵敏度": "Sensitivity",
    "检测区域": "ROI (Region of Interest)",
    "ROI": "ROI",
    "感兴趣区域": "Region of Interest",
    "IO": "I/O",
    "IO输入": "I/O Input",
    "IO输出": "I/O Output",
    "继电器": "Relay",
    "隔离继电器": "Isolated Relay",
    "报警": "Alarm",
    "误报": "False Alarm",
    "漏报": "Missed Detection",
    "SD卡": "SD Card",
    "U盘": "USB Drive",
    "网口": "Ethernet Port",
    "以太网": "Ethernet",
    "通讯": "Communication",
    "MES": "MES",
    "MES系统": "MES System",
    "ERP": "ERP",
    "SCADA": "SCADA",
    "PLC": "PLC",
    "工控机": "Industrial PC",
    "触摸屏": "Touch Screen",
    "HMI": "HMI",
    "操作界面": "User Interface",
    "UI": "UI",

    # 性能
    "处理速度": "Processing Speed",
    "检测速度": "Inspection Speed",
    "检测精度": "Inspection Accuracy",
    "精度": "Accuracy",
    "稳定性": "Stability",
    "可靠性": "Reliability",
    "重复性": "Repeatability",
    "误检率": "False Detection Rate",
    "漏检率": "Miss Rate",
    "良品率": "Yield Rate",
    "不良率": "Defect Rate",
    "合格率": "Pass Rate",
    "节拍": "Cycle Time",
    "产能": "Throughput",
    "效率": "Efficiency",

    # 服务/支持
    "非标自动化": "Custom Automation",
    "定制化": "Customized",
    "解决方案": "Solution",
    "技术支持": "Technical Support",
    "售后服务": "After-Sales Service",
    "安装调试": "Installation & Commissioning",
    "培训": "Training",
    "保修": "Warranty",
    "质保": "Quality Warranty",
    "维护": "Maintenance",
    "升级": "Upgrade",
    "改造": "Retrofit",
    "集成": "Integration",
    "对接": "Integration / Interfacing",

    # 行业
    "3C": "3C (Computer, Communication, Consumer Electronics)",
    "电子": "Electronics",
    "半导体": "Semiconductor",
    "新能源": "New Energy",
    "锂电": "Lithium Battery",
    "汽车": "Automotive",
    "医疗": "Medical",
    "制药": "Pharmaceutical",
    "食品": "Food",
    "包装": "Packaging",
    "印刷": "Printing",
    "纺织": "Textile",
    "家电": "Home Appliance",
    "航空航天": "Aerospace",
    "军工": "Defense",

    # 公司/资质
    "ISO9001": "ISO 9001",
    "ISO14001": "ISO 14001",
    "CE": "CE",
    "专利": "Patent",
    "发明专利": "Invention Patent",
    "实用新型专利": "Utility Model Patent",
    "软件著作权": "Software Copyright",
    "高新技术企业": "High-Tech Enterprise",
    "研发中心": "R&D Center",
    "生产基地": "Production Base",
    "销售网络": "Sales Network",
    "服务网络": "Service Network",
}

# ============== 词典：精确短语 ==============
NAV = {
    "模具监视保护器": "Mold Monitor & Protector",
    "视觉传感器": "Vision Sensor",
    "六面光学分拣机": "6-Sided Optical Sorter",
    "柔性上料振动盘设备": "Flexible Feeding System",
    "在线检测设备": "Inline Inspection Equipment",
    "连接器在线检测设备": "Connector Inline Inspection",
    "HDMI拉料检测设备": "HDMI Pulling Inspection",
    "塑料件在线检测设备": "Plastic Part Inline Inspection",
}

FOOT = {
    "产品服务": "Products",
    "视频中心": "Videos",
    "产品介绍": "Product Intro",
    "操作视频": "How-To Videos",
    "视频案例": "Case Videos",
    "联系我们": "Contact Us",
    "联系方式": "Contact Info",
    "留言反馈": "Leave a Message",
    "全国客户服务热线": "Service Hotline",
    "官方邮箱": "Official Email",
    "微信公众号": "WeChat Official",
    "中国": "China",
}

COMMON = {
    "首页": "Home",
    "上一页": "Prev",
    "下一页": "Next",
    "更多": "More",
    "返回": "Back",
    "搜索": "Search",
    "查看详情": "View Details",
    "阅读全文": "Read More",
    "合作伙伴": "Partners",
    "应用案例": "Applications",
    "技术参数": "Specifications",
    "软件功能": "Software",
    "硬件优势": "Hardware",
    "公司新闻": "News",
    "关于我们": "About Us",
    "公司简介": "Company Profile",
    "企业文化": "Culture",
    "资质荣誉": "Honors",
    "发展历程": "Milestones",
    "新闻动态": "News",
    "行业资讯": "Industry",
    "在线留言": "Online Message",
    "地址": "Address",
    "电话": "Tel",
    "邮箱": "Email",
    "手机": "Mobile",
    "传真": "Fax",
}

# ============== 标题/描述 整段翻译（手工核心词条）==============
TITLE_MAP = {
    "模具监视保护器与工业视觉检测设备厂家｜迈必达":
        "Mold Monitor, Protector & Industrial Vision Inspection | Maibida",
    "模具监视保护器-昆山迈必达智能设备有限公司":
        "Mold Monitor & Protector | Kunshan Maibida Intelligent Equipment Co., Ltd.",
    "并联上料机器人与柔性供料设备｜昆山迈必达":
        "Parallel Feeding Robot & Flexible Feeding Equipment | Kunshan Maibida",
}

COMPANY = {
    "昆山迈必达智能设备有限公司": "Kunshan Maibida Intelligent Equipment Co., Ltd.",
    "迈必达": "Maibida",
}

# ============== 工具 ==============
def read(p):
    return p.read_text(encoding='utf-8', errors='ignore')

def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')

# ============== 路径重写 ==============
def rewrite_paths(html_text, depth, for_en=True):
    """
    for_en=True: 
      - 资源路径补一层 ../（让出 en/ 这层）
      - 内部 .html 链接：保持相对路径（在 en/ 镜像里相对位置一致）
    """
    if not for_en:
        return html_text

    def bump_attr(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        v = val.strip()
        if not v or v.startswith(('http://','https://','//','#','mailto:','tel:','javascript:','data:')):
            return m.group(0)
        if '.html' in v.lower():
            return m.group(0)
        if v.startswith('/'):
            # 已是根绝对资源，保持
            return m.group(0)
        # 折叠多余斜杠（不破坏协议）
        v = re.sub(r'/{2,}', '/', v)
        new_v = '../' + v
        return f'{attr}={q}{new_v}{q}'

    out = re.sub(r'\b(src|href|poster|action)=(["\'])([^"\']+)\2', bump_attr, html_text)
    return out


def fix_html_links(html_text, is_en, rel):
    """
    幂等地把所有 .html 内部链接改写到站点根绝对路径：
      - 英文镜像(is_en=True)：/en/<path>.html
      - 中文页(is_en=False)：/<path>.html
    已根绝对、已带 /en/ 的链接不会产生双斜杠。
    rel: 当前文件相对站点根目录的路径，如 product/10032.html
    """
    cur_dir = str(Path(rel).parent).replace('\\', '/')
    if cur_dir in ('.', ''):
        cur_dir = ''

    def fix(m):
        attr, q, v = m.group(1), m.group(2), m.group(3).strip()
        # 折叠多余斜杠（不破坏 https:// 等协议）
        v = re.sub(r'(?<!:)//+', '/', v)
        if not v or v.startswith(('http://','https://','//','#','mailto:','tel:','javascript:','data:')):
            return m.group(0)
        if '.html' not in v.lower():
            return m.group(0)
        # 去掉 .html 后的 query/anchor
        tail = ''
        m2 = re.search(r'\.html([?#].*)$', v)
        if m2:
            tail = m2.group(1)
            v = v[:m2.start()] + '.html'
        # 归一：去掉前导斜杠与任何已有的 en/ 前缀，避免重复
        path = v.lstrip('/')
        while path.startswith('en/'):
            path = path[3:]
        # 相对 cur_dir 解析
        if path and not path.startswith('/'):
            combined = (cur_dir + '/' + path) if cur_dir else path
            segs = []
            for s in combined.split('/'):
                if s == '..':
                    if segs:
                        segs.pop()
                elif s and s != '.':
                    segs.append(s)
            path = '/'.join(segs)
        else:
            path = path.lstrip('/')
        while path.startswith('en/'):
            path = path[3:]
        if is_en:
            path = 'en/' + path
        return f'{attr}={q}/{path}{tail}{q}'

    return re.sub(r'\b(href|action)=(["\'])([^"\']+\.html[^"\']*)\2', fix, html_text)

# ============== 翻译：JSON-LD 结构化数据 ==============
JSONLD_KEYS = ('name', 'description', 'headline', 'alternativeHeadline', 'about',
               'articleSection', 'caption', 'text')


def translate_jsonld(html_text):
    """仅翻译 <script type="application/ld+json"> 中指定键的字符串值（公司名/描述等）"""
    def kv_repl(mm):
        key, q, val = mm.group(1), mm.group(2), mm.group(3)
        if key in JSONLD_KEYS and re.search(r'[一-鿿]', val):
            return f'"{key}": {q}{machine_translate(val)}{q}'
        return mm.group(0)
    def repl(m):
        block = m.group(0)
        return re.sub(
            r'"(name|description|headline|alternativeHeadline|about|articleSection|caption)"\s*:\s*(")([^"]*)\2',
            kv_repl, block)
    return re.sub(r'<script[^>]*application/ld\+json[^>]*>[\s\S]*?</script>', repl, html_text)


# ============== 翻译：片段 ==============
def translate_text(t, lang='en'):
    """对单个文本片段做词典替换（贪心最长匹配）"""
    if not t:
        return t
    if lang != 'en':
        return t
    full = {}
    full.update(TITLE_MAP)
    full.update(COMPANY)
    full.update(NAV)
    full.update(FOOT)
    full.update(COMMON)
    full.update(TERMS)
    keys = sorted(full.keys(), key=lambda k: -len(k))
    out = t
    for k in keys:
        if k in out:
            out = out.replace(k, full[k])
    return out


# ============== 机器翻译（带术语保护）==============
_translator = None
_trans_cache = {}
_has_zh = re.compile(r'[一-鿿]')

def _get_translator():
    global _translator
    if _translator is None:
        from deep_translator import MyMemoryTranslator
        _translator = MyMemoryTranslator(source='zh-CN', target='en-GB')
    return _translator

def _protect_terms(s):
    """把术语替换为占位符 __T0__ __T1__ ..."""
    full = {}
    full.update(TERMS)
    full.update(COMPANY)
    keys = sorted([k for k in full.keys() if len(k) >= 2], key=lambda k: -len(k))
    placeholder = []
    out = s
    for k in keys:
        if k in out:
            idx = len(placeholder)
            placeholder.append(full[k])
            out = out.replace(k, f' __T{idx}__ ')
    return out, placeholder

def _restore_terms(s, placeholder):
    for i, term in enumerate(placeholder):
        # 匹配各种被破坏的形式：__T0__ / __ T 0 __ / T 0 / T0 等
        pat = re.compile(rf'\s*_+\s*T\s*{i}\s*_+\s*|\s+\bT\s*{i}\b\s*', re.I)
        s = pat.sub(f' {term} ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s+([.,;:!?%)\]])', r'\1', s)
    s = re.sub(r'([(\[])\s+', r'\1', s)
    return s

def machine_translate(s):
    """整段机器翻译，优先读缓存"""
    if not s or not _has_zh.search(s):
        return s
    key = s.strip()
    # 优先读缓存
    if key in _trans_cache:
        return _trans_cache[key]
    # 太短直接走词典
    if len(key) < 6:
        return translate_text(key)
    # 没缓存则跳过（build 阶段不再现场调用 MT）
    return translate_text(key)


def load_cache():
    """从 _zh2en.jsonl 加载缓存"""
    cache_file = ROOT / '_zh2en.jsonl'
    if not cache_file.exists():
        return
    import json
    with cache_file.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                o = json.loads(line)
                if o['zh'] and o['en']:
                    _trans_cache[o['zh'].strip()] = o['en']
            except:
                pass
    print(f"cache loaded: {len(_trans_cache)} entries")

# ============== 处理 HTML 文本节点 ==============
TAG_SKIP = {'script','style','noscript','code','pre','textarea'}

def translate_html(html_text, use_mt=True):
    """用 BeautifulSoup 精确翻译文本节点，保留标签结构"""
    from bs4 import BeautifulSoup, NavigableString, Comment
    soup = BeautifulSoup(html_text, 'html.parser')
    tr = machine_translate if use_mt else translate_text

    # 1. 翻译属性 alt/title/placeholder/value
    for el in soup.find_all(True):
        for attr in ('alt','title','placeholder','value'):
            if el.has_attr(attr):
                v = el.get(attr)
                if isinstance(v, str) and v.strip():
                    el[attr] = tr(v)

    # 2. 翻译 meta content
    for el in soup.find_all('meta'):
        if el.get('name') in ('description','keywords') and el.get('content'):
            el['content'] = tr(el['content'])

    # 3. title 标签
    if soup.title and soup.title.string:
        soup.title.string.replace_with(NavigableString(tr(str(soup.title.string))))

    # 4. 翻译文本节点
    for node in list(soup.find_all(string=True)):
        parent = node.parent
        if parent is None: continue
        if parent.name in TAG_SKIP: continue
        if isinstance(node, Comment): continue
        s = str(node)
        if not s.strip(): continue
        new_s = tr(s)
        if new_s != s:
            node.replace_with(NavigableString(new_s))

    return str(soup)

# ============== 语言切换按钮 ==============
LANG_BTN = """<div class="lang-switch">
  <button type="button" class="lang-btn" aria-haspopup="true" aria-expanded="false">
    <span class="lang-cur">{cur}</span><span class="lang-caret">▾</span>
  </button>
  <div class="lang-menu" role="menu">
    <a class="lang-item {active_zh}" href="{zh_url}" hreflang="zh-CN" lang="zh-CN">中文</a>
    <a class="lang-item {active_en}" href="{en_url}" hreflang="en" lang="en">English</a>
  </div>
</div>"""

LANG_SCRIPT = """<script>
(function(){
  if (window.__langSwitchInit) return;
  window.__langSwitchInit = true;
  function closeAll(){
    document.querySelectorAll('.lang-switch.open').forEach(function(s){
      s.classList.remove('open');
      var b=s.querySelector('.lang-btn'); if(b) b.setAttribute('aria-expanded','false');
    });
  }
  document.addEventListener('click', function(e){
    var sw = e.target.closest && e.target.closest('.lang-switch');
    if(sw){
      if(e.target.closest('.lang-btn')){
        e.preventDefault();
        var wasOpen = sw.classList.contains('open');
        closeAll();
        if(!wasOpen){
          sw.classList.add('open');
          sw.querySelector('.lang-btn').setAttribute('aria-expanded','true');
        }
        return;
      }
      return;
    }
    closeAll();
  });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeAll(); });
})();
</script>"""

LANG_CSS = """<style>
/* language switch in header */
.top .clear.wrap, .top2 .clear.wrap { position: relative; }
.top .T-nav, .top2 .T-nav { margin-right: 110px; }
.lang-switch { position: absolute; right: 0; top: 50%; transform: translateY(-50%); z-index: 50; }
.lang-btn { display:inline-flex; align-items:center; gap:6px; background:transparent; border:1px solid rgba(0,0,0,.15); border-radius:4px; padding:6px 10px; font-size:14px; color:#333; cursor:pointer; line-height:1; transition: all .2s; }
.top2 .lang-btn { color:#fff; border-color: rgba(255,255,255,.3); }
.top2.on .lang-btn { color:#333; border-color: rgba(0,0,0,.15); }
.lang-btn:hover { border-color:#009944; color:#009944; }
.top2 .lang-btn:hover { border-color:#009944; color:#009944; }
.lang-caret { font-size:10px; opacity:.7; }
.lang-menu { position:absolute; right:0; top:calc(100% + 8px); background:#fff; border:1px solid rgba(0,0,0,.08); border-radius:6px; box-shadow:0 6px 24px rgba(0,0,0,.12); min-width:120px; padding:6px 0; display:none; }
.lang-switch.open .lang-menu { display:block; }
.lang-item { display:block; padding:10px 18px; color:#333; font-size:14px; text-decoration:none; transition:background .15s; }
.lang-item:hover { background:#f0f8f3; color:#009944; }
.lang-item.active { color:#009944; font-weight:600; }
@media (max-width: 768px) {
  .top .T-nav, .top2 .T-nav { margin-right: 0; }
  .lang-switch { right: 60px; top: 18px; transform:none; }
}
</style>"""

def _strip_old_lang_li(html_text):
    """移除旧的 <li class="lang-switch">...</li>"""
    return re.sub(r'<li[^>]*class="lang-switch"[^>]*>[\s\S]*?</li>', '', html_text)

def strip_lang_stuff(html_text):
    """幂等清除所有注入的语言切换相关片段（按钮 div、语言样式、语言脚本）"""
    # 按钮 div（含一个嵌套 lang-menu div）：</ul> 后插入，结束于 </div></div>
    html_text = re.sub(r'<div class="lang-switch">[\s\S]*?</div>\s*</div>', '', html_text)
    # 注入的 <style> 语言样式块
    html_text = re.sub(r'<style>\s*/\* language switch in header \*/[\s\S]*?</style>', '', html_text)
    # 注入的 <script> 语言脚本块（含 .lang-switch）
    html_text = re.sub(r'<script>[\s\S]*?\.lang-switch[\s\S]*?</script>', '', html_text)
    return html_text


def insert_lang_switch(html_text, zh_url, en_url, cur):
    # 先移除旧的
    html_text = _strip_old_lang_li(html_text)
    html_text = strip_lang_stuff(html_text)
    # 防重复
    if '<div class="lang-switch">' in html_text:
        return html_text

    btn = LANG_BTN.format(
        cur=("中文" if cur=='zh' else 'English'),
        zh_url=zh_url, en_url=en_url,
        active_zh=('active' if cur=='zh' else ''),
        active_en=('active' if cur=='en' else ''),
    )

    # 在 </ul> 后插入按钮（在 .top/.top2 容器内）
    pat = re.compile(r'(<ul[^>]*class="[^"]*T-nav[^"]*"[^>]*>.*?</ul>)', re.S)
    m = pat.search(html_text)
    if m:
        html_text = html_text[:m.end(1)] + '\n' + btn + html_text[m.end(1):]
    else:
        html_text = re.sub(r'(<body[^>]*>)', r'\1\n' + btn, html_text, count=1)

    # 在 </head> 前插入 CSS
    if '</head>' in html_text:
        html_text = html_text.replace('</head>', LANG_CSS + '\n</head>', 1)
    else:
        html_text = LANG_CSS + html_text

    # 在 </body> 前插入 JS（仅一次）
    if '</body>' in html_text:
        html_text = html_text.replace('</body>', LANG_SCRIPT + '\n</body>', 1)
    else:
        html_text = html_text + LANG_SCRIPT
    return html_text

# ============== 主流程 ==============
def build():
    files = []
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith('en/'):
            continue
        files.append(rel)
    files.sort()
    print(f"Found {len(files)} pages")

    for rel in files:
        src = ROOT / rel
        dst = EN / rel
        depth = rel.count('/')
        text = read(src)

        # 先清除任何已注入的语言切换片段，得到干净基底
        base = strip_lang_stuff(text)

        # 1. 资源路径补 ../
        en_text = rewrite_paths(base, depth, for_en=True)

        # 2. 改 lang
        en_text = re.sub(r'<html([^>]*?)lang="zh-CN"', r'<html\1lang="en"', en_text)

        # 3. 翻译
        en_text = translate_html(en_text)
        en_text = translate_jsonld(en_text)

        # 4. 内部 .html 链接改写到 /en/... 根绝对（幂等）
        en_text = fix_html_links(en_text, True, rel)

        # 5. canonical 改 en
        en_text = re.sub(
            r'<link\s+href="(https://www\.maibida\.com)/([^"]*)"\s+rel="canonical"\s*/?>',
            lambda m: f'<link href="{m.group(1)}/en/{m.group(2)}" rel="canonical"/>',
            en_text
        )

        # 6. 在 en 页加切换按钮（用根绝对路径；按钮在链接改写之后插入，不被改写）
        zh_url = '/' + rel
        en_url = '/en/' + rel
        en_text = insert_lang_switch(en_text, zh_url=zh_url, en_url=en_url, cur='en')

        write(dst, en_text)
        print(f"  EN  {rel}")

    # 7. 中文页：清注入物 + 链接规范化 + 加切换按钮
    for rel in files:
        src = ROOT / rel
        text = read(src)
        base = strip_lang_stuff(text)
        # 内部 .html 链接改写到 /... 根绝对（折叠 //，幂等）
        zh_text = fix_html_links(base, False, rel)
        zh_url = '/' + rel
        en_url = '/en/' + rel
        zh_text = insert_lang_switch(zh_text, zh_url=zh_url, en_url=en_url, cur='zh')
        write(src, zh_text)
        print(f"  ZH  {rel}")

    print("DONE")

if __name__ == '__main__':
    load_cache()
    build()
