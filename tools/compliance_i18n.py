"""Localized compliance text for the pre-launch remediation (11 locales).

Pure data. Kept as a Python module so every generator imports the same
single source of truth; no page is written from here directly.
"""
LANGS = ["zh-CN", "en-US", "es-MX", "en-SG", "id-ID", "th-TH",
         "vi-VN", "ko-KR", "ja-JP", "ms-MY", "ru-RU"]

COMPANY_ZH = "昆山迈必达智能设备有限公司"
COMPANY_EN = "Kunshan Maibida Intelligent Equipment Co., Ltd."
ADDRESS_ZH = "中国江苏省苏州昆山市玉山镇乐山路6号裕大科技园2楼213室"
ADDRESS_EN = ("Room 213, 2/F, Yuda Science and Technology Park, No. 6 Leshan Road, "
              "Yushan Town, Kunshan, Suzhou, Jiangsu, China")
EMAIL = "mai_bida@163.com"
TEL = "+86 159 9567 5085"
POLICY_VERSION = "1.0"
EFFECTIVE_DATE = "2026-11-07"
RETENTION_MONTHS = 24

# ---------------------------------------------------------------- policy pages
# Each locale: title, lead, back label, and 10 [heading, body] sections.
POLICY = {}

POLICY["zh-CN"] = {
    "title": "隐私政策", "nav": "隐私政策", "back": "返回首页",
    "lead": "本政策说明本站如何收集、使用、保存与保护访客及询盘信息，适用于 www.maibida.com 的全部语言版本。",
    "sections": [
        ["数据控制者", f"{COMPANY_ZH}（以下简称「我们」）是个人信息处理者。地址：{ADDRESS_ZH}。联系邮箱：{EMAIL}，电话：{TEL}。"],
        ["收集的信息", "当您通过留言表单主动提交时，我们收集：姓名、邮箱、电话、公司、国家/地区、留言内容，以及提交语种、来源页面、提交时间、同意记录与政策版本。我们不在您浏览产品页时收集此类信息。"],
        ["使用目的与法律依据", "上述信息仅用于回复您的产品咨询、提供报价与技术资料、履行双方后续合同，以及在您同意的前提下发送业务跟进信息。处理依据为您的明确同意及订立/履行合同所必需。我们不会将信息用于自动化决策或用户画像。"],
        ["保存期限", f"询盘信息自提交之日起保存 {RETENTION_MONTHS} 个月，用于业务跟进与争议处理；期限届满或您行使删除权后，我们将在合理期限内删除或匿名化处理。"],
        ["存储地点与跨境传输", f"数据存储在中国境内由我们控制的服务器中，文件权限仅限授权人员。为回复来自墨西哥、西班牙、新加坡、越南、泰国、韩国等地的咨询，您的信息可能被我们的授权业务人员跨境访问；我们不会因此降低保护水平，并按需签署保密与数据处理约定。"],
        ["与第三方共享", "我们不出售、出租或公开您的个人信息。仅在以下情形共享：为完成您明确要求的交付或物流而必需；依适用法律法规、监管机构或司法机关强制要求；以及为保护我方合法权益且法律允许时。受托处理方须承担同等保密义务。"],
        ["您的权利", "您有权访问、更正、删除您的个人信息，撤回同意，限制或反对特定处理，并在适用时要求数据可携带。撤回同意不影响撤回前基于同意的处理合法性。请发送邮件至 " + EMAIL + " 提出请求，我们会在适用法律规定的期限内响应；您也有权向所在地监管机构投诉。"],
        ["Cookie 与追踪", "本站不设置 Google Analytics、Meta Pixel、百度统计等第三方追踪脚本，不投放行为广告。表单与语言切换仅依赖必要的功能性存储；如未来引入分析类 Cookie，我们将在启用前单独征求您的同意。"],
        ["未成年人", "本站面向企业采购与工业设备选型，不面向未满 18 周岁的未成年人，也不会故意收集其个人信息。"],
        ["政策变更与版本", f"本政策版本 {POLICY_VERSION}，生效日期 {EFFECTIVE_DATE}。如有实质变更，我们将在本页公布并更新版本号；涉及新增处理目的时会重新取得您的同意。"],
    ],
}

POLICY["en-US"] = {
    "title": "Privacy Policy", "nav": "Privacy Policy", "back": "Back to home",
    "lead": "This policy explains how this website collects, uses, retains and protects visitor and enquiry data. It applies to all language editions of www.maibida.com.",
    "sections": [
        ["Data controller", f"{COMPANY_EN} ('we') is the controller of your personal data. Address: {ADDRESS_EN}. Email: {EMAIL}. Phone: {TEL}."],
        ["What we collect", "When you voluntarily submit the enquiry form we collect your name, email, phone, company, country/region and message, plus the submission language, source page, timestamp, consent record and policy version. We do not collect these details while you simply browse product pages."],
        ["Purposes and legal basis", "The data is used only to answer your product enquiry, provide quotations and technical documentation, perform a subsequent contract, and — where you have consented — follow up on business matters. The legal bases are your explicit consent and the steps necessary to enter into or perform a contract. We do not use the data for automated decision-making or profiling."],
        ["Retention", f"Enquiry records are kept for {RETENTION_MONTHS} months from submission for follow-up and dispute handling, then deleted or anonymised. They are deleted earlier if you exercise your right to erasure."],
        ["Storage and international transfers", "Records are stored on servers under our control in China with access restricted to authorised staff. To reply to enquiries from Mexico, Spain, Singapore, Vietnam, Thailand and Korea, authorised staff may access the data from outside China. We maintain the same level of protection and put confidentiality and data-processing terms in place where required."],
        ["Sharing with third parties", "We do not sell, rent or publish your personal data. We share it only where necessary to perform a delivery you explicitly requested, where required by applicable law, regulators or courts, or where necessary to protect our legal rights. Processors acting for us are bound by equivalent confidentiality duties."],
        ["Your rights", "You may request access, rectification, erasure, restriction, objection, portability where applicable, and withdrawal of consent. Withdrawal does not affect the lawfulness of processing before it. Email " + EMAIL + " and we will respond within the statutory period; you may also lodge a complaint with your local supervisory authority (including under GDPR/LOPDGDD, LFPDPPP, PDPA, Decree 13/2023 and PIPA as applicable)."],
        ["Cookies and tracking", "This site does not load Google Analytics, Meta Pixel, Baidu Analytics or other third-party tracking scripts, and does not serve behavioural advertising. Only functionally necessary storage is used for the form and language switch. If analytics cookies are introduced, we will request your consent before enabling them."],
        ["Children", "This site addresses business purchasers and industrial equipment selection. It is not directed at persons under 18 and we do not knowingly collect their personal data."],
        ["Changes and version", f"Version {POLICY_VERSION}, effective {EFFECTIVE_DATE}. Material changes will be published here with an updated version number; a new processing purpose will require fresh consent."],
    ],
}

POLICY["es-MX"] = {
    "title": "Aviso de Privacidad", "nav": "Aviso de Privacidad", "back": "Volver al inicio",
    "lead": "Este aviso explica cómo este sitio recaba, utiliza, conserva y protege los datos de visitantes y de contacto. Aplica a todas las versiones de idioma de www.maibida.com.",
    "sections": [
        ["Responsable de los datos", f"{COMPANY_EN} («nosotros») es el responsable de sus datos personales. Domicilio: {ADDRESS_EN}. Correo: {EMAIL}. Teléfono: {TEL}."],
        ["Datos que recabamos", "Al enviar voluntariamente el formulario recabamos nombre, correo electrónico, teléfono, empresa, país/región y mensaje, además del idioma, la página de origen, la fecha de envío, el registro de consentimiento y la versión del aviso. No recabamos estos datos cuando usted solo navega por las páginas de producto."],
        ["Finalidades y base jurídica", "Los datos se usan únicamente para responder a su consulta, enviar cotizaciones y documentación técnica, cumplir un contrato posterior y, con su consentimiento, dar seguimiento comercial. Las bases son su consentimiento expreso y la necesidad de celebrar o ejecutar un contrato. No se usan para decisiones automatizadas ni perfilamiento."],
        ["Conservación", f"Los registros se conservan {RETENTION_MONTHS} meses desde el envío para seguimiento y atención de controversias y después se eliminan o anonimizan. Se eliminan antes si usted ejerce su derecho de cancelación."],
        ["Almacenamiento y transferencias", "Los registros se almacenan en servidores bajo nuestro control en China, con acceso restringido a personal autorizado. Para responder consultas de México, España, Singapur, Vietnam, Tailandia y Corea, personal autorizado puede acceder desde el extranjero. Mantenemos el mismo nivel de protección y suscribimos acuerdos de confidencialidad y tratamiento cuando corresponde."],
        ["Comunicación a terceros", "No vendemos, rentamos ni publicamos sus datos personales. Solo los compartimos cuando es necesario para una entrega que usted solicitó expresamente, por obligación legal o requerimiento de autoridad, o para proteger nuestros derechos legales. Los encargados quedan sujetos a obligaciones equivalentes de confidencialidad."],
        ["Derechos ARCO", "Usted puede ejercer los derechos de acceso, rectificación, cancelación y oposición, así como revocar su consentimiento, limitar el tratamiento y solicitar portabilidad cuando proceda. La revocación no afecta el tratamiento previo. Escriba a " + EMAIL + "; responderemos en el plazo legal y usted puede acudir a la autoridad de protección de datos de su país."],
        ["Cookies y seguimiento", "Este sitio no carga Google Analytics, Meta Pixel, Baidu Analytics ni otros scripts de seguimiento de terceros y no muestra publicidad conductual. Solo se usa almacenamiento funcional necesario para el formulario y el selector de idioma. Si se incorporan cookies de analítica, solicitaremos su consentimiento antes de activarlas."],
        ["Menores de edad", "El sitio se dirige a compradores empresariales y a la selección de equipo industrial. No se dirige a menores de 18 años y no recabamos sus datos de forma intencional."],
        ["Cambios y versión", f"Versión {POLICY_VERSION}, vigente desde {EFFECTIVE_DATE}. Los cambios sustanciales se publicarán aquí con una nueva versión; una finalidad adicional requerirá un nuevo consentimiento."],
    ],
}

POLICY["en-SG"] = dict(
    POLICY["en-US"],
    title="Privacy Policy (Singapore / Asia-Pacific)", nav="Privacy Policy",
    lead="For the Singapore / Asia-Pacific English edition: this policy explains how this website collects, uses, retains and protects visitor and enquiry data, and it also applies to all other language editions of www.maibida.com.")

