import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# ==========================================
# 1. SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Citation Intelligence", page_icon="🎓", layout="wide")

# Google Analytics & SEO (Düzeltildi)
def add_seo():
    ga_id = "G-90YJBXFY8W" 
    meta_tags = """
        <meta name="description" content="Citemate Pro: Uluslararası standartlarda atıf motoru.">
        <meta name="keywords" content="vancouver, apa 7th, ieee, pubmed, mendeley, tcga, geo">
    """
    st.components.v1.html(f"{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>", height=0)

add_seo()

# ==========================================
# 2. OTURUM HAFIZASI (SESSION STATE)
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

# ==========================================
# 3. GLOBAL TASARIM (CSS)
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 58px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 5px; }}
    .sub-title {{ color: #f8fafc; font-size: 20px; margin-bottom: 30px; font-weight: 300; }}
    .service-card {{ 
        background: #161b22; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #34d399; 
        margin-bottom: 20px;
        min-height: 180px;
    }}
    .feature-tag {{ 
        background: #064e3b; color: #34d399; padding: 4px 10px; 
        border-radius: 5px; font-size: 10px; font-weight: bold; margin-right: 5px; 
    }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid #1e293b; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ (NAVİGASYON)
# ==========================================
with st.sidebar:
    st.markdown('<p style="font-size:26px; font-weight:bold; color:#34d399;">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.divider()
    
    # Dil Seçimi
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"; st.rerun()
    if c2.button("🇺🇸 EN"): st.session_state.lang = "English"; st.rerun()
    
    st.divider()
    
    # Menü Seçimi (Hatanın Çözümü Burada)
    page = st.radio("MENÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"])
    
    st.divider()
    st.markdown(f"""
        <div style="background:#1e293b; padding:15px; border-radius:10px; border:1px solid #334155;">
            <p style="color:#34d399; font-weight:bold; margin-bottom:5px;">📩 İletişim</p>
            <p style="color:#94a3b8; font-size:12px;">Analiz ve danışmanlık talepleriniz için:</p>
            <a href="mailto:{MY_EMAIL}" style="display:block; background:#34d399; color:black; text-align:center; padding:8px; border-radius:5px; font-weight:bold; text-decoration:none;">E-Posta Gönder</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. ATIF MOTORU MANTIĞI (GLOBAL STANDARTLAR)
# ==========================================
def format_citation(data, style, index):
    t, a, y, j, d = data['title'], data['author'], data['year'], data['journal'], data['doi']
    # NLM, APA 7, IEEE Standartları
    if style == "Vancouver": return f"{index}. {a}. {t}. {j}. {y}. doi:{d}"
    elif style == "APA 7th": return f"{a} ({y}). {t}. {j}. https://doi.org/{d}"
    elif style == "IEEE": return f"[{index}] {a}, \"{t},\" {j}, {y}. DOI: {d}"
    else: return f"{a}. \"{t}.\" {j}, {y}, doi:{d}."

def get_data(query, is_doi=False):
    try:
        url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        authors = item.get('author', [])
        # Mendeley/Scholar formatı (Surname I.)
        main_author = f"{authors[0].get('family', '')} {authors[0].get('given', '')[:1]}" if authors else "Anonymous"
        if len(authors) > 1: main_author += " et al"
        return {
            "title": item.get('title', [''])[0], "author": main_author,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2026]])[0][0]),
            "journal": item.get('container-title', [''])[0], "doi": item.get('DOI', '')
        }
    except: return None

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================

# SAYFA 1: ATIF MOTORU
if page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Global Veritabanlarıyla Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Seamless Citation Management"}</p>', unsafe_allow_html=True)

    style = st.selectbox("Atıf Formatı (Standard):", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI / PMID", "🔍 Akıllı Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Girin:", placeholder="10.1101/...")
        if st.button("Listeye Ekle"):
            res = get_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı (Scholar/PubMed):")
        if st.button("Ara ve Ekle"):
            res = get_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle", type="pdf")
        if f and st.button("DOI Çözümle"):
            with fitz.open(stream=f.read(), filetype="pdf") as doc:
                text = "".join([page.get_text() for page in doc[:3]])
                match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                if match:
                    res = get_data(match.group(), True)
                    if res: st.session_state.refs.append(res); st.rerun()
                else: st.warning("DOI bulunamadı.")

    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = format_citation(r, style, i)
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        c1, c2 = st.columns(2)
        with c1: st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        with c2: 
            if st.button("🗑️ Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

# SAYFA 2: PROFESYONEL HİZMETLER (DÜZELTİLDİ)
elif page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Biyoinformatik ve Büyük Veri Çözümleri</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
            <div class="service-card">
                <h3 style="color:#34d399; margin-top:0;">🧬 Genetik Veri Analizi</h3>
                <p style="color:#cbd5e1; font-size:14px;">NCBI, GEO ve TCGA veritabanları üzerinden Diferansiyel Gen Ekspresyonu, Pathway Zenginleştirme ve Sağkalım Analizleri.</p>
                <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">R/PYTHON</span>
            </div>
            <div class="service-card">
                <h3 style="color:#34d399; margin-top:0;">🤖 Sağlıkta Makine Öğrenimi</h3>
                <p style="color:#cbd5e1; font-size:14px;">Klinik ve omik verilerle hastalık tahmini, sınıflandırma ve Deep Learning modellerinin geliştirilmesi.</p>
                <span class="feature-tag">AI</span><span class="feature-tag">Scikit-Learn</span>
            </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
            <div class="service-card">
                <h3 style="color:#34d399; margin-top:0;">📊 Büyük Veri Analitiği</h3>
                <p style="color:#cbd5e1; font-size:14px;">Karmaşık akademik ve biyolojik veri setlerinin ileri istatistiksel yöntemlerle raporlanması ve görselleştirilmesi.</p>
                <span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span>
            </div>
            <div class="service-card">
                <h3 style="color:#34d399; margin-top:0;">🖋️ Akademik Yazım & Editoryal</h3>
                <p style="color:#cbd5e1; font-size:14px;">Uluslararası standartlarda referans yönetimi (Mendeley, EndNote uyumlu) ve yayına hazırlık danışmanlığı.</p>
                <span class="feature-tag">Editorial</span><span class="feature-tag">Publication</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("Hizmetlerimiz hakkında detaylı bilgi ve iş birliği için yan menüden bizimle iletişime geçebilirsiniz.")

# FOOTER
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Teknolojik Üstünlük</div>', unsafe_allow_html=True)
