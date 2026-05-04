import streamlit as st
import requests
import re
from datetime import datetime
from typing import Optional
import html
from urllib.parse import quote
import base64

try:
    import fitz
except ImportError:
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

# ==========================================
# 1. SAYFA YAPILANDIRMASI & LOGO
# ==========================================
st.set_page_config(page_title="Citemate Pro", page_icon="🎓", layout="wide")

# Logonuzun GitHub üzerindeki doğrudan linki
LOGO_URL = "https://raw.githubusercontent.com/sajjadeslamkhah/citemate-app/main/Logo.jpg"

# ==========================================
# LANGUAGE DICTIONARY - TÜRKÇE
# ==========================================

LANGUAGES = {
    "TR": {
        "app_title": "Citemate Pro",
        "app_tagline": "Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi",
        "sidebar_brand": "Citemate Pro",
        "menu_home": "🏠 Ana Sayfa",
        "menu_general": "📘 Genel Bilgiler",
        "menu_citation_engine": "🔗 Atif Motoru",
        "menu_why": "💡 Neden Citemate?",
        "menu_guide": "📖 Kullanım Kılavuzu",
        "menu_faq": "❓ SSS",
        "menu_about": "ℹ️ Hakkında",
        "format_label": "Format:",
        "tab_doi": "DOI",
        "tab_search": "Arama",
        "tab_pdf": "PDF",
        "doi_label": "DOI:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Ekle",
        "search_label": "Başlık:",
        "search_placeholder": "Yayın başlığı...",
        "search_button": "Ara",
        "pdf_label": "PDF Yükle",
        "pdf_button": "Yükle",
        "download_button": "İndir",
        "error_empty_input": "Lütfen bilgi girin",
        "error_invalid_doi": "Geçersiz DOI formatı",
        "error_no_results": "Sonuç bulunamadı",
        "error_timeout": "Timeout (10s)",
        "error_connection": "Bağlantı hatası",
        "error_pdf": "PDF hatası",
        "error_pymupdf": "PyMuPDF gerekli: pip install pymupdf",
        "success_added": "Eklendi!",
        "warning_duplicate": "Bu kaynak zaten var!",
        "searching": "Aranıyor...",
        "reading": "Okunuyor...",
        "delete": "Sil",
        "no_sources": "Kaynak yok",
        "contact_email": "📧 mbgsajjad@gmail.com",
        "contact_button": "Bize Ulaşın",
        "copyright": "© 2026 Tüm hakları saklıdır",
    }
}

# ==========================================
# SESSION STATE
# ==========================================

if 'refs' not in st.session_state:
    st.session_state.refs = []
if 'page' not in st.session_state:
    st.session_state.page = "citation_engine"

def get_text(key: str) -> str:
    return LANGUAGES["TR"].get(key, key)