POLICY["id-ID"] = {
    "title": "Kebijakan Privasi", "nav": "Kebijakan Privasi", "back": "Kembali ke beranda",
    "lead": "Kebijakan ini menjelaskan bagaimana situs mengumpulkan, menggunakan, menyimpan, dan melindungi data pengunjung serta pertanyaan. Berlaku untuk semua edisi bahasa www.maibida.com.",
    "sections": [
        ["Pengendali data", f"{COMPANY_EN} ('kami') adalah pengendali data pribadi Anda. Alamat: {ADDRESS_EN}. Email: {EMAIL}. Telepon: {TEL}."],
        ["Data yang dikumpulkan", "Saat Anda mengirim formulir secara sukarela, kami mengumpulkan nama, email, telepon, perusahaan, negara/wilayah, dan pesan, serta bahasa, halaman asal, waktu kirim, catatan persetujuan, dan versi kebijakan. Data tersebut tidak dikumpulkan saat Anda hanya menelusuri halaman produk."],
        ["Tujuan dan dasar hukum", "Data hanya digunakan untuk menjawab pertanyaan, memberikan penawaran dan dokumentasi teknis, melaksanakan kontrak berikutnya, dan — dengan persetujuan Anda — menindaklanjuti kerja sama. Dasarnya adalah persetujuan eksplisit dan langkah yang diperlukan untuk membuat atau melaksanakan kontrak. Data tidak digunakan untuk keputusan otomatis atau profil."],
        ["Penyimpanan", f"Catatan disimpan {RETENTION_MONTHS} bulan sejak pengiriman untuk tindak lanjut dan penanganan sengketa, lalu dihapus atau dianonimkan. Penghapusan lebih awal dilakukan jika Anda menggunakan hak penghapusan."],
        ["Lokasi dan transfer lintas negara", "Data disimpan di server yang kami kendalikan di Tiongkok dengan akses terbatas bagi staf berwenang. Untuk menjawab pertanyaan dari Meksiko, Spanyol, Singapura, Vietnam, Thailand, dan Korea, staf berwenang dapat mengaksesnya dari luar negeri dengan tingkat perlindungan yang sama dan perjanjian kerahasiaan bila diperlukan."],
        ["Berbagi dengan pihak ketiga", "Kami tidak menjual, menyewakan, atau memublikasikan data pribadi Anda. Data hanya dibagikan untuk pengiriman yang Anda minta secara tegas, karena kewajiban hukum atau permintaan otoritas, atau untuk melindungi hak hukum kami. Pemroses data terikat kewajiban kerahasiaan yang setara."],
        ["Hak Anda", "Anda dapat meminta akses, perbaikan, penghapusan, pembatasan, keberatan, portabilitas bila berlaku, dan penarikan persetujuan. Penarikan tidak memengaruhi pemrosesan sebelumnya. Kirim email ke " + EMAIL + "; kami akan merespons dalam jangka waktu yang ditentukan hukum, dan Anda dapat mengajukan keluhan kepada otoritas setempat."],
        ["Cookie dan pelacakan", "Situs ini tidak memuat Google Analytics, Meta Pixel, Baidu Analytics, atau skrip pelacakan pihak ketiga lainnya dan tidak menampilkan iklan perilaku. Hanya penyimpanan fungsional yang diperlukan untuk formulir dan pemilih bahasa. Jika cookie analitik ditambahkan, persetujuan akan diminta terlebih dahulu."],
        ["Anak-anak", "Situs ini ditujukan untuk pembeli bisnis dan pemilihan peralatan industri, bukan untuk orang di bawah 18 tahun, dan kami tidak sengaja mengumpulkan data mereka."],
        ["Perubahan dan versi", f"Versi {POLICY_VERSION}, berlaku {EFFECTIVE_DATE}. Perubahan material akan diumumkan di sini dengan nomor versi baru; tujuan pemrosesan tambahan memerlukan persetujuan baru."],
    ],
}

POLICY["th-TH"] = {
    "title": "นโยบายความเป็นส่วนตัว", "nav": "นโยบายความเป็นส่วนตัว", "back": "กลับสู่หน้าแรก",
    "lead": "นโยบายนี้อธิบายวิธีที่เว็บไซต์เก็บรวบรวม ใช้ จัดเก็บ และคุ้มครองข้อมูลของผู้เยี่ยมชมและข้อมูลติดต่อ โดยใช้กับทุกภาษาของ www.maibida.com",
    "sections": [
        ["ผู้ควบคุมข้อมูล", f"{COMPANY_EN} (「เรา」) เป็นผู้ควบคุมข้อมูลส่วนบุคคล ที่อยู่: {ADDRESS_EN} อีเมล: {EMAIL} โทร: {TEL}"],
        ["ข้อมูลที่เก็บรวบรวม", "เมื่อคุณส่งแบบฟอร์มด้วยความสมัครใจ เราเก็บชื่อ อีเมล โทรศัพท์ บริษัท ประเทศ/ภูมิภาค และข้อความ รวมถึงภาษา หน้าที่มา เวลาที่ส่ง บันทึกความยินยอม และเวอร์ชันนโยบาย เราไม่เก็บข้อมูลเหล่านี้ขณะที่คุณเพียงเข้าชมหน้าสินค้า"],
        ["วัตถุประสงค์และฐานทางกฎหมาย", "ข้อมูลใช้เพียงเพื่อตอบคำถาม จัดส่งใบเสนอราคาและเอกสารเทคนิค ปฏิบัติตามสัญญาที่ตามมา และติดตามธุรกิจเมื่อได้รับความยินยอม ฐานคือความยินยอมโดยชัดแจ้งและความจำเป็นในการเข้าหรือปฏิบัติตามสัญญา เราไม่ใช้ข้อมูลเพื่อการตัดสินใจอัตโนมัติหรือการสร้างโปรไฟล์"],
        ["ระยะเวลาจัดเก็บ", f"บันทึกถูกเก็บ {RETENTION_MONTHS} เดือนนับจากวันส่ง เพื่อติดตามและจัดการข้อพิพาท จากนั้นจะถูกลบหรือทำให้ไม่ระบุตัวตน และจะถูกลบก่อนหน้านั้นหากคุณใช้สิทธิขอให้ลบ"],
        ["สถานที่จัดเก็บและการโอนข้ามประเทศ", "ข้อมูลจัดเก็บในเซิร์ฟเวอร์ที่เราควบคุมในประเทศจีน โดยจำกัดการเข้าถึงเฉพาะเจ้าหน้าที่ที่ได้รับอนุญาต เพื่อตอบคำถามจากเม็กซิโก สเปน สิงคโปร์ เวียดนาม ไทย และเกาหลี เจ้าหน้าที่ที่ได้รับอนุญาตอาจเข้าถึงจากต่างประเทศ โดยคงระดับการคุ้มครองเดียวกันและจัดทำข้อตกลงการรักษาความลับเมื่อจำเป็น"],
        ["การเปิดเผยแก่บุคคลที่สาม", "เราไม่ขาย ให้เช่า หรือเปิดเผยข้อมูลส่วนบุคคลของคุณต่อสาธารณะ จะเปิดเผยเฉพาะเมื่อจำเป็นสำหรับการส่งมอบที่คุณร้องขอชัดเจน ตามข้อกำหนดของกฎหมายหรือหน่วยงานกำกับดูแล หรือเพื่อคุ้มครองสิทธิทางกฎหมายของเรา ผู้ประมวลผลต้องผูกพันตามหน้าที่รักษาความลับที่เท่าเทียมกัน"],
        ["สิทธิของคุณ", "คุณมีสิทธิขอเข้าถึง แก้ไข ลบ จำกัด คัดค้าน โอนย้ายข้อมูลเมื่อใช้บังคับ และถอนความยินยอม การถอนไม่กระทบความชอบด้วยกฎหมายของการประมวลผลก่อนหน้า ส่งอีเมลถึง " + EMAIL + " เราจะตอบภายในระยะเวลาตามกฎหมาย และคุณสามารถร้องเรียนต่อหน่วยงานกำกับดูแลในประเทศของคุณ"],
        ["คุกกี้และการติดตาม", "เว็บไซต์ไม่โหลด Google Analytics, Meta Pixel, Baidu Analytics หรือสคริปต์ติดตามบุคคลที่สามอื่น ๆ และไม่แสดงโฆษณาตามพฤติกรรม ใช้เฉพาะการจัดเก็บที่จำเป็นต่อการทำงานของแบบฟอร์มและตัวเลือกภาษา หากเพิ่มคุกกี้วิเคราะห์ เราจะขอความยินยอมก่อนเปิดใช้งาน"],
        ["ผู้เยาว์", "เว็บไซต์มุ่งให้บริการผู้ซื้อภาคธุรกิจและการเลือกอุปกรณ์อุตสาหกรรม ไม่มุ่งให้บริการผู้ที่มีอายุต่ำกว่า 18 ปี และเราไม่เก็บข้อมูลของผู้เยาว์โดยเจตนา"],
        ["การเปลี่ยนแปลงและเวอร์ชัน", f"เวอร์ชัน {POLICY_VERSION} มีผลตั้งแต่ {EFFECTIVE_DATE} การเปลี่ยนแปลงสาระสำคัญจะประกาศที่หน้านี้พร้อมหมายเลขเวอร์ชันใหม่ วัตถุประสงค์ใหม่ต้องขอความยินยอมอีกครั้ง"],
    ],
}

POLICY["vi-VN"] = {
    "title": "Chính sách Quyền riêng tư", "nav": "Chính sách Riêng tư", "back": "Về trang chủ",
    "lead": "Chính sách này giải thích cách website thu thập, sử dụng, lưu trữ và bảo vệ dữ liệu của khách truy cập và thông tin liên hệ, áp dụng cho mọi phiên bản ngôn ngữ của www.maibida.com.",
    "sections": [
        ["Bên kiểm soát dữ liệu", f"{COMPANY_EN} ('chúng tôi') là bên kiểm soát dữ liệu cá nhân. Địa chỉ: {ADDRESS_EN}. Email: {EMAIL}. Điện thoại: {TEL}."],
        ["Dữ liệu thu thập", "Khi bạn tự nguyện gửi biểu mẫu, chúng tôi thu thập họ tên, email, điện thoại, công ty, quốc gia/khu vực và nội dung, cùng ngôn ngữ, trang nguồn, thời điểm gửi, bản ghi đồng ý và phiên bản chính sách. Chúng tôi không thu thập các dữ liệu này khi bạn chỉ xem trang sản phẩm."],
        ["Mục đích và cơ sở pháp lý", "Dữ liệu chỉ dùng để trả lời yêu cầu, gửi báo giá và tài liệu kỹ thuật, thực hiện hợp đồng sau đó và — khi bạn đồng ý — chăm sóc khách hàng. Cơ sở là sự đồng ý rõ ràng và các bước cần thiết để giao kết hoặc thực hiện hợp đồng. Không dùng cho quyết định tự động hay lập hồ sơ."],
        ["Thời gian lưu trữ", f"Bản ghi được lưu {RETENTION_MONTHS} tháng kể từ khi gửi để theo dõi và xử lý tranh chấp, sau đó xóa hoặc ẩn danh. Xóa sớm hơn khi bạn thực hiện quyền yêu cầu xóa."],
        ["Nơi lưu trữ và chuyển dữ liệu xuyên biên giới", "Dữ liệu lưu trên máy chủ do chúng tôi kiểm soát tại Trung Quốc, chỉ nhân sự được ủy quyền truy cập. Để trả lời yêu cầu từ Mexico, Tây Ban Nha, Singapore, Việt Nam, Thái Lan và Hàn Quốc, nhân sự được ủy quyền có thể truy cập từ nước ngoài với mức bảo vệ tương đương và thỏa thuận bảo mật khi cần (theo Nghị định 13/2023)."],
        ["Chia sẻ với bên thứ ba", "Chúng tôi không bán, cho thuê hay công khai dữ liệu cá nhân. Chỉ chia sẻ khi cần cho việc giao hàng bạn yêu cầu rõ ràng, theo nghĩa vụ pháp lý hoặc yêu cầu của cơ quan nhà nước, hoặc để bảo vệ quyền lợi hợp pháp. Bên xử lý phải tuân thủ nghĩa vụ bảo mật tương đương."],
        ["Quyền của bạn", "Bạn có quyền yêu cầu truy cập, chỉnh sửa, xóa, hạn chế, phản đối, chuyển dữ liệu khi áp dụng và rút lại sự đồng ý. Việc rút lại không ảnh hưởng đến tính hợp pháp của xử lý trước đó. Gửi email tới " + EMAIL + "; chúng tôi phản hồi trong thời hạn luật định và bạn có thể khiếu nại lên cơ quan quản lý tại quốc gia của mình."],
        ["Cookie và theo dõi", "Website không tải Google Analytics, Meta Pixel, Baidu Analytics hay script theo dõi bên thứ ba khác và không hiển thị quảng cáo hành vi. Chỉ dùng lưu trữ chức năng cần thiết cho biểu mẫu và bộ chọn ngôn ngữ. Nếu bổ sung cookie phân tích, chúng tôi sẽ xin sự đồng ý trước."],
        ["Trẻ vị thành niên", "Website hướng đến người mua doanh nghiệp và lựa chọn thiết bị công nghiệp, không hướng đến người dưới 18 tuổi và chúng tôi không cố ý thu thập dữ liệu của họ."],
        ["Thay đổi và phiên bản", f"Phiên bản {POLICY_VERSION}, hiệu lực {EFFECTIVE_DATE}. Thay đổi trọng yếu sẽ công bố tại đây kèm số phiên bản mới; mục đích xử lý mới cần sự đồng ý mới."],
    ],
}

