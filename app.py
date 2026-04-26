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
# 3. TASARIM
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
    st.session_state.page = st.radio("MENÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    st.markdown(f"""
        <div class="contact-container">
            <p style="color:#34d399; font-weight:bold;">📩 İletişim</p>
            <p style="color:#94a3b8; font-size:12px;">Analiz ve danışmanlık talepleriniz için:</p>
            <a href="mailto:{MY_EMAIL}" class="contact-btn">Mesaj Gönder</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. AKILLI FORMATLAMA MOTORU (SCHOLAR & PUBMED UYUMLU)
# ==========================================
def format_citation(data, style, index):
    title = data.get('title', 'Untitled')
    author = data.get('author', 'Anon')
    year = data.get('year', '2026')
    journal = data.get('journal', '')
    doi = data.get('doi', '')
    
    if style == "Vancouver":
        # PubMed/NLM Standardı: Author Surname Initials. Title. Journal. Year;Vol(Issue):Pages.
        return f"{index}. {author}. {title}. {journal}. {year}. doi:{doi}"
    elif style == "APA 7th":
        # Mendeley/Scholar Standardı: Author, A. A. (Year). Title. Journal. URL
        return f"{author} ({year}). {title}. {journal}. https://doi.org/{doi}"
    elif style == "IEEE":
        # EndNote Standardı: [n] Author, "Title," Journal, vol, no, pp, Year.
        return f"[{index}] {author}, \"{title},\" {journal}, {year}. DOI: {doi}"
    else: # MLA
        return f"{author}. \"{title}.\" {journal}, {year}, doi:{doi}."

def get_global_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        
        # Scholar/Mendeley uyumlu yazar formatı (Surname I.)
        authors = item.get('author', [])
        processed_authors = []
        for a in authors[:3]: # İlk 3 yazarı işle
            processed_authors.append(f"{a.get('family', '')} {a.get('given', '')[:1]}")
        
        main_author = ", ".join(processed_authors)
        if len(authors) > 3: main_author += " et al"
        if not authors: main_author = "Anonymous"
        
        return {
            "title": item.get('title', [''])[0],
            "author": main_author,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2026]])[0][0]),
            "journal": item.get('container-title', [''])[0],
            "doi": item.get('DOI', '')
        }
    except: return None

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================
if st.session_state.page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Global Veritabanlarıyla Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Seamless Citation Management with Global Databases"}</p>', unsafe_allow_html=True)

    st.markdown("""<div class="info-box"><b>Citemate Pro</b>; PubMed, Google Scholar ve Mendeley uyumlu uluslararası standartlarda (Vancouver, APA, IEEE) 
                referans oluşturur. Karmaşık akademik verileri saniyeler içinde hatasız kaynakçaya dönüştürür.</div>""", unsafe_allow_html=True)

    style = st.selectbox("Format:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI / PMID", "🔍 Akıllı Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI veya PubMed ID Girin:", placeholder="10.1101/...")
        if st.button("Listeye Ekle"):
            res = get_global_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Makale/Yayın Adı (Scholar Uyumlu):", placeholder="Örn: TCGA pan-cancer analysis...")
        if st.button("Global Ara ve Ekle"):
            res = get_global_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle (Metadata Çözümleme)", type="pdf")
        if f and st.button("PDF'den Veri Çek"):
            try:
                doc = fitz.open(stream=f.read(), filetype="pdf")
                text = "".join([doc[i].get_text() for i in range(min(len(doc), 3))])
                match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                if match:
                    res = get_global_data(match.group(), True)
                    if res: st.session_state.refs.append(res); st.rerun()
                else: st.warning("Dosyada DOI tespit edilemedi.")
            except: st.error("PDF işleme hatası.")
    
    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = format_citation(r, style, i)
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: st.download_button("📥 TXT Olarak İndir (EndNote/Mendeley Uyumlu)", txt_out, use_container_width=True)
        with c2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Biyoinformatik ve Büyük Veri Çözümleri</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="service-card">
            <h3>🧬 Genetik Veri Analizi</h3>
            <p>NCBI, GEO ve TCGA veritabanları üzerinden diferansiyel gen ekspresyonu ve sağkalım analizleri.</p>
            <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">NCBI</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card">
            <h3>🤖 Sağlıkta Makine Öğrenimi</h3>
            <p>Python tabanlı klinik veri modelleme, hastalık sınıflandırma ve tahmine dayalı biyoinformatik sistemler.</p>
            <span class="feature-tag">Python</span><span class="feature-tag">Deep Learning</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="service-card">
            <h3>📊 Büyük Veri Analitiği</h3>
            <p>Karmaşık akademik ve biyolojik veri setlerinin Python ile ileri istatistiksel raporlanması.</p>
            <span class="feature-tag">Big Data</span><span class="feature-tag">DataViz</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card">
            <h3>🖋️ Akademik Yazım & Editoryal</h3>
            <p>Uluslararası standartlarda referans yönetimi ve yayına hazırlık danışmanlığı.</p>
            <span class="feature-tag">Editorial</span><span class="feature-tag">Reference Management</span>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük ve Teknolojik Üstünlükle.</div>', unsafe_allow_html=True)
