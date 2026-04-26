import streamlit as st
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import urllib.parse

# ==========================================
# 1. SAYFA YAPILANDIRMASI & ANALYTICS (SEO)
# ==========================================
st.set_page_config(page_title="Citemate Pro | Lifegenix Labs", page_icon="🎓", layout="wide")

def add_analytics():
    ga_id = "G-90YJBXFY8W" 
    google_verification = '<meta name="google-site-verification" content="PjsiKrJtJ7MoRpZcOG1IK3VZpNh6WMGmMcnk6OIAHfE" />'
    meta_tags = """
        <meta name="description" content="Lifegenix Danışmanlık tarafından geliştirilen profesyonel akademik atıf motoru. Vancouver, APA ve BibTeX desteği.">
        <meta name="author" content="Lifegenix Danışmanlık">
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
        "footer_rights": "© 2026 Lifegenix Danışmanlık. Tüm hakları saklıdır.",
        "contact_btn": "✉️ Bize Mesaj Gönder"
    },
    "English": {
        "welcome": "Academic Citation Engine",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Title", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Process Source", "cite_style": "📌 Citation Style:",
        "footer_rights": "© 2026 Lifegenix Consulting. All Rights Reserved.",
        "contact_btn": "✉️ Send Us a Message"
    }
}
L = languages[st.session_state.lang]

# ==========================================
# 3. TASARIM (MODERN & KURUMSAL)
# ==========================================
st.markdown("""
    <style>
    .stApp { background: #0e1117; }
    .announcement-bar { background: linear-gradient(90deg, #34d399, #10b981); color: black; padding: 8px; text-align: center; font-size: 14px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 20px; transition: 0.3s; }
    .stButton>button:hover { background-color: #34d399; color: black; border: none; }
    .sidebar-brand { font-size: 22px; font-weight: bold; color: #34d399; }
    .sidebar-text { font-size: 14px; color: #94a3b8; }
    .metric-card { background: #1e293b; padding: 15px; border-radius: 10px; border-left: 4px solid #34d399; }
    .contact-button { display: block; background-color: #1e293b; color: #34d399 !important; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: bold; border: 1px solid #34d399; transition: 0.3s; }
    .contact-button:hover { background-color: #34d399; color: black !important; }
    .footer-text { color: #4b5563; font-size: 13px; text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# Duyuru Bandı
st.markdown('<div class="announcement-bar">🚀 Lifegenix Danışmanlık Güvencesiyle Akademik Çözümler</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sidebar-brand">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f"<p class='sidebar-text'>Kayıtlı Kaynak: <b>{len(st.session_state.refs)}</b></p>", unsafe_allow_html=True)
    st.divider()
    
    # İletişim Alanı
    st.subheader("📬 İletişim")
    # Lütfen mail adresini buraya yaz
    st.markdown(f'<a href="mailto:iletisim@lifegenix.com" class="contact-button">{L["contact_btn"]}</a>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("🌐 Dil / Language"):
        st.session_state.lang = "English" if st.session_state.lang == "Türkçe" else "Türkçe"
        st.rerun()
    st.info("💡 BibTeX formatı LaTeX kullanıcıları için otomatik olarak hazırlanır.")

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
            year = str(datetime.now().year)
            if 'published-print' in item: year = str(item['published-print']['date-parts'][0][0])
            return {"title": str(title), "author": str(auth_str), "year": str(year), "url": f"https://doi.org/{doi}"}
    except: pass
    return None

def process_pdf(file_bytes, filename):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([doc[i].get_text() for i in range(min(len(doc), 2))])
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        doi_match = re.search(doi_pattern, text, re.I)
        if doi_match: return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        return {"title": lines[0] if lines else filename, "author": "PDF", "year": str(datetime.now().year), "url": filename}
    except: return None

# ==========================================
# 5. ARAYÜZ (GİRİŞ-ÇIKTI)
# ==========================================
st.title(f"🎓 {L['welcome']}")

col_main, col_stats = st.columns([8, 2])
with col_stats:
    st.markdown(f"<div class='metric-card'><b>Sistem Durumu:</b><br>✅ Aktif</div>", unsafe_allow_html=True)

style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "BibTeX (LaTeX)"])

t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])

with t_doi:
    doi_in = st.text_input("DOI / URL", placeholder="10.1111/j.1234...")
    if st.button(L["add_btn"], key="doi_btn"):
        res = fetch_academic_data(doi_in, is_doi=True)
        if res: 
            st.session_state.refs.append(res)
            st.toast("Kaynak eklendi!", icon="✅")
            st.rerun()

with t_search:
    q_in = st.text_input(L["tab_search"], placeholder="Makale başlığını girin...")
    if st.button(L["add_btn"], key="q_btn"):
        res = fetch_academic_data(q_in, is_doi=False)
        if res:
            st.session_state.temp_search = res
    if st.session_state.temp_search:
        st.info(f"Bulundu: {st.session_state.temp_search['title']}")
        if st.button("✅ Onayla ve Ekle"):
            st.session_state.refs.append(st.session_state.temp_search)
            st.session_state.temp_search = None
            st.rerun()

with t_pdf:
    pf = st.file_uploader(L["tab_pdf"], type="pdf")
    if pf and st.button(L["add_btn"], key="pdf_btn"):
        res = process_pdf(pf.read(), pf.name)
        if res:
            st.session_state.refs.append(res)
            st.toast("PDF Analiz Edildi!", icon="📄")
            st.rerun()

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
    if st.button("🗑️ Tümünü Temizle"):
        st.session_state.refs = []
        st.rerun()
else:
    st.info("Analiz edilecek kaynak eklenmedi.")

# ==========================================
# 6. KURUMSAL FOOTER & TELİF (LIFERGENIX)
# ==========================================
st.markdown(f"""
    <div class="footer-text">
        {L['footer_rights']}<br>
        <b>Lifegenix Danışmanlık</b> tarafından 2026 tarihinde kurulmuştur.<br>
        Akademik verimlilik ve hassasiyet için tasarlanmıştır.
    </div>
""", unsafe_allow_html=True)