POLICY["ko-KR"] = {
    "title": "개인정보 처리방침", "nav": "개인정보 처리방침", "back": "홈으로",
    "lead": "본 방침은 www.maibida.com의 모든 언어판에서 방문자 및 문의 정보를 어떻게 수집·이용·보관·보호하는지 설명합니다.",
    "sections": [
        ["개인정보 처리자", f"{COMPANY_EN}(이하 '당사')가 개인정보 처리자입니다. 주소: {ADDRESS_EN}. 이메일: {EMAIL}. 전화: {TEL}."],
        ["수집하는 항목", "문의 양식을 자발적으로 제출할 때 성명, 이메일, 전화번호, 회사, 국가/지역, 문의 내용과 함께 제출 언어, 유입 페이지, 제출 시각, 동의 기록 및 방침 버전을 수집합니다. 제품 페이지를 단순 열람할 때는 이러한 정보를 수집하지 않습니다."],
        ["이용 목적 및 법적 근거", "해당 정보는 문의 회신, 견적 및 기술 자료 제공, 이후 계약 이행, 그리고 동의한 경우 영업 후속 연락에만 사용됩니다. 근거는 명시적 동의와 계약 체결·이행에 필요한 조치입니다. 자동화된 의사결정이나 프로파일링에 사용하지 않습니다."],
        ["보유 기간", f"문의 기록은 제출일로부터 {RETENTION_MONTHS}개월간 후속 업무 및 분쟁 대응을 위해 보관한 뒤 삭제 또는 익명화합니다. 삭제권을 행사하면 그 전이라도 삭제합니다."],
        ["보관 장소 및 국외 이전", "기록은 당사가 관리하는 중국 내 서버에 권한자만 접근 가능하도록 보관합니다. 멕시코, 스페인, 싱가포르, 베트남, 태국, 한국 등에서 온 문의에 회신하기 위해 권한을 가진 담당자가 국외에서 접근할 수 있으며, 동일한 보호 수준을 유지하고 필요 시 비밀유지 및 처리 위탁 계약을 체결합니다."],
        ["제3자 제공", "개인정보를 판매·임대·공개하지 않습니다. 귀하가 명시적으로 요청한 납품에 필요한 경우, 법령·감독기관·법원의 요구가 있는 경우, 또는 당사의 적법한 권익 보호에 필요한 경우에만 공유하며 수탁자는 동등한 비밀유지 의무를 집니다."],
        ["정보주체의 권리", "열람, 정정, 삭제, 처리정지, 이의제기, 적용 시 전송 요구 및 동의 철회를 요청할 수 있습니다. 동의 철회는 철회 전 처리의 적법성에 영향을 주지 않습니다. " + EMAIL + "로 요청하면 법정 기간 내 회신하며, 소재지 감독기관에 민원을 제기할 수도 있습니다."],
        ["쿠키 및 추적", "본 사이트는 Google Analytics, Meta Pixel, 바이두 통계 등 제3자 추적 스크립트를 불러오지 않으며 행위 기반 광고를 게재하지 않습니다. 양식과 언어 전환에 필요한 기능적 저장만 사용합니다. 분석 쿠키를 도입할 경우 사전에 별도 동의를 받습니다."],
        ["아동", "본 사이트는 기업 구매자와 산업장비 선정을 대상으로 하며 만 18세 미만을 대상으로 하지 않고, 그 개인정보를 고의로 수집하지 않습니다."],
        ["방침 변경 및 버전", f"버전 {POLICY_VERSION}, 시행일 {EFFECTIVE_DATE}. 중요한 변경은 본 페이지에 버전과 함께 공지하며, 새로운 처리 목적에는 새 동의를 받습니다."],
    ],
}

POLICY["ja-JP"] = {
    "title": "プライバシーポリシー", "nav": "プライバシーポリシー", "back": "ホームへ戻る",
    "lead": "本ポリシーは、www.maibida.com の全言語版において、訪問者およびお問い合わせ情報をどのように取得・利用・保存・保護するかを説明します。",
    "sections": [
        ["データ管理者", f"{COMPANY_EN}（以下「当社」）が個人データの管理者です。住所：{ADDRESS_EN}。メール：{EMAIL}。電話：{TEL}。"],
        ["取得する情報", "お問い合わせフォームを任意で送信された場合、お名前、メールアドレス、電話番号、会社名、国・地域、お問い合わせ内容に加え、送信言語、参照ページ、送信日時、同意記録、ポリシー版数を取得します。製品ページを閲覧するだけではこれらの情報は取得しません。"],
        ["利用目的および法的根拠", "取得した情報は、お問い合わせへの返信、見積・技術資料の提供、その後の契約履行、および同意をいただいた場合の営業上のフォローにのみ使用します。根拠は明示的な同意と契約の締結・履行に必要な行為です。自動意思決定やプロファイリングには利用しません。"],
        ["保存期間", f"お問い合わせ記録は送信日から {RETENTION_MONTHS} か月間、フォローおよび紛争対応のため保存し、その後削除または匿名化します。削除権を行使された場合はそれより前に削除します。"],
        ["保管場所および越境移転", "記録は当社が管理する中国国内のサーバーに、権限者のみがアクセスできる状態で保管します。メキシコ、スペイン、シンガポール、ベトナム、タイ、韓国からのお問い合わせに返信するため、権限を持つ担当者が国外からアクセスする場合がありますが、同等の保護水準を維持し、必要に応じて秘密保持およびデータ処理契約を締結します。"],
        ["第三者との共有", "個人データを販売・貸与・公開することはありません。お客様が明示的に依頼した納品に必要な場合、法令・規制当局・裁判所の要求がある場合、または当社の適法な権利保護に必要な場合にのみ共有し、受託者には同等の秘密保持義務を課します。"],
        ["お客様の権利", "アクセス、訂正、削除、処理の制限・異議申立て、適用される場合のデータポータビリティ、同意の撤回を求めることができます。撤回は撤回前の処理の適法性に影響しません。" + EMAIL + " までご連絡ください。法定期間内に対応し、所在地の監督機関への申立ても可能です。"],
        ["Cookie とトラッキング", "本サイトは Google Analytics、Meta Pixel、百度統計などの第三者トラッキングスクリプトを読み込まず、行動ターゲティング広告も表示しません。フォームと言語切替に必要な機能的保存のみを使用します。分析用 Cookie を導入する場合は事前に同意を取得します。"],
        ["未成年者", "本サイトは法人購入者と産業機器の選定を対象としており、18 歳未満を対象とせず、その個人データを故意に取得しません。"],
        ["改定および版数", f"版数 {POLICY_VERSION}、施行日 {EFFECTIVE_DATE}。重要な変更は本ページに版数とともに掲載し、新たな利用目的には改めて同意を取得します。"],
    ],
}

POLICY["ms-MY"] = {
    "title": "Dasar Privasi", "nav": "Dasar Privasi", "back": "Kembali ke laman utama",
    "lead": "Dasar ini menerangkan bagaimana laman ini mengumpul, menggunakan, menyimpan dan melindungi data pelawat serta pertanyaan. Ia terpakai bagi semua edisi bahasa www.maibida.com.",
    "sections": [
        ["Pengawal data", f"{COMPANY_EN} ('kami') ialah pengawal data peribadi anda. Alamat: {ADDRESS_EN}. E-mel: {EMAIL}. Telefon: {TEL}."],
        ["Data yang dikumpulkan", "Apabila anda menghantar borang secara sukarela, kami mengumpulkan nama, e-mel, telefon, syarikat, negara/wilayah dan mesej, serta bahasa, halaman asal, masa hantar, rekod persetujuan dan versi dasar. Kami tidak mengumpulkan data ini semasa anda hanya melayari halaman produk."],
        ["Tujuan dan asas undang-undang", "Data digunakan hanya untuk menjawab pertanyaan, menyediakan sebut harga dan dokumentasi teknikal, melaksanakan kontrak seterusnya, dan — dengan persetujuan anda — susulan perniagaan. Asasnya ialah persetujuan jelas dan langkah perlu untuk membentuk atau melaksanakan kontrak. Data tidak digunakan untuk keputusan automatik atau pemprofilan."],
        ["Tempoh simpanan", f"Rekod disimpan {RETENTION_MONTHS} bulan dari tarikh hantar untuk susulan dan pengendalian pertikaian, kemudian dipadam atau dianonimkan. Dipadam lebih awal jika anda menggunakan hak pemadaman."],
        ["Lokasi dan pemindahan rentas sempadan", "Data disimpan pada pelayan kawalan kami di China dengan akses terhad kepada kakitangan berkuasa. Untuk menjawab pertanyaan dari Mexico, Sepanyol, Singapura, Vietnam, Thailand dan Korea, kakitangan berkuasa boleh mengakses dari luar negara dengan tahap perlindungan sama dan perjanjian kerahsiaan apabila perlu."],
        ["Perkongsian dengan pihak ketiga", "Kami tidak menjual, menyewa atau menerbitkan data peribadi anda. Data dikongsi hanya bagi penghantaran yang anda minta secara jelas, keperluan undang-undang atau pihak berkuasa, atau perlindungan hak sah kami. Pemproses tertakluk kepada kewajipan kerahsiaan setara."],
        ["Hak anda", "Anda boleh meminta akses, pembetulan, pemadaman, sekatan, bantahan, keboleh-alihan jika terpakai, dan penarikan balik persetujuan. Penarikan tidak menjejaskan pemprosesan sebelum itu. E-mel " + EMAIL + "; kami akan menjawab dalam tempoh berkanun dan anda boleh mengadu kepada pihak berkuasa tempatan."],
        ["Kuki dan penjejakan", "Laman ini tidak memuatkan Google Analytics, Meta Pixel, Baidu Analytics atau skrip penjejakan pihak ketiga lain dan tidak memaparkan iklan tingkah laku. Hanya storan fungsi perlu untuk borang dan pemilih bahasa. Jika kuki analitik ditambah, persetujuan akan diminta terlebih dahulu."],
        ["Kanak-kanak", "Laman ini ditujukan kepada pembeli perniagaan dan pemilihan peralatan industri, bukan kepada bawah 18 tahun, dan kami tidak sengaja mengumpulkan data mereka."],
        ["Perubahan dan versi", f"Versi {POLICY_VERSION}, berkuat kuasa {EFFECTIVE_DATE}. Perubahan material akan diterbitkan di sini dengan nombor versi baharu; tujuan baharu memerlukan persetujuan baharu."],
    ],
}

