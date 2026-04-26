import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Global Citation Hub", page_icon="🎓", layout="wide")

def add_seo():
    ga_id = "G-90YJBXFY8W" 
    meta_tags = """
        <meta name="description" content="Citemate Pro: PubMed, Google Scholar ve Mendeley uyumlu uluslararası atıf düzenleme motoru.">
        <meta name="keywords" content="vancouver style, apa 7th, pubmed citation, endnote, mendeley, tcga veri analizi, geo ncbi">
    """
    st.components.v1.html(f"{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>", height=0)

add_seo()

# ==========================================
# 2. HAFIZA BAŞLATMA
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'page' not in st.session_state: st.session_state.page = "🏠 Atıf Motoru"
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

# ==========================================
# 3. TASARIM (CSS)
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 62px !important; font-weight: 900 !important; color: #34d399; text-shadow: 0px 0px 25px rgba(52, 211, 153, 0.4); margin-bottom: 0px; }}
    .sub-title {{ color: #f8fafc; font-size: 22px; margin-bottom: 45px; font-weight: 300; }}
    .info-box {{ background-color: rgba(52, 211, 153, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin-bottom: 35px; }}
    .contact-container {{ background: #1e293b; padding: 18px; border-radius: 15px; margin-top: 25px; border: 1px solid #334155; }}
    .contact-btn {{ display: block; background: #34d399; color: black !important; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; text-decoration: none; margin-top: 10px; }}
    .service-card {{ background: #161b22; padding: 30px; border-radius: 18px; border-top: 5px solid #34d399; margin-bottom: 25px; transition: 0.3s; }}
    .service-card:hover {{ border-color: #10b981; transform: translateY(-5px); }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 6px; text-transform: uppercase; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 80px; padding: 25px; border-top: 1px solid #1e293b; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ
# ==========================================
with st.sidebar:
    st.markdown('<p style="font-size:28px; font-weight:bold; color:#34d399;">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"; st.rerun()
    if c2.button("🇺🇸 EN"): st.session_state.lang = "English"; st.rerun()
    st.divider()
    
    # Navigasyon seçimi hafızaya alınır
    st.session_state.page = st.radio("MENÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    
    st.markdown(f"""
        <div class="contact-container">
            <p style="color:#34d399; font-weight:bold;">{"📩 İletişim" if st.session_state.lang == "Türkçe" else "📩 Contact"}</p>
            <a href="mailto:{MY_EMAIL}" class="contact-btn">{"Mesaj Gönder" if st.session_state.lang == "Türkçe" else "Send Message"}</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. ATIF MOTORU FONKSİYONLARI
# ==========================================
def format_citation(data, style, index):
    t, a, y, j, d = data['title'], data['author'], data['year'], data['journal'], data['doi']
    if style == "Vancouver": return f"{index}. {a}. {t}. {j}. {y}. doi:{d}"
    elif style == "APA 7th": return f"{a} ({y}). {t}. {j}. https://doi.org/{d}"
    elif style == "IEEE": return f"[{index}] {a}, \"{t},\" {j}, {y}. DOI: {d}"
    else: return f"{a}. \"{t}.\" {j}, {y}, doi:{d}."

def get_global_data(query, is_doi=False):
    try:
        url = f"https://api.crossref.org/works/{query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        authors = item.get('author', [])
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
if st.session_state.page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Engine"}</p>', unsafe_allow_html=True)

    st.markdown("""<div class="info-box"><b>Citemate Pro</b>; PubMed, Google Scholar ve Mendeley uyumlu uluslararası standartlarda 
                kaynakça oluşturur. Karmaşık akademik verileri saniyeler içinde hatasız referanslara dönüştürür.</div>""", unsafe_allow_html=True)

    style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI", "🔍 Global Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI / PMID Girin:")
        if st.button("Listeye Ekle", key="add_doi"):
            res = get_global_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı:")
        if st.button("Ara ve Ekle", key="add_search"):
            res = get_global_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle", type="pdf")
        if f and st.button("Çözümle"):
            doc = fitz.open(stream=f.read(), filetype="pdf")
            text = "".join([doc[i].get_text() for i in range(min(len(doc), 3))])
            match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
            if match:
                res = get_global_data(match.group(), True)
                if res: st.session_state.refs.append(res); st.rerun()

    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = format_citation(r, style, i)
            st.code(cite, language="text")
            txt_out += cite + "\n"
        st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        if st.button("🗑️ Temizle"): st.session_state.refs = []; st.rerun()

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Veri ve Analiz Çözümleri</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="service-card"><h3>🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA büyük veri setlerinin işlenmesi ve yorumlanması.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik ve omik verilerle geliştirilen tahmin ve yapay zeka modelleri.</p><span class="feature-tag">Python</span><span class="feature-tag">AI</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="service-card"><h3>📊 Büyük Veri Analitiği</h3><p>Karmaşık akademik veri setlerinin ileri istatistiksel raporlanması.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🖋️ Akademik Yazım</h3><p>Uluslararası standartlarda referans ve editoryal düzenleme.</p><span class="feature-tag">Editorial</span></div>""", unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük ve Teknolojik Üstünlükle.</div>', unsafe_allow_html=True)
