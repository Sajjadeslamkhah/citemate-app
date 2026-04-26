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
        <meta name="description" content="Citemate Pro: Uluslararası standartlarda Vancouver, APA ve IEEE atıf düzenleme motoru.">
        <meta name="keywords" content="vancouver style, apa 7th, ieee citation, academic reference, lifegenix">
    """
    ga_code = f"{google_verification}{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"
    st.components.v1.html(ga_code, height=0)

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
    .service-card {{ background: #161b22; padding: 30px; border-radius: 18px; border-top: 5px solid #34d399; margin-bottom: 25px; }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 6px; }}
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
    st.markdown(f'<div class="contact-container"><p style="color:#34d399; font-weight:bold;">📩 İletişim</p><a href="mailto:{MY_EMAIL}" class="contact-btn">Mesaj Gönder</a></div>', unsafe_allow_html=True)

# ==========================================
# 5. ATIF FORMATLAMA (ULUSLARARASI STANDARTLAR)
# ==========================================
def format_citation(data, style, index):
    title = data.get('title', 'Untitled')
    author = data.get('author', 'Anon')
    year = data.get('year', 'n.d.')
    journal = data.get('journal', '')
    doi = data.get('doi', '')
    
    if style == "Vancouver":
        # Vancouver: Soyadı Baş Harf. Başlık. Dergi. Yıl;Cilt(Sayı):Sayfa.
        return f"{index}. {author}. {title}. {journal}. {year}. doi:{doi}"
    elif style == "APA 7th":
        # APA: Soyadı, A. (Yıl). Başlık. Dergi, Cilt(Sayı), Sayfa. URL
        return f"{author} ({year}). {title}. {journal}. https://doi.org/{doi}"
    elif style == "IEEE":
        # IEEE: [n] A. Soyadı, "Başlık," Dergi, cilt, sayı, sayfa, Yıl.
        return f"[{index}] {author}, \"{title},\" {journal}, {year}. DOI: {doi}"
    else: # MLA
        return f"{author}. \"{title}.\" {journal}, {year}, doi:{doi}."

def get_data(query, is_doi=False):
    # Gelişmiş DOI Regex
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
    
    try:
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        
        # Yazar İşleme
        authors = item.get('author', [])
        if authors:
            main_author = f"{authors[0].get('family', '')} {authors[0].get('given', '')[:1]}"
            if len(authors) > 1: main_author += " et al"
        else: main_author = "Anonymous"
        
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
    st.markdown(f'<p class="sub-title">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Engine"}</p>', unsafe_allow_html=True)

    st.markdown("""<div class="info-box"><b>Citemate Pro</b>, uluslararası standartlarda (Vancouver, APA, IEEE) kaynakça oluşturur. 
                DOI veya başlık girerek saniyeler içinde hatasız referans listesi hazırlayabilirsiniz.</div>""", unsafe_allow_html=True)

    style = st.selectbox("Atıf Formatı:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI", "🔍 Global Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI:", placeholder="10.1101/2024...")
        if st.button("Listeye Ekle"):
            res = get_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı:", placeholder="Title of the paper...")
        if st.button("Ara ve Ekle"):
            res = get_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF", type="pdf")
        if f and st.button("Analiz Et"):
            doc = fitz.open(stream=f.read(), filetype="pdf")
            text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
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
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        with c2: 
            if st.button("🗑️ Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Veriden Yayına Stratejik Çözümler</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="service-card"><h3>🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik ve omik verilerle yapay zeka modelleri.</p><span class="feature-tag">ML / AI</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="service-card"><h3>📊 Büyük Veri Analitiği</h3><p>Büyük ölçekli verilerin ileri istatistiksel raporlanması.</p><span class="feature-tag">Big Data</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🖋️ Referans Yazımı</h3><p>Karmaşık yayınların editoryal düzenlenmesi.</p><span class="feature-tag">Editorial Review</span></div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Teknolojik Üstünlük.</div>', unsafe_allow_html=True)