POLICY["ru-RU"] = {
    "title": "Политика конфиденциальности", "nav": "Конфиденциальность", "back": "На главную",
    "lead": "Настоящая политика описывает, как сайт собирает, использует, хранит и защищает данные посетителей и запросов. Она действует для всех языковых версий www.maibida.com.",
    "sections": [
        ["Оператор данных", f"{COMPANY_EN} («мы») является оператором персональных данных. Адрес: {ADDRESS_EN}. Эл. почта: {EMAIL}. Тел.: {TEL}."],
        ["Какие данные собираются", "При добровольной отправке формы мы получаем имя, эл. почту, телефон, компанию, страну/регион и текст сообщения, а также язык, страницу-источник, время отправки, запись о согласии и версию политики. При простом просмотре страниц продуктов эти данные не собираются."],
        ["Цели и правовое основание", "Данные используются только для ответа на запрос, предоставления коммерческого предложения и технической документации, исполнения последующего договора и — при наличии согласия — деловой переписки. Основаниями являются явное согласие и действия, необходимые для заключения или исполнения договора. Автоматизированные решения и профилирование не применяются."],
        ["Срок хранения", f"Записи хранятся {RETENTION_MONTHS} месяцев с момента отправки для сопровождения и урегулирования споров, затем удаляются или обезличиваются. По вашему требованию они удаляются раньше."],
        ["Место хранения и трансграничная передача", "Данные хранятся на контролируемых нами серверах в Китае с доступом только для уполномоченного персонала. Для ответов на запросы из Мексики, Испании, Сингапура, Вьетнама, Таиланда и Кореи уполномоченные сотрудники могут получать доступ из-за рубежа с сохранением того же уровня защиты и при необходимости с соглашениями о конфиденциальности."],
        ["Передача третьим лицам", "Мы не продаём, не сдаём в аренду и не публикуем ваши персональные данные. Передача возможна лишь для явно запрошенной вами поставки, по требованию закона, регулятора или суда, либо для защиты наших законных прав. Обработчики связаны равнозначными обязательствами конфиденциальности."],
        ["Ваши права", "Вы вправе требовать доступа, исправления, удаления, ограничения, возражения, переноса данных (где применимо) и отзыва согласия. Отзыв не влияет на законность обработки до него. Пишите на " + EMAIL + "; мы ответим в установленный срок, и вы можете обратиться в надзорный орган своей страны."],
        ["Файлы cookie и отслеживание", "Сайт не загружает Google Analytics, Meta Pixel, Baidu Analytics и другие сторонние скрипты отслеживания и не показывает поведенческую рекламу. Используется только функциональное хранилище, необходимое для формы и переключателя языков. При внедрении аналитических cookie мы предварительно запросим согласие."],
        ["Несовершеннолетние", "Сайт предназначен для корпоративных заказчиков и подбора промышленного оборудования, не ориентирован на лиц младше 18 лет, и мы не собираем их данные преднамеренно."],
        ["Изменения и версия", f"Версия {POLICY_VERSION}, действует с {EFFECTIVE_DATE}. Существенные изменения публикуются здесь с обновлением номера версии; новая цель обработки потребует нового согласия."],
    ],
}

# ---------------------------------------------------------------- terms pages
TERMS = {}

TERMS["zh-CN"] = {
    "title": "销售条款与技术声明", "nav": "销售条款", "back": "返回首页",
    "lead": "本页说明本站产品信息、技术参数、图片及报价的性质与适用范围，构成双方后续技术协议与销售合同的参考基础。",
    "sections": [
        ["网页信息的性质", "本站（含全部语言版本）展示的产品介绍、技术参数、检测能力、应用案例与图片仅供选型参考，不构成要约、性能保证或合同承诺。最终规格、配置、价格、交期与验收标准以双方签署的技术协议、报价单及销售合同为准。"],
        ["技术参数与工况依赖", "页面所列的精度（如 ±0.02 mm、0.0007 mm）、节拍（如 4500 PCS/H、60 个/分）、分辨率（如 8 MP / 800 万像素）与检测能力，均为在规定工件、光照、治具定位、来料状态与参数设定下的典型参考值。实际表现受现场工况影响，须经双方样件测试与验收确认。"],
        ["全数检测表述", "「支持产线全数在线检测」描述设备的功能范围，不代表任何条件下均达到 100% 检出或零漏检。检出率、误报率与节拍以双方确认的验收标准和技术协议为准。"],
        ["规格变更", "因产品迭代、供应链调整或客户定制需要，规格、外观、软件功能与型号可能变更，恕不另行通知；已签署合同项下的变更须经双方书面确认。"],
        ["图片与示意图", "产品照片、应用场景图、界面截图及示意图仅用于说明。示意图、渲染图或带生成工具标识的图片不代表实际交付外观或真实检测结果，请以实物及交付文档为准。"],
        ["第三方组件与商标", "设备可能采用第三方供应的通用元器件（如 CMOS 图像传感器）。第三方名称如被提及，仅用于说明部件规格，不表示原厂合作、授权、背书或整机品牌归属。所有第三方商标归其权利人所有。"],
        ["保修与责任范围", "保修范围、期限、易损件与除外情形以销售合同约定为准。对于未按说明书安装使用、擅自改装、外部供电或环境异常、耗材磨损及不可抗力造成的故障，我们不承担保修责任。除法律强制规定外，我们不就间接损失、停产损失或利润损失承担责任。"],
        ["适用法律与争议解决", "本声明及后续交易适用中华人民共和国法律；双方应首先友好协商，协商不成时按销售合同约定的争议解决方式处理。本页各语言版本若有语义差异，以中文版为准。"],
        ["联系与版本", f"商务与技术咨询：{EMAIL}，电话 {TEL}。版本 {POLICY_VERSION}，生效日期 {EFFECTIVE_DATE}。"],
    ],
}

TERMS["en-US"] = {
    "title": "Terms of Sale & Technical Disclaimer", "nav": "Terms of Sale", "back": "Back to home",
    "lead": "This page defines the nature and scope of the product information, specifications, images and quotations published on this website, and forms the reference basis for the technical agreement and sales contract between the parties.",
    "sections": [
        ["Nature of website information", "Product descriptions, specifications, inspection capabilities, application cases and images on this site (all language editions) are for selection guidance only and do not constitute an offer, a performance guarantee or a contractual commitment. Final specifications, configuration, price, lead time and acceptance criteria are governed by the signed technical agreement, quotation and sales contract."],
        ["Specifications and operating conditions", "Published accuracy (e.g. ±0.02 mm, 0.0007 mm), throughput (e.g. 4500 PCS/H, 60 pcs/min), resolution (e.g. 8 MP) and inspection capabilities are typical reference values obtained under defined workpieces, lighting, fixture positioning, incoming material condition and parameter settings. Actual results depend on site conditions and must be confirmed by joint sample testing and acceptance."],
        ["Full in-line inspection wording", "'Supports full in-line inspection of the production line' describes the functional scope of the equipment. It does not represent 100% detection or zero misses under all conditions. Detection rate, false-alarm rate and cycle time are governed by the acceptance criteria and technical agreement agreed by both parties."],
        ["Changes to specifications", "Specifications, appearance, software functions and model numbers may change due to product iteration, supply-chain adjustments or customer customisation without prior notice. Changes to an already signed contract require written confirmation by both parties."],
        ["Images and illustrations", "Product photographs, application images, UI screenshots and illustrations are provided for explanatory purposes only. Schematic, rendered or tool-generated images do not represent the delivered appearance or a real inspection result; the physical product and delivery documents prevail."],
        ["Third-party components and trademarks", "Equipment may incorporate generic components supplied by third parties (for example CMOS image sensors). Any third-party name is used solely to describe a component specification and does not imply an original-manufacturer partnership, authorisation, endorsement or product brand ownership. All third-party trademarks belong to their respective owners."],
        ["Warranty and limitation of liability", "Warranty scope, duration, wear parts and exclusions are governed by the sales contract. We are not liable under warranty for faults caused by installation or use contrary to the manual, unauthorised modification, abnormal power or environment, consumable wear, or force majeure. Except where mandatory law provides otherwise, we are not liable for indirect loss, production downtime or lost profit."],
        ["Governing law and disputes", "This notice and subsequent transactions are governed by the laws of the People's Republic of China. The parties shall first seek an amicable settlement; failing that, disputes follow the mechanism agreed in the sales contract. If language versions differ, the Chinese version prevails."],
        ["Contact and version", f"Commercial and technical enquiries: {EMAIL}, phone {TEL}. Version {POLICY_VERSION}, effective {EFFECTIVE_DATE}."],
    ],
}

