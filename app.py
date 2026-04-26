import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF kütüphanesinin yüklü olduğundan emin olun: pip install pymupdf

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

# ==========================================
# 5. ATIF FORMATLAMA & VERİ ÇEKME
# ==========================================
def format_citation(data, style, index):
    title = data.get('title', 'Başlıksız')
    author = data.get('author', 'Anonim')
    year = data.get('year', 't.y.')
    journal = data.get('journal', 'Dergi Bilgisi Yok')
    doi = data.get('doi', '')
    
    if style == "Vancouver":
        return f"{index}. {author}. {title}. {journal}. {year}. doi:{doi}"
    elif style == "APA 7th":
        return f"{author} ({year}). {title}. {journal}. https://doi.org/{doi}"
    elif style == "IEEE":
        return f"[{index}] {author}, \"{title},\" {journal}, {year}. DOI: {doi}"
    else: # MLA
        return f"{author}. \"{title}.\" {journal}, {year}, doi:{doi}."

def get_data(query, is_doi=False):
    # DOI Regex geliştirildi
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        
        authors = item.get('author', [])
        if authors:
            main_author = f"{authors[0].get('family', '')} {authors[0].get('given', '')[:1]}"
            if len(authors) > 1: main_author += " et al"
        else: main_author = "Anonymous"
        
        return {
            "title": item.get('title', [''])[0],
            "author": main_author,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2024]])[0][0]),
            "journal": item.get('container-title', [''])[0],
            "doi": item.get('DOI', '')
        }
    except Exception as e:
        return None

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================
if st.session_state.page == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Engine"}</p>', unsafe_allow_html=True)

    style = st.selectbox("Atıf Formatı:", ["Vancouver", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI", "🔍 Global Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Girin:", placeholder="10.1101/...")
        if st.button("Listeye Ekle", key="doi_btn"):
            res = get_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()
            else: st.error("Bu DOI numarası ile veri bulunamadı.")

    with t2:
        q_in = st.text_input("Makale Adı Girin:", placeholder="Örn: AI in Healthcare")
        if st.button("Ara ve Ekle", key="search_btn"):
            res = get_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        uploaded_file = st.file_uploader("PDF Dosyanızı Yükleyin", type="pdf")
        if uploaded_file and st.button("Dosyayı Çözümle"):
            try:
                # PDF Okuma
                file_bytes = uploaded_file.read()
                with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                    found_doi = None
                    # İlk 3 sayfayı tara
                    for page_num in range(min(len(doc), 3)):
                        text = doc[page_num].get_text()
                        match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                        if match:
                            found_doi = match.group()
                            break
                    
                    if found_doi:
                        res = get_data(found_doi, True)
                        if res: 
                            st.session_state.refs.append(res)
                            st.success(f"DOI Bulundu: {found_doi}")
                            st.rerun()
                    else:
                        st.warning("Dosya metninde geçerli bir DOI numarası tespit edilemedi.")
            except Exception as e:
                st.error(f"PDF işlenirken bir hata oluştu: {str(e)}")
    
    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = format_citation(r, style, i)
            st.code(cite, language="text") # Sağ üstteki butondan kopyalanabilir
            txt_out += cite + "\n"
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        with c2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.write("Profesyonel Hizmetler Sayfası...")

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık</div>', unsafe_allow_html=True)
