import streamlit as st
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import urllib.parse

# ==========================================
# 1. SAYFA YAPILANDIRMASI & ANALYTICS
# ==========================================
st.set_page_config(page_title="Citemate Pro - Professional Citation Engine", page_icon="🎓", layout="wide")

def add_analytics():
    ga_id = "G-90YJBXFY8W" 
    google_verification = '<meta name="google-site-verification" content="PjsiKrJtJ7MoRpZcOG1IK3VZpNh6WMGmMcnk6OIAHfE" />'
    meta_tags = """
        <meta name="description" content="Professional citation generator for Vancouver, APA, and BibTeX.">
        <meta name="keywords" content="academic citation, vancouver generator, bibtex, apa 7th">
    """
    ga_code = f"{google_verification}{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"
    st.components.v1.html(ga_code, height=0)

add_analytics()

# ==========================================
# 2. HAFIZA VE DİL SİSTEMİ
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"
if 'refs' not in st.session_state: st.session_state.refs = []
if 'temp_search' not in st.session_state: st.session_state.temp_search = None

languages = {
    "Türkçe": {
        "welcome": "Akademik Atıf Motoru",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Başlık", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynağı İşle", "cite_style": "📌 Atıf Formatı:",
        "footer_msg": "Citemate Pro - Profesyonel Araştırmacı Portalı"
    },
    "English": {
        "welcome": "Academic Citation Engine",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Title", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Process Source", "cite_style": "📌 Citation Style:",
        "footer_msg": "Citemate Pro - Professional Researcher Portal"
    }
}
L = languages[st.session_state.lang]

# ==========================================
# 3. TASARIM (MODERN & PREMIUM)
# ==========================================
st.markdown("""
    <style>
    .stApp { background: #0e1117; }
    .stButton>button { width: 100%; border-radius: 20px; transition: 0.3s; }
    .stButton>button:hover { background-color: #34d399; color: black; border: none; }
    .sidebar-text { font-size: 14px; color: #94a3b8; }
    .metric-card { background: #1e293b; padding: 15px; border-radius: 10px; border-left: 4px solid #34d399; }
    </style>
    """, unsafe_allow_html=True)

# Yan Panel (Sidebar) - Profesyonel Bilgi Alanı
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=80)
    st.title("Citemate Pro")
    st.markdown(f"<p class='sidebar-text'>Giriş yapılan kaynak: <b>{len(st.session_state.refs)}</b></p>", unsafe_allow_html=True)
    st.divider()
    st.info("💡 İpucu: BibTeX formatı LaTeX kullanıcıları için otomatik olarak hazırlanır.")
    if st.button("🌐 Dil Değiştir / Change Language"):
        st.session_state.lang = "English" if st.session_state.lang == "Türkçe" else "Türkçe"
        st.rerun()

# ==========================================
# 4. FONKSİYONLAR
# ==========================================
def fetch_academic_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, query, re.I)
    doi = doi_match.group().strip("/") if doi_match else query
    try:
        url = f"https://api.crossref.org/works/{doi}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', [''])[0]
            authors = item.get('author', [])
            auth_str = authors[0].get('family') or "Anonim" if authors else "Anonim"
            if len(authors) > 1: auth_str += " et al."
            year = "2026" # Varsayılan
            if 'published-print' in item: year = str(item['published-print']['date-parts'][0][0])
            return {"title": str(title), "author": str(auth_str), "year": str(year), "url": f"https://doi.org/{doi}", "raw": item}
    except: pass
    return None

# ==========================================
# 5. ARAYÜZ
# ==========================================
st.title(f"🎓 {L['welcome']}")

col_main, col_stats = st.columns([8, 2])
with col_stats:
    st.markdown(f"<div class='metric-card'><b>Durum:</b><br>Sistem Aktif</div>", unsafe_allow_html=True)

style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "BibTeX (LaTeX)"])

t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])

with t_doi:
    doi_in = st.text_input("DOI / URL", placeholder="10.1111/j.1234...")
    if st.button(L["add_btn"], key="doi_btn"):
        res = fetch_academic_data(doi_in, is_doi=True)
        if res: 
            st.session_state.refs.append(res)
            st.toast("Kaynak başarıyla eklendi!", icon="✅")
            st.rerun()

# (Search ve PDF kısımları aynı mantıkla devam eder, toast eklenir)
# ... [Kısalık adına diğer giriş kısımları stabil kalmıştır] ...

# ÇIKTI ALANI
st.divider()
if st.session_state.refs:
    all_txt = ""
    for i, r in enumerate(st.session_state.refs, 1):
        if style == "BibTeX (LaTeX)":
            cite = f"@article{{ref{i},\n  author = {{{r['author']}}},\n  title = {{{r['title']}}},\n  year = {{{r['year']}}},\n  url = {{{r['url']}}}\n}}"
        elif style == "Vancouver":
            cite = f"{i}. {r['author']}. {r['title']}. {r['year']}. {r['url']}"
        else:
            cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
        
        st.code(cite, language="latex" if "BibTeX" in style else None)
        all_txt += cite + "\n\n"
    
    st.download_button("📥 Kaynakçayı İndir (.txt)", all_txt, use_container_width=True)
    if st.button("🗑️ Listeyi Temizle"):
        st.session_state.refs = []
        st.rerun()
else:
    st.info("Henüz bir kaynak eklemediniz. Başlamak için yukarıdaki sekmeleri kullanın.")

# SEO Alanı (Önceki mesajdaki gibi devam eder)
# ...