TERMS["es-MX"] = {
    "title": "Términos de Venta y Aviso Técnico", "nav": "Términos de Venta", "back": "Volver al inicio",
    "lead": "Esta página define la naturaleza y el alcance de la información de producto, especificaciones, imágenes y cotizaciones del sitio, y sirve de base de referencia para el acuerdo técnico y el contrato de compraventa.",
    "sections": [
        ["Naturaleza de la información", "Las descripciones, especificaciones, capacidades de inspección, casos de aplicación e imágenes del sitio (todas las ediciones de idioma) son únicamente una guía de selección y no constituyen oferta, garantía de desempeño ni compromiso contractual. Las especificaciones finales, configuración, precio, plazo de entrega y criterios de aceptación se rigen por el acuerdo técnico, la cotización y el contrato firmados."],
        ["Especificaciones y condiciones de operación", "La precisión (p. ej. ±0.02 mm, 0.0007 mm), el ritmo (p. ej. 4500 PCS/H, 60 pzs/min), la resolución (p. ej. 8 MP) y las capacidades publicadas son valores de referencia típicos obtenidos con piezas, iluminación, posicionamiento de utillaje, estado del material y parámetros definidos. El resultado real depende de las condiciones de planta y debe confirmarse con pruebas de muestra y aceptación conjunta."],
        ["Alcance de la inspección total", "«Admite inspección total en línea» describe el alcance funcional del equipo y no representa una detección del 100% ni ausencia de omisiones en cualquier condición. La tasa de detección, las falsas alarmas y el ciclo se rigen por los criterios de aceptación y el acuerdo técnico pactados."],
        ["Cambios de especificaciones", "Las especificaciones, la apariencia, las funciones de software y los modelos pueden cambiar por iteración del producto, ajustes de cadena de suministro o personalización, sin previo aviso. Todo cambio en un contrato ya firmado requiere confirmación escrita de ambas partes."],
        ["Imágenes e ilustraciones", "Las fotografías de producto, imágenes de aplicación, capturas de interfaz e ilustraciones tienen fines explicativos. Las imágenes esquemáticas, renderizadas o generadas con herramientas no representan la apariencia entregada ni un resultado real de inspección; prevalecen el producto físico y la documentación de entrega."],
        ["Componentes y marcas de terceros", "El equipo puede incorporar componentes genéricos de terceros (por ejemplo, sensores de imagen CMOS). Cualquier nombre de tercero se usa solo para describir una especificación y no implica colaboración, autorización, respaldo ni titularidad de marca del fabricante original. Las marcas pertenecen a sus titulares."],
        ["Garantía y limitación de responsabilidad", "El alcance, plazo, piezas de desgaste y exclusiones de la garantía se rigen por el contrato. No cubrimos fallas por instalación o uso contrario al manual, modificaciones no autorizadas, alimentación o ambiente anormales, desgaste de consumibles o fuerza mayor. Salvo disposición legal imperativa, no respondemos por daños indirectos, paros de producción ni lucro cesante."],
        ["Ley aplicable y controversias", "Este aviso y las operaciones posteriores se rigen por la legislación de la República Popular China. Las partes procurarán primero una solución amistosa y, en su defecto, aplicarán el mecanismo pactado en el contrato. En caso de discrepancia entre versiones, prevalece la versión en chino."],
        ["Contacto y versión", f"Consultas comerciales y técnicas: {EMAIL}, teléfono {TEL}. Versión {POLICY_VERSION}, vigente desde {EFFECTIVE_DATE}."],
    ],
}

TERMS["en-SG"] = dict(
    TERMS["en-US"],
    title="Terms of Sale (Singapore / Asia-Pacific)", nav="Terms of Sale",
    lead="For the Singapore / Asia-Pacific English edition: this page defines the nature and scope of the product information, specifications, images and quotations published on this website, and forms the reference basis for the technical agreement and sales contract.")

TERMS["id-ID"] = {
    "title": "Syarat Penjualan & Pernyataan Teknis", "nav": "Syarat Penjualan", "back": "Kembali ke beranda",
    "lead": "Halaman ini menjelaskan sifat dan cakupan informasi produk, spesifikasi, gambar, dan penawaran di situs ini sebagai dasar acuan perjanjian teknis dan kontrak penjualan.",
    "sections": [
        ["Sifat informasi", "Deskripsi produk, spesifikasi, kemampuan inspeksi, kasus aplikasi, dan gambar di situs (semua edisi bahasa) hanya sebagai panduan pemilihan dan bukan penawaran, jaminan kinerja, atau komitmen kontrak. Spesifikasi akhir, konfigurasi, harga, waktu pengiriman, dan kriteria penerimaan diatur oleh perjanjian teknis, penawaran, dan kontrak yang ditandatangani."],
        ["Spesifikasi dan kondisi operasi", "Akurasi (mis. ±0.02 mm, 0.0007 mm), kecepatan (mis. 4500 PCS/H, 60 pcs/menit), resolusi (mis. 8 MP), dan kemampuan yang dipublikasikan adalah nilai acuan tipikal pada kondisi benda kerja, pencahayaan, posisi fixture, kondisi material, dan parameter yang ditetapkan. Hasil nyata bergantung pada kondisi lapangan dan harus dikonfirmasi melalui uji sampel dan penerimaan bersama."],
        ["Makna inspeksi menyeluruh", "'Mendukung inspeksi menyeluruh secara inline' menjelaskan cakupan fungsi peralatan, bukan deteksi 100% atau tanpa kegagalan dalam segala kondisi. Tingkat deteksi, alarm palsu, dan siklus diatur oleh kriteria penerimaan dan perjanjian teknis yang disepakati."],
        ["Perubahan spesifikasi", "Spesifikasi, tampilan, fungsi perangkat lunak, dan nomor model dapat berubah karena iterasi produk, penyesuaian rantai pasok, atau kustomisasi tanpa pemberitahuan sebelumnya. Perubahan pada kontrak yang telah ditandatangani memerlukan konfirmasi tertulis kedua belah pihak."],
        ["Gambar dan ilustrasi", "Foto produk, gambar aplikasi, tangkapan layar antarmuka, dan ilustrasi hanya untuk penjelasan. Gambar skematik, render, atau hasil alat bantu tidak mewakili tampilan produk yang dikirim maupun hasil inspeksi nyata; produk fisik dan dokumen pengiriman yang berlaku."],
        ["Komponen dan merek pihak ketiga", "Peralatan dapat menggunakan komponen umum dari pihak ketiga (misalnya sensor citra CMOS). Nama pihak ketiga hanya menjelaskan spesifikasi komponen dan tidak menunjukkan kerja sama, otorisasi, dukungan, atau kepemilikan merek dari produsen asal. Merek tetap menjadi milik pemegangnya."],
        ["Garansi dan batas tanggung jawab", "Cakupan, masa berlaku, suku cadang aus, dan pengecualian garansi diatur dalam kontrak. Kami tidak bertanggung jawab atas kerusakan akibat pemasangan atau penggunaan yang menyimpang dari manual, modifikasi tanpa izin, daya atau lingkungan abnormal, keausan konsumabel, atau force majeure. Kecuali diwajibkan hukum, kami tidak menanggung kerugian tidak langsung, penghentian produksi, atau kehilangan laba."],
        ["Hukum yang berlaku dan sengketa", "Pernyataan ini dan transaksi berikutnya tunduk pada hukum Republik Rakyat Tiongkok. Para pihak mengupayakan musyawarah terlebih dahulu; jika gagal, digunakan mekanisme yang disepakati dalam kontrak. Jika versi bahasa berbeda, versi bahasa Tionghoa yang berlaku."],
        ["Kontak dan versi", f"Pertanyaan komersial dan teknis: {EMAIL}, telepon {TEL}. Versi {POLICY_VERSION}, berlaku {EFFECTIVE_DATE}."],
    ],
}

TERMS["th-TH"] = {
    "title": "เงื่อนไขการขายและข้อความปฏิเสธทางเทคนิค", "nav": "เงื่อนไขการขาย", "back": "กลับสู่หน้าแรก",
    "lead": "หน้านี้กำหนดลักษณะและขอบเขตของข้อมูลผลิตภัณฑ์ ข้อมูลจำเพาะ รูปภาพ และใบเสนอราคาบนเว็บไซต์ เพื่อใช้เป็นแนวทางอ้างอิงสำหรับความตกลงทางเทคนิคและสัญญาขาย",
    "sections": [
        ["ลักษณะของข้อมูล", "คำอธิบายผลิตภัณฑ์ ข้อมูลจำเพาะ ความสามารถในการตรวจสอบ กรณีการใช้งาน และรูปภาพบนเว็บไซต์ทุกภาษา เป็นเพียงแนวทางในการเลือกผลิตภัณฑ์ ไม่ถือเป็นคำเสนอ การรับประกันสมรรถนะ หรือพันธกรณีตามสัญญา ข้อมูลจำเพาะ การกำหนดค่า ราคา ระยะเวลาส่งมอบ และเกณฑ์การรับมอบงานสุดท้ายเป็นไปตามความตกลงทางเทคนิค ใบเสนอราคา และสัญญาที่ลงนาม"],
        ["ข้อมูลจำเพาะและเงื่อนไขการทำงาน", "ค่าความแม่นยำ (เช่น ±0.02 มม., 0.0007 มม.) อัตราการผลิต (เช่น 4500 PCS/H, 60 ชิ้น/นาที) ความละเอียด (เช่น 8 MP) และความสามารถที่เผยแพร่ เป็นค่าอ้างอิงทั่วไปภายใต้ชิ้นงาน แสง การจัดตำแหน่งจิก สภาพวัตถุดิบ และการตั้งค่าที่กำหนด ผลจริงขึ้นกับสภาพหน้างานและต้องยืนยันด้วยการทดสอบตัวอย่างและการรับมอบร่วมกัน"],
        ["ความหมายของการตรวจสอบทั้งหมด", "「รองรับการตรวจสอบทั้งหมดแบบอินไลน์」อธิบายขอบเขตฟังก์ชันของเครื่อง ไม่ได้หมายถึงการตรวจพบ 100% หรือไม่มีสิ่งตกหล่นในทุกเงื่อนไข อัตราการตรวจพบ การแจ้งเตือนผิดพลาด และรอบการทำงานเป็นไปตามเกณฑ์รับมอบและความตกลงทางเทคนิคที่ตกลงกัน"],
        ["การเปลี่ยนแปลงข้อมูลจำเพาะ", "ข้อมูลจำเพาะ รูปลักษณ์ ฟังก์ชันซอฟต์แวร์ และรุ่นอาจเปลี่ยนแปลงจากการพัฒนาผลิตภัณฑ์ การปรับห่วงโซ่อุปทาน หรือการปรับแต่งตามลูกค้า โดยไม่ต้องแจ้งล่วงหน้า การเปลี่ยนแปลงในสัญญาที่ลงนามแล้วต้องได้รับการยืนยันเป็นลายลักษณ์อักษรจากทั้งสองฝ่าย"],
        ["รูปภาพและภาพประกอบ", "ภาพถ่ายผลิตภัณฑ์ ภาพการใช้งาน ภาพหน้าจอ และภาพประกอบมีไว้เพื่ออธิบายเท่านั้น ภาพเขียนแบบ ภาพเรนเดอร์ หรือภาพจากเครื่องมือสร้างภาพไม่แสดงถึงรูปลักษณ์ที่ส่งมอบหรือผลการตรวจสอบจริง ให้ถือผลิตภัณฑ์จริงและเอกสารส่งมอบเป็นหลัก"],
        ["ชิ้นส่วนและเครื่องหมายการค้าของบุคคลที่สาม", "เครื่องอาจใช้ชิ้นส่วนทั่วไปจากบุคคลที่สาม (เช่น เซนเซอร์ภาพ CMOS) ชื่อบุคคลที่สามใช้เพื่ออธิบายข้อมูลจำเพาะของชิ้นส่วนเท่านั้น ไม่สื่อถึงความร่วมมือ การอนุญาต การรับรอง หรือความเป็นเจ้าของแบรนด์จากผู้ผลิตรายเดิม เครื่องหมายการค้ายังคงเป็นของเจ้าของ"],
        ["การรับประกันและข้อจำกัดความรับผิด", "ขอบเขต ระยะเวลา ชิ้นส่วนสึกหรอ และข้อยกเว้นของการรับประกันเป็นไปตามสัญญา เราไม่รับผิดต่อความเสียหายจากการติดตั้งหรือใช้งานผิดจากคู่มือ การดัดแปลงโดยไม่ได้รับอนุญาต ไฟฟ้าหรือสภาพแวดล้อมผิดปกติ การสึกหรอของวัสดุสิ้นเปลือง หรือเหตุสุดวิสัย เว้นแต่กฎหมายบังคับไว้เป็นอย่างอื่น เราไม่รับผิดต่อความเสียหายทางอ้อม การหยุดผลิต หรือการสูญเสียกำไร"],
        ["กฎหมายที่ใช้บังคับและข้อพิพาท", "ประกาศนี้และธุรกรรมที่ตามมาอยู่ภายใต้กฎหมายของสาธารณรัฐประชาชนจีน ให้คู่สัญญาเจรจาอย่างมิตรไมตรีก่อน หากไม่เป็นผลให้ใช้กลไกที่ตกลงในสัญญา หากภาษาต่างกัน ให้ถือฉบับภาษาจีนเป็นหลัก"],
        ["ติดต่อและเวอร์ชัน", f"สอบถามด้านการค้าและเทคนิค: {EMAIL} โทร {TEL} เวอร์ชัน {POLICY_VERSION} มีผลตั้งแต่ {EFFECTIVE_DATE}"],
    ],
}

