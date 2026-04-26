import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF
import urllib.parse

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Lifegenix", page_icon="🎓", layout="wide")

def add_analytics():
    ga_id = "G-90YJBXFY8W" 
    google_verification = '<meta name="google-site-verification" content="PjsiKrJtJ7MoRpZcOG1IK3VZpNh6WMGmMcnk6OIAHfE" />'
    meta_tags = """
        <meta name="description" content="Lifegenix Danışmanlık profesyonel atıf ve akademik danışmanlık platformu.">
        <meta name="keywords" content="vancouver atıf, apa 7, akademik danışmanlık, referans yazımı">
    """
    ga_code = f"{google_verification}{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>"
    st.components.v1.html(ga_code, height=0)

add_analytics()

# ==========================================
# 2. HAFIZA VE DİL SİSTEMİ
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"
if 'refs' not in st.session_state: st.session_state.refs = []

languages = {
    "Türkçe": {
        "welcome": "Akademik Atıf Motoru",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Başlık", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Kaynağı Ekle", "cite_style": "📌 Atıf Formatı Seçin:",
        "footer_rights": "© 2026 Lifegenix Danışmanlık. Tüm hakları saklıdır.",
        "contact_btn": "✉️ Bize Mesaj Gönder",
        "services_title": "💎 Profesyonel Hizmetler"
    },
    "English": {
        "welcome": "Academic Citation Engine",
        "tab_doi": "🔗 DOI/Link", "tab_search": "🔍 Title", "tab_pdf": "📄 PDF",
        "add_btn": "➕ Add Source", "cite_style": "📌 Select Citation Style:",
        "footer_rights": "© 2026 Lifegenix Consulting. All Rights Reserved.",
        "contact_btn": "✉️ Send Us a Message",
        "services_title": "💎 Professional Services"
    }
}
L = languages[st.session_state.lang]

# ==========================================
# 3. TASARIM
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; }
    .sidebar-brand { font-size: 24px; font-weight: bold; color: #34d399; text-align: center; }
    .contact-button { display: block; background-color: #1e293b; color: #34d399 !important; padding: 10px; border-radius: 8px; text-align: center; text-decoration: none; font-weight: bold; border: 1px solid #34d399; margin-top: 10px; }
    .service-card { background-color: #161b22; padding: 12px; border-radius: 8px; border-left: 3px solid #34d399; margin-bottom: 10px; font-size: 13px; }
    .footer-text { color: #4b5563; font-size: 12px; text-align: center; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sidebar-brand">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.divider()
    
    # PROFESYONEL HİZMETLER SEKMESİ
    st.subheader(L["services_title"])
    st.markdown("""
    <div class="service-card"><b>📊 Akademik Analiz</b><br>Bibliyometrik ve veri analiz hizmetleri.</div>
    <div class="service-card"><b>🖋️ Referans Yazımı</b><br>Tez ve makale referans düzenleme.</div>
    <div class="service-card"><b>🧬 Lifegenix Danışmanlık</b><br>Biyoinformatik ve yayın stratejisi.</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📬 İletişim")
    st.markdown(f'<a href="mailto:iletisim@lifegenix.com" class="contact-button">{L["contact_btn"]}</a>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("🌐 Dil / Language"):
        st.session_state.lang = "English" if st.session_state.lang == "Türkçe" else "Türkçe"
        st.rerun()

# ==========================================
# 4. FONKSİYONLAR (PDF DÜZELTİLDİ)
# ==========================================
def fetch_academic_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, query, re.I)
    doi = doi_match.group().strip("/") if doi_match else query
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://api.crossref.org/works/{doi}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10, headers=headers)
        if res.status_code == 200:
            data = res.json().get('message', {})
            item = data['items'][0] if 'items' in data else data
            title = item.get('title', [''])[0]
            authors = item.get('author', [])
            auth_str = authors[0].get('family') or "Anonim" if authors else "Anonim"
            if len(authors) > 1: auth_str += " et al."
            year = "2026"
            if 'published-print' in item: year = str(item['published-print']['date-parts'][0][0])
            elif 'issued' in item: year = str(item['issued']['date-parts'][0][0])
            return {"title": str(title), "author": str(auth_str), "year": str(year), "url": f"https://doi.org/{doi}"}
    except: pass
    return None

def process_pdf(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for i in range(min(len(doc), 3)): # İlk 3 sayfayı tara
            text += doc[i].get_text()
        
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        doi_match = re.search(doi_pattern, text, re.I)
        if doi_match:
            return fetch_academic_data(doi_match.group().strip("/"), is_doi=True)
        return None
    except Exception as e:
        return None

# ==========================================
# 5. ARAYÜZ
# ==========================================
st.title(f"🎓 {L['welcome']}")

style = st.selectbox(L["cite_style"], ["Vancouver", "APA 7th", "IEEE", "MLA"])

t_doi, t_search, t_pdf = st.tabs([L["tab_doi"], L["tab_search"], L["tab_pdf"]])

with t_doi:
    doi_in = st.text_input("DOI veya URL girin:", placeholder="Örn: 10.1111/j.1234...")
    if st.button(L["add_btn"], key="btn_doi"):
        if doi_in:
            res = fetch_academic_data(doi_in, is_doi=True)
            if res: st.session_state.refs.append(res); st.rerun()
            else: st.error("Veri bulunamadı. Lütfen DOI numarasını kontrol edin.")

with t_search:
    q_in = st.text_input(L["tab_search"], placeholder="Makale adını yazın...")
    if st.button(L["add_btn"], key="btn_q"):
        res = fetch_academic_data(q_in, is_doi=False)
        if res:
            st.session_state.refs.append(res)
            st.rerun()

with t_pdf:
    pf = st.file_uploader(L["tab_pdf"], type="pdf")
    if pf:
        if st.button("🚀 PDF Analiz Et"):
            with st.spinner("DOI aranıyor..."):
                res = process_pdf(pf.read())
                if res:
                    st.session_state.refs.append(res)
                    st.success("Kaynak başarıyla eklendi!")
                    st.rerun()
                else:
                    st.warning("PDF içinde DOI bulunamadı. Lütfen manuel ekleyin.")

# ÇIKTI ALANI
st.divider()
if st.session_state.refs:
    all_txt = ""
    for i, r in enumerate(st.session_state.refs, 1):
        if style == "Vancouver":
            cite = f"{i}. {r['author']}. {r['title']}. {r['year']}. {r['url']}"
        elif style == "APA 7th":
            cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
        else:
            cite = f"[{i}] {r['author']}, '{r['title']}', {r['year']}. {r['url']}"
        
        st.code(cite)
        all_txt += cite + "\n\n"
    
    st.download_button("📥 Listeyi İndir (.txt)", all_txt, use_container_width=True)
    if st.button("🗑️ Tümünü Temizle"):
        st.session_state.refs = []
        st.rerun()

# ==========================================
# 6. KURUMSAL FOOTER
# ==========================================
st.markdown(f"""
    <div class="footer-text">
        {L['footer_rights']}<br>
        <b>Lifegenix Danışmanlık</b> tarafından 2026 tarihinde akademik dürüstlük ilkesiyle kurulmuştur.
    </div>
""", unsafe_allow_html=True)
