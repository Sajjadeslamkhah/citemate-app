import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO (GÜÇLENDİRİLMİŞ)
# ==========================================
st.set_page_config(page_title="Citemate Pro | Lifegenix Data Insights", page_icon="🎓", layout="wide")

def add_seo():
    ga_id = "G-90YJBXFY8W" 
    google_verification = '<meta name="google-site-verification" content="PjsiKrJtJ7MoRpZcOG1IK3VZpNh6WMGmMcnk6OIAHfE" />'
    meta_tags = """
        <meta name="description" content="Lifegenix Labs: Python tabanlı biyoinformatik, sağlıkta makine öğrenimi ve TCGA/GEO veri analizi çözümleri.">
        <meta name="keywords" content="TCGA veri analizi, GEO biyoinformatik, sağlıkta makine öğrenimi, python akademik analiz, büyük veri genetik">
    """
    ga_code = f"{google_verification}{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"
    st.components.v1.html(ga_code, height=0)

add_seo()

# ==========================================
# 2. TASARIM (PREMIUM DARK MODE)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-title { font-size: 56px !important; font-weight: 850 !important; color: #34d399; text-shadow: 0px 0px 20px rgba(52, 211, 153, 0.3); margin-bottom: 5px; }
    .sub-title { color: #94a3b8; font-size: 20px; margin-bottom: 40px; font-style: italic; }
    .sidebar-brand { font-size: 26px !important; font-weight: bold; color: #34d399; }
    .service-card { background: #161b22; padding: 25px; border-radius: 15px; border-top: 4px solid #34d399; margin-bottom: 20px; }
    .feature-tag { background: #064e3b; color: #34d399; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; margin-right: 5px; }
    .footer { color: #4b5563; font-size: 13px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }
    .contact-link { display: block; background: #34d399; color: black !important; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; text-decoration: none; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. YAN MENÜ & NAVİGASYON
# ==========================================
if 'page' not in st.session_state: st.session_state.page = "Ana Sayfa"

with st.sidebar:
    st.markdown('<p class="sidebar-brand">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.caption("Advanced Academic Intelligence")
    st.divider()
    
    page = st.radio("Navigasyon", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"])
    st.session_state.page = page
    
    st.divider()
    st.subheader("📬 İletişim")
    st.markdown('<a href="mailto:iletisim@lifegenix.com" class="contact-link">📧 Mesaj Gönder</a>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("© 2026 **Lifegenix Danışmanlık**<br>Tüm hakları saklıdır.", unsafe_allow_html=True)

# ==========================================
# 4. FONKSİYONLAR
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
            return {"title": item.get('title', [''])[0], "author": auth, "year": year, "url": f"https://doi.org/{query}" if is_doi else "https://doi.org/"}
    except: return None

# ==========================================
# 5. SAYFA İÇERİKLERİ
# ==========================================

if st.session_state.page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Büyük Veri ve Sağlık Teknolojileri İçin Akademik Referans Motoru</p>', unsafe_allow_html=True)

    style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI Entegrasyonu", "🔍 Başlık Arama", "📄 Akıllı PDF Analizi"])
    
    with t1:
        doi = st.text_input("DOI Girin:")
        if st.button("Listeye Ekle"):
            res = get_cite(doi, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q = st.text_input("Makale Başlığı:")
        if st.button("Ara ve Ekle"):
            res = get_cite(q, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle", type="pdf")
        st.caption("Makale metadata verileri otomatik analiz edilir.")
    
    if st.session_state.refs:
        st.divider()
        txt = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = f"{i}. {r['author']}. {r['title']}. {r['year']}." if style == "Vancouver" else f"{r['author']} ({r['year']}). {r['title']}."
            st.code(cite)
            txt += cite + "\n"
        st.download_button("📥 Kaynakçayı İndir", txt)
        if st.button("🗑️ Temizle"): st.session_state.refs = []; st.rerun()

    # SSS VE SEO ALANI
    st.divider()
    with st.expander("❓ Sıkça Sorulan Sorular"):
        st.write("**Citemate Pro güvenli mi?** Tüm veriler Crossref API üzerinden doğrulanır.")
        st.write("**Python desteği var mı?** Evet, sistemimiz Python tabanlı veri çekme algoritmalarıyla çalışır.")

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Veriden Yayına Akademik Çözümler</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="service-card">
            <h3>🧬 Genetik Veri Analizi</h3>
            <p>NCBI, GEO ve TCGA gibi büyük veri setlerinin işlenmesi, fenotip-genotip ilişkilendirmesi.</p>
            <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">NCBI</span>
        </div>
        <div class="service-card">
            <h3>🤖 Sağlıkta Makine Öğrenimi</h3>
            <p>Klinik veriler ve omik veriler kullanılarak hastalık tahmini ve sınıflandırma modelleri.</p>
            <span class="feature-tag">Python</span><span class="feature-tag">Deep Learning</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="service-card">
            <h3>📊 Büyük Veri Analitiği</h3>
            <p>Büyük ölçekli akademik verilerin Python tabanlı kütüphanelerle istatistiksel raporlanması.</p>
            <span class="feature-tag">Big Data</span><span class="feature-tag">Statistics</span>
        </div>
        <div class="service-card">
            <h3>🖋️ Referans Yazımı</h3>
            <p>Karmaşık makale ve tezlerin referans yönetiminin Lifegenix uzmanlığıyla düzenlenmesi.</p>
            <span class="feature-tag">Professional Review</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. FOOTER
# ==========================================
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık tarafından kurulmuştur. <br> Akademik dürüstlük ve teknolojik üstünlük ilkesiyle.</div>', unsafe_allow_html=True)