TERMS["vi-VN"] = {
    "title": "Điều khoản Bán hàng & Tuyên bố Kỹ thuật", "nav": "Điều khoản Bán hàng", "back": "Về trang chủ",
    "lead": "Trang này xác định tính chất và phạm vi của thông tin sản phẩm, thông số, hình ảnh và báo giá trên website, làm cơ sở tham chiếu cho thỏa thuận kỹ thuật và hợp đồng mua bán.",
    "sections": [
        ["Tính chất thông tin", "Mô tả sản phẩm, thông số, năng lực kiểm tra, trường hợp ứng dụng và hình ảnh trên website (mọi ngôn ngữ) chỉ để tham khảo chọn lựa, không phải chào hàng, bảo đảm hiệu năng hay cam kết hợp đồng. Thông số cuối cùng, cấu hình, giá, thời gian giao hàng và tiêu chuẩn nghiệm thu theo thỏa thuận kỹ thuật, báo giá và hợp đồng đã ký."],
        ["Thông số và điều kiện vận hành", "Độ chính xác (ví dụ ±0.02 mm, 0.0007 mm), tốc độ (4500 PCS/H, 60 chiếc/phút), độ phân giải (8 MP) và năng lực công bố là giá trị tham khảo điển hình trong điều kiện phôi, ánh sáng, định vị đồ gá, trạng thái nguyên liệu và thông số đã quy định. Kết quả thực tế phụ thuộc điều kiện hiện trường và phải được xác nhận bằng thử mẫu và nghiệm thu chung."],
        ["Cách hiểu kiểm tra toàn bộ", "「Hỗ trợ kiểm tra toàn bộ trực tuyến trên dây chuyền」mô tả phạm vi chức năng của thiết bị, không có nghĩa là phát hiện 100% hay không bỏ sót trong mọi điều kiện. Tỷ lệ phát hiện, báo động giả và chu kỳ theo tiêu chuẩn nghiệm thu và thỏa thuận kỹ thuật hai bên."],
        ["Thay đổi thông số", "Thông số, hình thức, chức năng phần mềm và mã model có thể thay đổi do cải tiến sản phẩm, điều chỉnh chuỗi cung ứng hoặc tùy biến theo khách hàng mà không báo trước. Thay đổi trong hợp đồng đã ký phải có xác nhận bằng văn bản của hai bên."],
        ["Hình ảnh và minh họa", "Ảnh sản phẩm, ảnh ứng dụng, ảnh giao diện và hình minh họa chỉ nhằm giải thích. Ảnh sơ đồ, ảnh dựng hoặc ảnh tạo bằng công cụ không thể hiện hình dạng giao hàng hay kết quả kiểm tra thực; sản phẩm thực và tài liệu giao hàng là căn cứ."],
        ["Linh kiện và nhãn hiệu bên thứ ba", "Thiết bị có thể dùng linh kiện thông dụng của bên thứ ba (ví dụ cảm biến hình ảnh CMOS). Tên bên thứ ba chỉ để mô tả thông số linh kiện, không hàm ý hợp tác, ủy quyền, chứng thực hay quyền sở hữu thương hiệu của nhà sản xuất gốc. Nhãn hiệu thuộc về chủ sở hữu."],
        ["Bảo hành và giới hạn trách nhiệm", "Phạm vi, thời hạn, vật tư hao mòn và trường hợp loại trừ theo hợp đồng. Chúng tôi không bảo hành lỗi do lắp đặt hoặc sử dụng sai hướng dẫn, tự ý sửa đổi, điện hoặc môi trường bất thường, hao mòn vật tư hoặc bất khả kháng. Trừ khi pháp luật bắt buộc, chúng tôi không chịu trách nhiệm với tổn thất gián tiếp, dừng sản xuất hay mất lợi nhuận."],
        ["Luật áp dụng và tranh chấp", "Tuyên bố này và giao dịch sau đó chịu sự điều chỉnh của pháp luật Cộng hòa Nhân dân Trung Hoa. Hai bên ưu tiên thương lượng; nếu không đạt được, áp dụng cơ chế đã thỏa thuận trong hợp đồng. Nếu các bản ngôn ngữ khác nhau, bản tiếng Trung là căn cứ."],
        ["Liên hệ và phiên bản", f"Tư vấn thương mại và kỹ thuật: {EMAIL}, điện thoại {TEL}. Phiên bản {POLICY_VERSION}, hiệu lực {EFFECTIVE_DATE}."],
    ],
}

TERMS["ko-KR"] = {
    "title": "판매 조건 및 기술 고지", "nav": "판매 조건", "back": "홈으로",
    "lead": "본 페이지는 사이트에 게시된 제품 정보, 사양, 이미지 및 견적의 성격과 적용 범위를 정하며, 향후 기술 합의서 및 판매 계약의 참고 기준이 됩니다.",
    "sections": [
        ["웹사이트 정보의 성격", "본 사이트(모든 언어판)의 제품 설명, 사양, 검사 능력, 적용 사례 및 이미지는 선정 참고용이며 청약, 성능 보증 또는 계약상 확약이 아닙니다. 최종 사양, 구성, 가격, 납기 및 검수 기준은 양 당사자가 서명한 기술 합의서, 견적서 및 판매 계약에 따릅니다."],
        ["사양 및 운전 조건", "게시된 정밀도(예: ±0.02 mm, 0.0007 mm), 처리 속도(예: 4500 PCS/H, 60 개/분), 해상도(예: 8 MP) 및 검사 능력은 규정된 공작물, 조명, 지그 위치, 원자재 상태 및 파라미터 설정에서의 대표 참고값입니다. 실제 성능은 현장 조건에 따라 달라지며 공동 샘플 테스트와 검수로 확정해야 합니다."],
        ["전수 검사 표현", "「생산 라인 전수 인라인 검사 지원」은 장비의 기능 범위를 설명하며, 모든 조건에서 100% 검출 또는 무누락을 의미하지 않습니다. 검출률, 오검률 및 사이클 타임은 양측이 합의한 검수 기준과 기술 합의서에 따릅니다."],
        ["사양 변경", "제품 개선, 공급망 조정 또는 고객 맞춤화로 사양, 외관, 소프트웨어 기능 및 모델명이 사전 통지 없이 변경될 수 있습니다. 이미 체결된 계약의 변경은 양측 서면 확인이 필요합니다."],
        ["이미지 및 도해", "제품 사진, 적용 이미지, UI 스크린샷 및 도해는 설명 목적입니다. 개략도, 렌더링 또는 생성 도구로 만든 이미지는 실제 납품 외형이나 실제 검사 결과를 나타내지 않으며 실물과 납품 문서가 우선합니다."],
        ["제3자 부품 및 상표", "장비에는 제3자가 공급하는 범용 부품(예: CMOS 이미지 센서)이 사용될 수 있습니다. 제3자 명칭은 부품 사양 설명을 위한 것으로, 원 제조사와의 제휴·승인·보증 또는 완제품 브랜드 소속을 의미하지 않습니다. 모든 제3자 상표는 권리자에게 귀속됩니다."],
        ["보증 및 책임 범위", "보증 범위, 기간, 소모품 및 제외 사항은 판매 계약에 따릅니다. 설명서와 다른 설치·사용, 무단 개조, 외부 전원 또는 환경 이상, 소모품 마모, 불가항력으로 인한 고장은 보증하지 않습니다. 강행 법규가 정하는 경우를 제외하고 간접 손실, 생산 중단 손실 또는 이익 손실에 대해 책임지지 않습니다."],
        ["준거법 및 분쟁", "본 고지 및 후속 거래는 중화인민공화국 법률에 따릅니다. 당사자는 우선 우호적으로 협의하고, 실패 시 판매 계약에서 합의한 분쟁 해결 방식에 따릅니다. 언어판 간 의미가 다를 경우 중국어판이 우선합니다."],
        ["연락처 및 버전", f"영업·기술 문의: {EMAIL}, 전화 {TEL}. 버전 {POLICY_VERSION}, 시행일 {EFFECTIVE_DATE}."],
    ],
}

TERMS["ja-JP"] = {
    "title": "販売条件および技術上の注意", "nav": "販売条件", "back": "ホームへ戻る",
    "lead": "本ページは、本サイトに掲載する製品情報・仕様・画像・見積の性質と適用範囲を定め、両者の技術協定書および売買契約の参考基礎とするものです。",
    "sections": [
        ["ウェブサイト情報の性質", "本サイト（全言語版）の製品説明、仕様、検査能力、適用事例および画像は選定の参考情報であり、申込み、性能保証または契約上の確約を構成しません。最終仕様、構成、価格、納期および検収基準は、両者が署名した技術協定書、見積書および売買契約に従います。"],
        ["仕様と稼働条件", "掲載される精度（例：±0.02 mm、0.0007 mm）、タクト（例：4500 PCS/H、60 個/分）、解像度（例：8 MP）および検査能力は、規定のワーク、照明、治具位置決め、材料状態およびパラメータ設定下で得られる代表参考値です。実際の結果は現場条件に左右され、双方のサンプル試験と検収により確定します。"],
        ["全数検査の表現", "「生産ラインの全数インライン検査に対応」は装置の機能範囲を説明するものであり、あらゆる条件下での 100% 検出または見逃しゼロを意味しません。検出率、誤報率およびサイクルタイムは双方が合意した検収基準と技術協定書に従います。"],
        ["仕様変更", "製品改良、供給網の調整または顧客仕様により、仕様、外観、ソフトウェア機能および型番が事前通知なく変更される場合があります。締結済み契約の変更は両者の書面確認を要します。"],
        ["画像・イラスト", "製品写真、適用画像、UI スクリーンショットおよびイラストは説明目的のみです。模式図、レンダリング画像または生成ツールによる画像は、実際の納品外観や実際の検査結果を示すものではなく、現品および納品文書を優先します。"],
        ["第三者の部品および商標", "装置には第三者が供給する汎用部品（例：CMOS イメージセンサー）が含まれる場合があります。第三者名は部品仕様の説明にのみ使用し、元メーカーとの提携・許諾・推奨または完成品ブランドの帰属を示すものではありません。第三者の商標は権利者に帰属します。"],
        ["保証および責任範囲", "保証の範囲、期間、消耗品および除外事項は売買契約に従います。取扱説明書に反する設置・使用、無断改造、電源・環境の異常、消耗品の摩耗または不可抗力に起因する故障は保証対象外です。強行法規に定める場合を除き、間接損害、生産停止損失または逸失利益について責任を負いません。"],
        ["準拠法および紛争", "本告知および後続の取引は中華人民共和国の法律に準拠します。両者はまず友好的に協議し、不成立の場合は売買契約で合意した紛争解決方法に従います。言語版間に相違がある場合は中国語版を優先します。"],
        ["連絡先および版数", f"営業・技術に関するお問い合わせ：{EMAIL}、電話 {TEL}。版数 {POLICY_VERSION}、施行日 {EFFECTIVE_DATE}。"],
    ],
}

