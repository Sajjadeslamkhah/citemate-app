import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Citation Intelligence", page_icon="🎓", layout="wide")

def add_seo():
    ga_id = "G-90YJBXFY8W" 
    google_verification = '<meta name="google-site-verification" content="PjsiKrJtJ7MoRpZcOG1IK3VZpNh6WMGmMcnk6OIAHfE" />'
    meta_tags = """
        <meta name="description" content="Citemate Pro: Akademik makaleleriniz için kusursuz Vancouver, APA ve IEEE atıf düzenleme motoru.">
        <meta name="keywords" content="atıf düzenleme, kaynakça oluşturucu, vancouver style, apa 7th, akademik referans motoru, lifegenix">
    """
    ga_code = f"{google_verification}{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"
    st.components.v1.html(ga_code, height=0)

add_seo()

# ==========================================
# 2. HAFIZA BAŞLATMA (KRİTİK HATA ÇÖZÜMÜ)
# ==========================================
# Hata almamak için tüm değişkenleri en başta tanımlıyoruz
if 'refs' not in st.session_state:
    st.session_state.refs = []

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Atıf Motoru"

# ==========================================
# 3. TASARIM (PRESTİJ ODAKLI)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-title { font-size: 62px !important; font-weight: 900 !important; color: #34d399; text-shadow: 0px 0px 25px rgba(52, 211, 153, 0.4); margin-bottom: 0px; letter-spacing: -1px; }
    .sub-title { color: #f8fafc; font-size: 22px; margin-bottom: 45px; font-weight: 300; letter-spacing: 1px; }
    .sidebar-brand { font-size: 28px !important; font-weight: bold; color: #34d399; margin-bottom: 10px; }
    .contact-container { background: #1e293b; padding: 18px; border-radius: 15px; margin-top: 25px; border: 1px solid #334155; }
    .contact-btn { display: block; background: #34d399; color: black !important; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; text-decoration: none; margin-top: 10px; transition: 0.3s ease; }
    .contact-btn:hover { background: #10b981; transform: translateY(-2px); }
    .service-card { background: #161b22; padding: 30px; border-radius: 18px; border-top: 5px solid #34d399; margin-bottom: 25px; }
    .feature-tag { background: #064e3b; color: #34d399; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 6px; text-transform: uppercase; }
    .footer { color: #64748b; font-size: 14px; text-align: center; margin-top: 80px; padding: 25px; border-top: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ (BÜTÜNLEŞİK YAPI)
# ==========================================
with st.sidebar:
    st.markdown('<p class="sidebar-brand">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.caption("Elite Academic Solutions | Powered by Lifegenix")
    st.divider()
    
    # Sayfa Seçimi
    selection = st.radio("SİSTEM MENÜSÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    st.session_state.page = selection
    
    # İletişim Bloğu
    st.markdown("""
        <div class="contact-container">
            <p style="color: #34d399; font-weight: bold; margin-bottom: 5px; font-size: 17px;">📩 Bize Ulaşın</p>
            <p style="color: #94a3b8; font-size: 13px;">Akademik iş birliği ve kurumsal analiz teklifleri için ulaşın.</p>
            <a href="mailto:iletisim@lifegenix.com" class="contact-btn">✉️ Mesaj Gönder</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("© 2026 **Lifegenix Danışmanlık**<br>Tüm hakları saklıdır.", unsafe_allow_html=True)

# ==========================================
# 5. MOTOR FONKSİYONLARI
# ==========================================
def get_cite(query, is_doi=False):
    try:
        url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            d = res.json()['message']
            item = d['items'][0] if 'items' in d else d
            auth = item.get('author', [{'family': 'Anonim'}])[0].get('family')
            if len(item.get('author', [])) > 1: auth += " et al."
            year = "2026"
            if 'published-print' in item: year = str(item['published-print']['date-parts'][0][0])
            return {"title": item.get('title', [''])[0], "author": auth, "year": year, "url": f"https://doi.org/{query}"}
    except: return None

def process_pdf(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 3))])
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
        if doi_match: return get_cite(doi_match.group().strip("/"), is_doi=True)
    except: pass
    return None

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================

if st.session_state.page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi</p>', unsafe_allow_html=True)

    style = st.selectbox("Tercih Edilen Standard:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI Entegrasyonu", "🔍 Global Arama", "📄 Akıllı PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Numarası:", placeholder="10.1016/j.cell...")
        if st.button("Kaynağı İşle", key="btn_doi"):
            res = get_cite(doi_in, True)
            if res: 
                st.session_state.refs.append(res)
                st.rerun()

    with t2:
        q_in = st.text_input("Yayın Başlığı:", placeholder="Makale adını giriniz...")
        if st.button("Veritabanında Ara", key="btn_q"):
            res = get_cite(q_in, False)
            if res: 
                st.session_state.refs.append(res)
                st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle", type="pdf")
        if f and st.button("Metadataları Çözümle"):
            res = process_pdf(f.read())
            if res: 
                st.session_state.refs.append(res)
                st.rerun()
            else: st.warning("Dosyada DOI bulunamadı.")
    
    # SONUÇ ALANI - HATA KORUMALI
    if len(st.session_state.refs) > 0:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = f"{i}. {r['author']}. {r['title']}. {r['year']}." if style == "Vancouver" else f"{r['author']} ({r['year']}). {r['title']}."
            st.code(cite)
            txt_out += cite + "\n"
        
        st.download_button("📥 Kaynakçayı Dışa Aktar (.txt)", txt_out, use_container_width=True)
        if st.button("🗑️ Tüm Kayıtları Temizle"):
            st.session_state.refs = []
            st.rerun()

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Veriden Yayına Stratejik Çözümler</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="service-card">
            <h3>🧬 Genetik Veri Analizi</h3>
            <p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve fenotip-genotip ilişkilendirmesi.</p>
            <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">NCBI</span>
        </div>
        <div class="service-card">
            <h3>🤖 Sağlıkta Makine Öğrenimi</h3>
            <p>Klinik ve omik veriler kullanılarak geliştirilen hastalık tahmin ve yapay zeka modelleri.</p>
            <span class="feature-tag">Python</span><span class="feature-tag">ML / AI</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="service-card">
            <h3>📊 Büyük Veri Analitiği</h3>
            <p>Büyük ölçekli akademik verilerin Python tabanlı ileri istatistiksel raporlanması.</p>
            <span class="feature-tag">Big Data</span><span class="feature-tag">Python</span>
        </div>
        <div class="service-card">
            <h3>🖋️ Referans Yazımı & Editoryal</h3>
            <p>Karmaşık yayınların referans yönetiminin Lifegenix uzmanlığıyla yüksek standartta düzenlenmesi.</p>
            <span class="feature-tag">Editorial Review</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 7. FOOTER
# ==========================================
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık tarafından kurulmuştur. <br> Akademik dürüstlük ve teknolojik üstünlük ilkesiyle.</div>', unsafe_allow_html=True)