# ==========================================
# STYLING
# ==========================================

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-title { font-size: 48px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 10px; }
    .subtitle { color: #94a3b8; font-size: 16px; margin-bottom: 30px; font-weight: 300; }
    .section-title { font-size: 32px !important; color: #34d399; margin: 30px 0 20px 0; font-weight: 800; }
    .ref-box { background-color: #161b22; padding: 15px; border-radius: 8px; border-left: 3px solid #34d399; margin: 10px 0; }
    .ref-title { font-weight: bold; color: #e2e8f0; }
    .error-box { background-color: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 5px; margin: 10px 0; }
    .success-box { background-color: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; color: #86efac; padding: 10px; border-radius: 5px; margin: 10px 0; }
    .info-box { background-color: rgba(52, 211, 153, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin: 20px 0; }
    .feature-box { background-color: #161b22; padding: 20px; border-radius: 10px; border-top: 3px solid #34d399; margin: 15px 0; }
    .why-item { background-color: #0f172a; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #34d399; }
    .guide-step { background-color: #161b22; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 5px solid #34d399; }
    .footer { color: #64748b; font-size: 12px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def is_valid_doi(doi_str: str) -> bool:
    if not isinstance(doi_str, str): return False
    return bool(re.match(r'^10\.\d{4,}/[^\s]+$', doi_str.strip()))

def extract_doi_from_text(text: str) -> Optional[str]:
    if not isinstance(text, str): return None
    match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
    return match.group().strip("/") if match else None

def sanitize(s: str, max_len: int = 300) -> str:
    if not isinstance(s, str): return ""
    return html.escape(s.strip())[:max_len]

def get_author(item: dict) -> str:
    try:
        authors = item.get('author', [])
        if not authors: return "Yazar Bilinmiyor"
        author = authors[0].get('family') or authors[0].get('literal', 'Yazar Bilinmiyor')
        if len(authors) > 1: return f"{author} vd."
        return sanitize(str(author))
    except: return "Yazar Bilinmiyor"

def get_year(item: dict) -> str:
    try:
        for key in ['published-online', 'published-print', 'created', 'issued']:
            if key in item and isinstance(item[key], dict):
                parts = item[key].get('date-parts')
                if parts and len(parts) > 0 and len(parts[0]) > 0:
                    year = parts[0][0]
                    if isinstance(year, int) and 1900 < year < 2100: return str(year)
    except: pass
    return str(datetime.now().year)

def is_duplicate(new_ref: dict) -> bool:
    for existing in st.session_state.refs:
        if new_ref.get('url', '').lower() == existing.get('url', '').lower(): return True
    return False

def format_citation(ref: dict, style: str, index: int) -> str:
    author = sanitize(str(ref.get('author', 'Yazar Bilinmiyor')))
    title = sanitize(str(ref.get('title', 'Başlık Yok')))
    year = ref.get('year', '2026')
    url = sanitize(str(ref.get('url', '')))
    if style == "Vancouver": return f"{index}. {author}. {title}. {year}. {url}"
    elif style == "APA 7. Baskı": return f"{author} ({year}). {title}. {url}"
    elif style == "IEEE": return f"[{index}] {author}, \"{title},\" {year}. {url}"
    return f"{author} ({year}). {title}."

def get_cite(query: str, is_doi: bool = False) -> Optional[dict]:
    try:
        url = f"https://api.crossref.org/works/{quote(query, safe='')}" if is_doi else f"https://api.crossref.org/works?query={quote(query, safe='')}&rows=1"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        msg = data['message']
        item = msg if is_doi else (msg['items'][0] if msg.get('items') else None)
        if not item: return None
        return {
            "title": sanitize(str(item.get('title', ['Başlık Yok'])[0]), 200),
            "author": get_author(item),
            "year": get_year(item),
            "url": f"https://doi.org/{item['DOI']}" if 'DOI' in item else item.get('URL', ''),
            "source": "Crossref"
        }
    except: return None

def process_pdf(file_bytes: bytes, filename: str) -> Optional[dict]:
    if fitz is None: return None
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([page.get_text() for page in doc[:3]])
        doi = extract_doi_from_text(text)
        if doi and is_valid_doi(doi): return get_cite(doi, is_doi=True)
        return {"title": sanitize(filename.replace('.pdf', ''), 200), "author": "PDF", "year": str(datetime.now().year), "url": filename, "source": "PDF"}
    except: return None

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.divider()
    if st.button(get_text("menu_home"), use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button(get_text("menu_general"), use_container_width=True): st.session_state.page = "general"; st.rerun()
    if st.button(get_text("menu_citation_engine"), use_container_width=True): st.session_state.page = "citation_engine"; st.rerun()
    if st.button(get_text("menu_why"), use_container_width=True): st.session_state.page = "why"; st.rerun()
    if st.button(get_text("menu_guide"), use_container_width=True): st.session_state.page = "guide"; st.rerun()
    if st.button(get_text("menu_faq"), use_container_width=True): st.session_state.page = "faq"; st.rerun()
    if st.button(get_text("menu_about"), use_container_width=True): st.session_state.page = "about"; st.rerun()
    if st.button("💎 Profesyonel Hizmetler", use_container_width=True): st.session_state.page = "services"; st.rerun()
    st.divider()
    st.markdown(f'<div class="info-box"><p style="color:#34d399;font-weight:bold;">{get_text("contact_email")}</p></div>', unsafe_allow_html=True)

# ==========================================
# PAGES
# ==========================================

if st.session_state.page == "home":
    st.markdown('<p class="main-title">Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{get_text("app_tagline")}</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-box"><p><strong>Citemate Pro</strong>, araştırmacıların ve öğrencilerin kaynakça hazırlama yükünü hafifletmek için tasarlanmış, yapay zeka destekli bir atıf düzenleme motorudur.</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<h3 style="color:#34d399;">🎯 Neden Citemate Pro?</h3>', unsafe_allow_html=True)
        st.markdown('<div class="why-item"><strong>⚡ Hız:</strong> DOI ile saniyeler içinde atıf oluşturun</div>', unsafe_allow_html=True)
        st.markdown('<div class="why-item"><strong>✅ Doğruluk:</strong> Global Crossref veritabanı ile senkronize</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<h3 style="color:#34d399;">📊 Özellikler</h3>', unsafe_allow_html=True)
        st.markdown('<div class="why-item"><strong>📄 PDF Analizi:</strong> PDF dosyasından veri çıkarma</div>', unsafe_allow_html=True)
        st.markdown('<div class="why-item"><strong>📋 4 Format:</strong> Vancouver, APA, IEEE, MLA</div>', unsafe_allow_html=True)

elif st.session_state.page == "general":
    st.markdown('<p class="main-title">📘 Genel Bilgiler</p>', unsafe_allow_html=True)
    st.markdown('<div class="feature-box"><strong>📋 Dört Atıf Formatı</strong><ul><li>Vancouver (NLM)</li><li>APA 7. Baskı</li><li>IEEE</li><li>MLA</li></ul></div>', unsafe_allow_html=True)

elif st.session_state.page == "citation_engine":
    st.markdown('<p class="main-title">🔗 Atıf Motoru</p>', unsafe_allow_html=True)
    style = st.selectbox(get_text("format_label"), ["Vancouver", "APA 7. Baskı", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["DOI", "Arama", "PDF"])
    with t1:
        doi_in = st.text_input("DOI:", key="doi_input")
        if st.button("Ekle"):
            res = get_cite(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()
    with t2:
        q_in = st.text_input("Başlık:", key="q_input")
        if st.button("Ara"):
            res = get_cite(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()
    with t3:
        pdf_file = st.file_uploader("PDF", type="pdf")
        if pdf_file and st.button("Yükle"):
            res = process_pdf(pdf_file.read(), pdf_file.name)
            if res: st.session_state.refs.append(res); st.rerun()
    
    if st.session_state.refs:
        st.divider()
        bib_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            cite = format_citation(r, style, i)
            st.code(cite)
            bib_out += cite + "\n"
        st.download_button("İndir", bib_out)
        if st.button("🗑️ Temizle"): st.session_state.refs = []; st.rerun()

elif st.session_state.page == "why":
    st.markdown('<p class="main-title">💡 Neden Citemate Pro?</p>', unsafe_allow_html=True)
    st.markdown('<div class="why-item"><strong>⚡ Hız:</strong> Ek yazılım kurmadan anında çözüm.</div>', unsafe_allow_html=True)
    st.markdown('<div class="why-item"><strong>✅ Doğruluk:</strong> Crossref metadata çekirdeği kullanılır.</div>', unsafe_allow_html=True)

elif st.session_state.page == "guide":
    st.markdown('<p class="main-title">📖 Kullanım Kılavuzu</p>', unsafe_allow_html=True)
    st.markdown('<div class="guide-step">1. DOI girin veya PDF yükleyin. 2. Format seçin. 3. Kaynakçayı indirin.</div>', unsafe_allow_html=True)

elif st.session_state.page == "faq":
    st.markdown('<p class="main-title">❓ SSS</p>', unsafe_allow_html=True)
    with st.expander("Scholar uyumlu mu?"): st.write("Evet, tam uyumludur.")

elif st.session_state.page == "about":
    st.markdown('<p class="main-title">ℹ️ Hakkında</p>', unsafe_allow_html=True)
    st.write("Citemate Pro, akademik dürüstlük ve teknolojik üstünlüğü birleştirir.")

elif st.session_state.page == "services":
    st.markdown('<p class="main-title">💎 Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="feature-box"><h4>🧬 Genetik Veri Analizi</h4><p>NCBI, GEO, TCGA veri setleri analizi.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><h4>🤖 Sağlıkta Makine Öğrenmesi</h4><p>Hastalık tahmin modelleri.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-box"><h4>📊 Büyük Veri Analitikleri</h4><p>İleri istatistiksel raporlama.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><h4>🖋️ Referans & Editorial</h4><p>Yayın hazırlık danışmanlığı.</p></div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer">{get_text("copyright")} | Lifegenix Consulting Ltd.</div>', unsafe_allow_html=True)