TERMS["ms-MY"] = {
    "title": "Syarat Jualan & Notis Teknikal", "nav": "Syarat Jualan", "back": "Kembali ke laman utama",
    "lead": "Halaman ini menentukan sifat dan skop maklumat produk, spesifikasi, imej dan sebut harga di laman ini sebagai asas rujukan bagi perjanjian teknikal dan kontrak jualan.",
    "sections": [
        ["Sifat maklumat", "Penerangan produk, spesifikasi, keupayaan pemeriksaan, kes aplikasi dan imej di laman ini (semua edisi bahasa) adalah panduan pemilihan sahaja dan bukan tawaran, jaminan prestasi atau komitmen kontrak. Spesifikasi akhir, konfigurasi, harga, masa penghantaran dan kriteria penerimaan ditentukan oleh perjanjian teknikal, sebut harga dan kontrak yang ditandatangani."],
        ["Spesifikasi dan keadaan operasi", "Ketepatan (cth. ±0.02 mm, 0.0007 mm), kadar (cth. 4500 PCS/H, 60 keping/min), resolusi (cth. 8 MP) dan keupayaan yang diterbitkan ialah nilai rujukan lazim di bawah bahan kerja, pencahayaan, kedudukan lekapan, keadaan bahan dan tetapan parameter yang ditetapkan. Hasil sebenar bergantung pada keadaan tapak dan mesti disahkan melalui ujian sampel dan penerimaan bersama."],
        ["Maksud pemeriksaan menyeluruh", "「Menyokong pemeriksaan menyeluruh secara dalam talian」menerangkan skop fungsi peralatan, bukan pengesanan 100% atau tiada keciciran dalam semua keadaan. Kadar pengesanan, penggera palsu dan masa kitaran ditentukan oleh kriteria penerimaan dan perjanjian teknikal yang dipersetujui."],
        ["Perubahan spesifikasi", "Spesifikasi, rupa, fungsi perisian dan nombor model boleh berubah akibat lelaran produk, pelarasan rantaian bekalan atau penyesuaian pelanggan tanpa notis awal. Perubahan kepada kontrak sedia ada memerlukan pengesahan bertulis kedua-dua pihak."],
        ["Imej dan ilustrasi", "Foto produk, imej aplikasi, tangkapan skrin antara muka dan ilustrasi adalah untuk penerangan sahaja. Imej skematik, render atau imej hasil alat tidak mewakili rupa sebenar yang dihantar atau keputusan pemeriksaan sebenar; produk fizikal dan dokumen penghantaran diutamakan."],
        ["Komponen dan tanda dagangan pihak ketiga", "Peralatan mungkin menggunakan komponen generik pihak ketiga (contohnya sensor imej CMOS). Nama pihak ketiga hanya menerangkan spesifikasi komponen dan tidak membayangkan kerjasama, kebenaran, sokongan atau pemilikan jenama pengeluar asal. Tanda dagangan kekal milik pemegangnya."],
        ["Waranti dan had liabiliti", "Skop, tempoh, alat ganti haus dan pengecualian waranti ditentukan oleh kontrak. Kami tidak menanggung kerosakan akibat pemasangan atau penggunaan menyimpang daripada manual, pengubahsuaian tanpa kebenaran, bekalan kuasa atau persekitaran tidak normal, kehausan bahan guna habis atau force majeure. Kecuali dikehendaki undang-undang, kami tidak bertanggungjawab bagi kerugian tidak langsung, pemberhentian pengeluaran atau kehilangan keuntungan."],
        ["Undang-undang terpakai dan pertikaian", "Notis ini dan urus niaga seterusnya tertakluk kepada undang-undang Republik Rakyat China. Pihak-pihak terlebih dahulu berunding secara baik; jika gagal, mekanisme yang dipersetujui dalam kontrak diguna pakai. Jika versi bahasa berbeza, versi bahasa Cina diutamakan."],
        ["Hubungan dan versi", f"Pertanyaan komersial dan teknikal: {EMAIL}, telefon {TEL}. Versi {POLICY_VERSION}, berkuat kuasa {EFFECTIVE_DATE}."],
    ],
}

TERMS["ru-RU"] = {
    "title": "Условия продажи и техническое уведомление", "nav": "Условия продажи", "back": "На главную",
    "lead": "Настоящая страница определяет характер и объём информации о продуктах, характеристик, изображений и коммерческих предложений сайта и служит основой для технического соглашения и договора купли-продажи.",
    "sections": [
        ["Характер информации", "Описания продуктов, характеристики, возможности контроля, примеры применения и изображения на сайте (все языковые версии) носят справочный характер для подбора и не являются офертой, гарантией характеристик или договорным обязательством. Окончательные спецификации, комплектация, цена, срок поставки и критерии приёмки определяются подписанными техническим соглашением, коммерческим предложением и договором."],
        ["Характеристики и условия эксплуатации", "Приведённые точность (напр. ±0.02 мм, 0.0007 мм), производительность (напр. 4500 PCS/H, 60 шт/мин), разрешение (напр. 8 MP) и возможности контроля являются типовыми справочными значениями при определённых заготовках, освещении, позиционировании оснастки, состоянии материала и настройках. Фактический результат зависит от условий площадки и подтверждается совместными испытаниями образцов и приёмкой."],
        ["Формулировка о сплошном контроле", "«Поддерживает сплошной контроль на линии» описывает функциональные возможности оборудования и не означает 100% обнаружение или отсутствие пропусков при любых условиях. Доля обнаружения, ложные срабатывания и время цикла определяются согласованными критериями приёмки и техническим соглашением."],
        ["Изменение характеристик", "Характеристики, внешний вид, функции ПО и номера моделей могут изменяться из-за развития продукта, корректировок цепочки поставок или кастомизации без предварительного уведомления. Изменения в уже подписанном договоре требуют письменного подтверждения обеих сторон."],
        ["Изображения и иллюстрации", "Фотографии изделий, изображения применений, снимки интерфейса и иллюстрации приведены только для пояснения. Схематические, отрендеренные или созданные инструментами изображения не отражают поставляемый внешний вид или реальный результат контроля; приоритет имеют физический продукт и документы поставки."],
        ["Компоненты и товарные знаки третьих лиц", "Оборудование может содержать универсальные компоненты третьих лиц (например, КМОП-датчики изображения). Наименование третьего лица используется лишь для описания характеристики компонента и не означает партнёрство, авторизацию, одобрение или принадлежность бренда производителю-оригиналу. Товарные знаки принадлежат их владельцам."],
        ["Гарантия и ограничение ответственности", "Объём, срок, быстроизнашивающиеся части и исключения гарантии определяются договором. Мы не отвечаем по гарантии за неисправности из-за монтажа или эксплуатации вопреки руководству, несанкционированных изменений, аномального питания или среды, износа расходных материалов либо форс-мажора. Кроме случаев императивной нормы закона, мы не отвечаем за косвенные убытки, простои производства или упущенную выгоду."],
        ["Применимое право и споры", "Настоящее уведомление и последующие сделки регулируются правом Китайской Народной Республики. Стороны сначала пытаются урегулировать спор мирно, а при недостижении согласия применяют механизм, согласованный в договоре. При расхождении языковых версий приоритет имеет версия на китайском языке."],
        ["Контакты и версия", f"Коммерческие и технические вопросы: {EMAIL}, тел. {TEL}. Версия {POLICY_VERSION}, действует с {EFFECTIVE_DATE}."],
    ],
}

# ---------------------------------------------------------------- short strings
FOOTER_LABELS = {
    "zh-CN": ("隐私政策", "销售条款", "技术声明"),
    "en-US": ("Privacy Policy", "Terms of Sale", "Technical Disclaimer"),
    "en-SG": ("Privacy Policy", "Terms of Sale", "Technical Disclaimer"),
    "es-MX": ("Aviso de Privacidad", "Términos de Venta", "Aviso Técnico"),
    "id-ID": ("Kebijakan Privasi", "Syarat Penjualan", "Pernyataan Teknis"),
    "th-TH": ("นโยบายความเป็นส่วนตัว", "เงื่อนไขการขาย", "ข้อความปฏิเสธทางเทคนิค"),
    "vi-VN": ("Chính sách Riêng tư", "Điều khoản Bán hàng", "Tuyên bố Kỹ thuật"),
    "ko-KR": ("개인정보 처리방침", "판매 조건", "기술 고지"),
    "ja-JP": ("プライバシーポリシー", "販売条件", "技術上の注意"),
    "ms-MY": ("Dasar Privasi", "Syarat Jualan", "Notis Teknikal"),
    "ru-RU": ("Конфиденциальность", "Условия продажи", "Техническое уведомление"),
}

DISCLAIMER = {
    "zh-CN": "技术声明：以上参数为规定工况下的典型参考值，仅供选型参考，不构成性能保证；实际检出率、精度与节拍取决于工件、光照、治具及参数设定，以双方技术协议与验收标准为准。规格如有变更，恕不另行通知。详见《销售条款与技术声明》。",
    "en-US": "Technical notice: the values above are typical reference figures under defined conditions, for selection guidance only, and do not constitute a performance guarantee. Actual detection rate, accuracy and cycle time depend on the workpiece, lighting, fixture and parameter settings and are governed by the signed technical agreement and acceptance criteria. Specifications may change without notice. See Terms of Sale & Technical Disclaimer.",
    "en-SG": "Technical notice: the values above are typical reference figures under defined conditions, for selection guidance only, and do not constitute a performance guarantee. Actual detection rate, accuracy and cycle time depend on the workpiece, lighting, fixture and parameter settings and are governed by the signed technical agreement and acceptance criteria. Specifications may change without notice. See Terms of Sale & Technical Disclaimer.",
    "es-MX": "Aviso técnico: los valores anteriores son referencias típicas en condiciones definidas, solo para orientar la selección, y no constituyen garantía de desempeño. La tasa de detección, precisión y ritmo reales dependen de la pieza, iluminación, utillaje y parámetros y se rigen por el acuerdo técnico y los criterios de aceptación firmados. Las especificaciones pueden cambiar sin previo aviso. Consulte Términos de Venta y Aviso Técnico.",
    "id-ID": "Catatan teknis: nilai di atas adalah acuan tipikal pada kondisi yang ditetapkan, hanya untuk panduan pemilihan, dan bukan jaminan kinerja. Tingkat deteksi, akurasi, dan siklus nyata bergantung pada benda kerja, pencahayaan, fixture, dan parameter serta diatur oleh perjanjian teknis dan kriteria penerimaan. Spesifikasi dapat berubah tanpa pemberitahuan. Lihat Syarat Penjualan & Pernyataan Teknis.",
    "th-TH": "หมายเหตุทางเทคนิค: ค่าข้างต้นเป็นค่าอ้างอิงทั่วไปภายใต้เงื่อนไขที่กำหนด เพื่อเป็นแนวทางการเลือกเท่านั้น ไม่ถือเป็นการรับประกันสมรรถนะ อัตราการตรวจพบ ความแม่นยำ และรอบการทำงานจริงขึ้นกับชิ้นงาน แสง จิก และพารามิเตอร์ และเป็นไปตามความตกลงทางเทคนิคและเกณฑ์รับมอบ ข้อมูลจำเพาะอาจเปลี่ยนแปลงโดยไม่แจ้งล่วงหน้า โปรดดูเงื่อนไขการขายและข้อความปฏิเสธทางเทคนิค",
    "vi-VN": "Lưu ý kỹ thuật: các giá trị trên là giá trị tham khảo điển hình trong điều kiện quy định, chỉ để hướng dẫn chọn lựa, không phải bảo đảm hiệu năng. Tỷ lệ phát hiện, độ chính xác và chu kỳ thực tế phụ thuộc vào phôi, ánh sáng, đồ gá và thông số, theo thỏa thuận kỹ thuật và tiêu chuẩn nghiệm thu đã ký. Thông số có thể thay đổi mà không báo trước. Xem Điều khoản Bán hàng & Tuyên bố Kỹ thuật.",
    "ko-KR": "기술 고지: 위 값은 규정된 조건에서의 대표 참고값으로 선정 참고용이며 성능을 보증하지 않습니다. 실제 검출률, 정밀도 및 사이클 타임은 공작물, 조명, 지그 및 파라미터 설정에 따라 달라지며 서명된 기술 합의서와 검수 기준에 따릅니다. 사양은 예고 없이 변경될 수 있습니다. 판매 조건 및 기술 고지를 참조하십시오.",
    "ja-JP": "技術上の注意：上記の値は規定条件下での代表参考値であり、選定の参考情報であって性能を保証するものではありません。実際の検出率・精度・サイクルタイムはワーク、照明、治具およびパラメータ設定に左右され、署名済みの技術協定書と検収基準に従います。仕様は予告なく変更される場合があります。販売条件および技術上の注意をご参照ください。",
    "ms-MY": "Notis teknikal: nilai di atas ialah nilai rujukan lazim pada keadaan yang ditetapkan, untuk panduan pemilihan sahaja dan bukan jaminan prestasi. Kadar pengesanan, ketepatan dan masa kitaran sebenar bergantung pada bahan kerja, pencahayaan, lekapan dan tetapan parameter serta ditentukan oleh perjanjian teknikal dan kriteria penerimaan. Spesifikasi boleh berubah tanpa notis. Lihat Syarat Jualan & Notis Teknikal.",
    "ru-RU": "Техническое уведомление: приведённые значения являются типовыми справочными величинами при определённых условиях, предназначены только для подбора и не являются гарантией характеристик. Фактические показатели обнаружения, точности и цикла зависят от заготовки, освещения, оснастки и настроек и определяются подписанным техническим соглашением и критериями приёмки. Характеристики могут изменяться без уведомления. См. Условия продажи и техническое уведомление.",
}

CONSENT = {
    "zh-CN": "我已阅读并同意 {link}，同意贵方按该政策处理我提交的信息。",
    "en-US": "I have read and agree to the {link} and consent to the processing of my submitted data as described there.",
    "en-SG": "I have read and agree to the {link} and consent to the processing of my submitted data as described there.",
    "es-MX": "He leído y acepto el {link} y consiento el tratamiento de mis datos conforme a dicho aviso.",
    "id-ID": "Saya telah membaca dan menyetujui {link} serta menyetujui pemrosesan data yang saya kirim sebagaimana dijelaskan di sana.",
    "th-TH": "ฉันได้อ่านและยินยอม {link} และยินยอมให้ประมวลผลข้อมูลที่ส่งตามที่ระบุในนโยบาย",
    "vi-VN": "Tôi đã đọc và đồng ý với {link}, đồng thời đồng ý cho xử lý dữ liệu tôi gửi theo chính sách đó.",
    "ko-KR": "{link}을(를) 읽고 동의하며, 해당 방침에 따라 제출한 정보가 처리되는 데 동의합니다.",
    "ja-JP": "{link}を読み、同意します。また、同ポリシーに従って送信情報が取り扱われることに同意します。",
    "ms-MY": "Saya telah membaca dan bersetuju dengan {link} serta mempersetujui pemprosesan data yang dihantar seperti yang dinyatakan.",
    "ru-RU": "Я ознакомился(ась) с {link} и согласен(на) на обработку отправленных данных в соответствии с ней.",
}

CONSENT_REQUIRED = {
    "zh-CN": "请先勾选同意隐私政策后再提交。",
    "en-US": "Please accept the Privacy Policy before submitting.",
    "en-SG": "Please accept the Privacy Policy before submitting.",
    "es-MX": "Acepte el Aviso de Privacidad antes de enviar.",
    "id-ID": "Setujui Kebijakan Privasi sebelum mengirim.",
    "th-TH": "กรุณายินยอมนโยบายความเป็นส่วนตัวก่อนส่ง",
    "vi-VN": "Vui lòng đồng ý với Chính sách Riêng tư trước khi gửi.",
    "ko-KR": "제출 전에 개인정보 처리방침에 동의해 주세요.",
    "ja-JP": "送信前にプライバシーポリシーへの同意が必要です。",
    "ms-MY": "Sila terima Dasar Privasi sebelum menghantar.",
    "ru-RU": "Перед отправкой примите Политику конфиденциальности.",
}

# ---------------------------------------------------------------- H4 / M5 / M7 / O1
# Exact visible phrases to replace, per locale. Tuples (old, new).
H4_FIX = {
    "zh-CN": ("实现100%全检零遗漏", "支持产线全数在线检测；实际检出表现以双方技术协议与验收标准为准"),
    "en-US": ("for 100% inspection with no missed parts", "to support full in-line inspection; actual detection performance is subject to the agreed technical specification and acceptance criteria"),
    "en-SG": ("for 100% inspection with no missed parts", "to support full in-line inspection; actual detection performance is subject to the agreed technical specification and acceptance criteria"),
    "es-MX": ("para realizar una inspección del 100% sin omisiones", "para admitir la inspección total en línea; el desempeño real de detección se rige por el acuerdo técnico y los criterios de aceptación pactados"),
    "id-ID": ("untuk melakukan inspeksi penuh 100% tanpa ada yang terlewat", "untuk mendukung inspeksi menyeluruh secara inline; kinerja deteksi nyata diatur oleh perjanjian teknis dan kriteria penerimaan yang disepakati"),
    "th-TH": ("ตรวจสอบทั้งหมด 100% โดยไม่มีการตรวจสอบตกหล่น", "เพื่อรองรับการตรวจสอบทั้งหมดแบบอินไลน์ โดยสมรรถนะการตรวจพบจริงเป็นไปตามความตกลงทางเทคนิคและเกณฑ์การรับมอบที่ตกลงกัน"),
    "vi-VN": ("thực hiện kiểm tra toàn bộ 100% không bỏ sót", "để hỗ trợ kiểm tra toàn bộ trực tuyến; hiệu năng phát hiện thực tế theo thỏa thuận kỹ thuật và tiêu chuẩn nghiệm thu đã thống nhất"),
    "ko-KR": ("검출 누락 없는 100% 전수 검사를 수행합니다", "생산 라인 전수 인라인 검사를 지원하며, 실제 검출 성능은 합의된 기술 사양과 검수 기준에 따릅니다"),
    "ja-JP": ("見逃しのない100%全数検査を実現します", "生産ラインの全数インライン検査に対応し、実際の検出性能は合意済みの技術仕様および検収基準に従います"),
    "ms-MY": ("bagi mencapai pemeriksaan penuh 100% tanpa tertinggal", "bagi menyokong pemeriksaan menyeluruh secara dalam talian; prestasi pengesanan sebenar tertakluk kepada spesifikasi teknikal dan kriteria penerimaan yang dipersetujui"),
    "ru-RU": ("для 100% сплошного контроля без пропусков", "для поддержки сплошного контроля на линии; фактические показатели обнаружения определяются согласованными техническими условиями и критериями приёмки"),
}

M5_FIX = {
    "zh-CN": ("保证产品交期", "有助于稳定生产计划"),
    "en-US": ("protect delivery schedules", "help stabilise production planning"),
    "en-SG": ("protect delivery schedules", "help stabilise production planning"),
    "es-MX": ("garantiza los plazos de entrega del producto", "ayuda a estabilizar el plan de producción"),
    "id-ID": ("menjamin jadwal pengiriman produk", "membantu menstabilkan rencana produksi"),
    "th-TH": ("รับประกันกำหนดส่งมอบผลิตภัณฑ์", "ช่วยให้แผนการผลิตมีเสถียรภาพ"),
    "vi-VN": ("bảo đảm thời gian giao hàng", "giúp ổn định kế hoạch sản xuất"),
    "ko-KR": ("제품 납기 준수", "생산 계획 안정화에 기여"),
    "ja-JP": ("製品納期の確保", "生産計画の安定化に寄与"),
    "ms-MY": ("menjamin tarikh penghantaran produk", "membantu menstabilkan perancangan pengeluaran"),
    "ru-RU": ("соблюдение сроков поставки продукции", "стабилизацию производственного плана"),
}

# M4 + M7: replace the "sensor brand" table header and its "Sony" value.
SENSOR_HEADER = {
    "zh-CN": "图像传感器", "en-US": "Image sensor", "en-SG": "Image sensor",
    "es-MX": "Sensor de imagen", "id-ID": "Sensor citra", "th-TH": "เซนเซอร์ภาพ",
    "vi-VN": "Cảm biến hình ảnh", "ko-KR": "이미지 센서", "ja-JP": "イメージセンサー",
    "ms-MY": "Sensor imej", "ru-RU": "Датчик изображения",
}
SENSOR_VALUE = {
    "zh-CN": "8 MP CMOS（第三方供应）", "en-US": "8 MP CMOS (third-party)",
    "en-SG": "8 MP CMOS (third-party)", "es-MX": "CMOS de 8 MP (tercero)",
    "id-ID": "CMOS 8 MP (pihak ketiga)", "th-TH": "CMOS 8 MP (บุคคลที่สาม)",
    "vi-VN": "CMOS 8 MP (bên thứ ba)", "ko-KR": "8 MP CMOS (제3자 공급)",
    "ja-JP": "8 MP CMOS（第三者供給）", "ms-MY": "CMOS 8 MP (pihak ketiga)",
    "ru-RU": "КМОП 8 Мп (третья сторона)",
}
SENSOR_HEADER_OLD = {
    "zh-CN": "sensor品牌", "en-US": "Sensor Brand", "en-SG": "Sensor Brand",
    "es-MX": "Marca del sensor", "id-ID": "Merek sensor", "th-TH": "ยี่ห้อ sensor",
    "vi-VN": "Thương hiệu sensor", "ko-KR": "sensor 브랜드", "ja-JP": "sensorブランド",
    "ms-MY": "Jenama sensor", "ru-RU": "Марка sensor",
}

O1_FIX_JA = [
    ("標準機の最高速度", "標準機の最大速度"),
    ("最高10個/秒", "最大10個/秒"),
    ("最高10个/秒", "最大10個/秒"),
    ("最高速度", "最大速度"),
]
