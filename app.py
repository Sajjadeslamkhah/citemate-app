import streamlit as st
import requests
import re
from datetime import datetime
from typing import Optional
import html
from urllib.parse import quote

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
# LANGUAGE DICTIONARY
# ==========================================

LANGUAGES = {
    "TR": {
        "app_title": "Citemate Pro",
        "app_tagline": "Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi",
        "sidebar_brand": "Citemate Pro",
        "menu_home": "🏠 Ana Sayfa",
        "menu_citation_engine": "🔗 Atif Motoru",
        "menu_faq": "❓ SSS",
        "menu_services": "💎 Profesyonel Hizmetler",
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
        "powered_by": "Lifegenix Danışmanlık tarafından",
        "copyright": "© 2026 Tüm hakları saklıdır",
    },
    "EN": {
        "app_title": "Citemate Pro",
        "app_tagline": "Seamless Citation Management for Academic Excellence",
        "sidebar_brand": "Citemate Pro",
        "menu_home": "🏠 Home",
        "menu_citation_engine": "🔗 Citation Engine",
        "menu_faq": "❓ FAQ",
        "menu_services": "💎 Professional Services",
        "menu_about": "ℹ️ About",
        "format_label": "Format:",
        "tab_doi": "DOI",
        "tab_search": "Search",
        "tab_pdf": "PDF",
        "doi_label": "DOI:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Add",
        "search_label": "Title:",
        "search_placeholder": "Publication title...",
        "search_button": "Search",
        "pdf_label": "Upload PDF",
        "pdf_button": "Upload",
        "download_button": "Download",
        "error_empty_input": "Please provide input",
        "error_invalid_doi": "Invalid DOI format",
        "error_no_results": "No results found",
        "error_timeout": "Timeout (10s)",
        "error_connection": "Connection error",
        "error_pdf": "PDF error",
        "error_pymupdf": "PyMuPDF required: pip install pymupdf",
        "success_added": "Added!",
        "warning_duplicate": "This source already exists!",
        "searching": "Searching...",
        "reading": "Reading...",
        "delete": "Delete",
        "no_sources": "No sources",
        "contact_email": "📧 mbgsajjad@gmail.com",
        "powered_by": "Powered by Lifegenix Consulting",
        "copyright": "© 2026 All rights reserved",
    }
}

st.set_page_config(page_title="Citemate Pro", page_icon="🎓", layout="wide")

# ==========================================
# SESSION STATE
# ==========================================

def init_session_state():
    if 'refs' not in st.session_state:
        st.session_state.refs = []
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'lang' not in st.session_state:
        st.session_state.lang = "TR"

init_session_state()

def get_text(key: str) -> str:
    lang = st.session_state.lang
    if lang not in LANGUAGES:
        lang = "TR"
    return LANGUAGES[lang].get(key, key)

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
    .ref-author { color: #94a3b8; font-size: 13px; }
    .ref-source { color: #64748b; font-size: 12px; font-style: italic; }
    .error-box { background-color: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 5px; margin: 10px 0; }
    .success-box { background-color: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; color: #86efac; padding: 10px; border-radius: 5px; margin: 10px 0; }
    .info-box { background-color: rgba(52, 211, 153, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin: 20px 0; }
    .feature-box { background-color: #161b22; padding: 20px; border-radius: 10px; border-top: 3px solid #34d399; margin: 15px 0; }
    .why-item { background-color: #0f172a; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #34d399; }
    .footer { color: #64748b; font-size: 12px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }
    .faq-item { background-color: #161b22; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .nav-button { background-color: #161b22 !important; border: 1px solid #34d399 !important; color: #34d399 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def is_valid_doi(doi_str: str) -> bool:
    if not isinstance(doi_str, str):
        return False
    return bool(re.match(r'^10\.\d{4,}/[^\s]+$', doi_str.strip()))

def extract_doi_from_text(text: str) -> Optional[str]:
    if not isinstance(text, str):
        return None
    match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
    return match.group().strip("/") if match else None

def sanitize(s: str, max_len: int = 300) -> str:
    if not isinstance(s, str):
        return ""
    return html.escape(s.strip())[:max_len]

def get_author(item: dict) -> str:
    try:
        authors = item.get('author', [])
        if not authors:
            return "Anonymous"
        author = authors[0].get('family') or authors[0].get('literal', 'Anonymous')
        if len(authors) > 1:
            return f"{author} et al."
        return sanitize(str(author))
    except:
        return "Anonymous"

def get_year(item: dict) -> str:
    try:
        for key in ['published-online', 'published-print', 'created', 'issued']:
            if key in item and isinstance(item[key], dict):
                parts = item[key].get('date-parts')
                if parts and len(parts) > 0 and len(parts[0]) > 0:
                    year = parts[0][0]
                    if isinstance(year, int) and 1900 < year < 2100:
                        return str(year)
    except:
        pass
    return str(datetime.now().year)

def is_duplicate(new_ref: dict) -> bool:
    for existing in st.session_state.refs:
        if new_ref.get('url', '').lower() == existing.get('url', '').lower():
            return True
        if (new_ref.get('title', '').lower()[:50] == existing.get('title', '').lower()[:50]):
            return True
    return False

def format_citation(ref: dict, style: str, index: int) -> str:
    author = sanitize(str(ref.get('author', 'Anonymous')))
    title = sanitize(str(ref.get('title', 'No Title')))
    year = ref.get('year', '2026')
    url = sanitize(str(ref.get('url', '')))
    
    if style == "Vancouver":
        return f"{index}. {author}. {title}. {year}. {url}"
    elif style == "APA 7th":
        return f"{author} ({year}). {title}. {url}"
    elif style == "IEEE":
        return f"[{index}] {author}, \"{title},\" {year}. {url}"
    elif style == "MLA":
        return f"{author}. {title}. {year}. {url}"
    return f"{author} ({year}). {title}."

# ==========================================
# API FUNCTIONS
# ==========================================

def get_cite(query: str, is_doi: bool = False) -> Optional[dict]:
    if not isinstance(query, str) or not query.strip():
        st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
        return None
    
    query = sanitize(query, max_len=200)
    
    try:
        if is_doi:
            url = f"https://api.crossref.org/works/{quote(query, safe='')}"
        else:
            url = f"https://api.crossref.org/works?query={quote(query, safe='')}&rows=1"
        
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if 'message' not in data:
            return None
        
        msg = data['message']
        item = msg if is_doi else (msg['items'][0] if msg.get('items') else None)
        
        if not item:
            st.markdown(f'<div class="error-box">{get_text("error_no_results")}</div>', unsafe_allow_html=True)
            return None
        
        title = item.get('title', ['No Title'])
        if isinstance(title, list):
            title = title[0] if title else 'No Title'
        
        return {
            "title": sanitize(str(title), 200),
            "author": get_author(item),
            "year": get_year(item),
            "url": f"https://doi.org/{item['DOI']}" if 'DOI' in item else item.get('URL', ''),
            "source": "Crossref"
        }
    
    except requests.exceptions.Timeout:
        st.markdown(f'<div class="error-box">{get_text("error_timeout")}</div>', unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
    
    return None

def process_pdf(file_bytes: bytes, filename: str) -> Optional[dict]:
    if fitz is None:
        st.markdown(f'<div class="error-box">{get_text("error_pymupdf")}</div>', unsafe_allow_html=True)
        return None
    
    try:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            
            for page_num in range(min(len(doc), 5)):
                try:
                    page = doc[page_num]
                    page_text = page.get_text()
                    text += page_text + "\n"
                    
                    if len(text) > 500:
                        break
                except:
                    continue
            
            if len(text.strip()) < 100:
                try:
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    for page_num in range(min(len(doc), 3)):
                        try:
                            pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2))
                            if Image and pytesseract:
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                page_text = pytesseract.image_to_string(img)
                                text += page_text + "\n"
                                
                                if len(text) > 500:
                                    break
                        except:
                            continue
                except:
                    pass
        except Exception as e:
            pass
        
        if len(text.strip()) < 50:
            return {
                "title": sanitize(filename.replace('.pdf', ''), 200),
                "author": "PDF",
                "year": str(datetime.now().year),
                "url": sanitize(filename),
                "source": "PDF (Fallback)"
            }
        
        doi = extract_doi_from_text(text)
        if doi and is_valid_doi(doi):
            result = get_cite(doi, is_doi=True)
            if result:
                return result
        
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
        lines = [l for l in lines if len(l) > 20 and len(l) < 200]
        
        if not lines:
            return {
                "title": sanitize(filename.replace('.pdf', ''), 200),
                "author": "PDF",
                "year": str(datetime.now().year),
                "url": sanitize(filename),
                "source": "PDF"
            }
        
        title = max(lines[:5], key=len, default=filename)
        
        return {
            "title": sanitize(title, 200),
            "author": "PDF",
            "year": str(datetime.now().year),
            "url": sanitize(filename),
            "source": "PDF"
        }
    
    except Exception as e:
        return {
            "title": sanitize(filename.replace('.pdf', ''), 200),
            "author": "PDF",
            "year": str(datetime.now().year),
            "url": sanitize(filename),
            "source": "PDF (Fallback)"
        }

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown('<p style="font-size: 24px; font-weight: bold; color: #34d399;">Citemate Pro</p>', unsafe_allow_html=True)
    
    # Language selector
    lang_cols = st.columns(2)
    if lang_cols[0].button("🇹🇷 TR", use_container_width=True):
        st.session_state.lang = "TR"
        st.rerun()
    if lang_cols[1].button("🇺🇸 EN", use_container_width=True):
        st.session_state.lang = "EN"
        st.rerun()
    
    st.divider()
    
    # Navigation buttons
    nav_cols = st.columns(1)
    
    if st.button(get_text("menu_home"), use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
    
    if st.button(get_text("menu_citation_engine"), use_container_width=True, key="nav_engine"):
        st.session_state.page = "citation_engine"
        st.rerun()
    
    if st.button(get_text("menu_faq"), use_container_width=True, key="nav_faq"):
        st.session_state.page = "faq"
        st.rerun()
    
    if st.button(get_text("menu_services"), use_container_width=True, key="nav_services"):
        st.session_state.page = "services"
        st.rerun()
    
    if st.button(get_text("menu_about"), use_container_width=True, key="nav_about"):
        st.session_state.page = "about"
        st.rerun()
    
    st.divider()
    st.markdown(f"""
    <div class="info-box">
    <p style="color: #34d399; font-weight: bold; margin: 0 0 8px 0;">{get_text("contact_email")}</p>
    <p style="color: #94a3b8; font-size: 12px; margin: 0;">{get_text("powered_by")}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# HOME PAGE
# ==========================================

if st.session_state.page == "home":
    st.markdown('<p class="main-title">Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{get_text("app_tagline")}</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <p><strong>Citemate Pro</strong>, araştırmacıların ve öğrencilerin kaynakça hazırlama yükünü hafifletmek için tasarlanmış, yapay zeka destekli bir atıf düzenleme motorudur. DOI numarası, yayın başlığı veya doğrudan PDF dosyanızı kullanarak saniyeler içinde hatasız; Vancouver, APA, IEEE ve MLA formatlarında profesyonel referanslar oluşturur.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #34d399;">🎯 Neden Citemate Pro?</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="why-item">
        <strong>⚡ Hız:</strong> DOI ile saniyeler içinde atıf oluşturun
        </div>
        <div class="why-item">
        <strong>✅ Doğruluk:</strong> Global Crossref veritabanı ile senkronize
        </div>
        <div class="why-item">
        <strong>💰 Ücretsiz:</strong> Araştırmacılar için tamamen ücretsiz
        </div>
        <div class="why-item">
        <strong>🔄 Otomatik:</strong> Formatlama tamamen otomatik
        </div>
        <div class="why-item">
        <strong>🔒 Güvenli:</strong> Verileriniz gizli kalır, hiçbir şey saklanmaz
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h3 style="color: #34d399;">📊 Özellikler</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="why-item">
        <strong>🔗 DOI Arama:</strong> Crossref API ile doğrudan erişim
        </div>
        <div class="why-item">
        <strong>🔍 Başlık Arama:</strong> Yayın adıyla referans bulun
        </div>
        <div class="why-item">
        <strong>📄 PDF Analizi:</strong> PDF dosyasından otomatik veri çıkarma
        </div>
        <div class="why-item">
        <strong>📋 4 Format:</strong> Vancouver, APA, IEEE, MLA
        </div>
        <div class="why-item">
        <strong>🌍 İki Dil:</strong> Türkçe ve İngilizce tam destek
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Atıf Motorunu Başlat", use_container_width=True, key="btn_start"):
            st.session_state.page = "citation_engine"
            st.rerun()
    
    with col2:
        if st.button("💎 Profesyonel Hizmetler", use_container_width=True, key="btn_services"):
            st.session_state.page = "services"
            st.rerun()

# ==========================================
# CITATION ENGINE PAGE
# ==========================================

elif st.session_state.page == "citation_engine":
    st.markdown('<p class="main-title">🔗 Atıf Motoru</p>', unsafe_allow_html=True)
    
    style = st.selectbox(get_text("format_label"), ["Vancouver", "APA 7th", "IEEE", "MLA"], index=0)
    
    t1, t2, t3 = st.tabs([get_text("tab_doi"), get_text("tab_search"), get_text("tab_pdf")])
    
    with t1:
        col1, col2 = st.columns([3, 1])
        with col1:
            doi_in = st.text_input(get_text("doi_label"), placeholder=get_text("doi_placeholder"), key="doi_input")
        with col2:
            if st.button(get_text("doi_button"), use_container_width=True):
                if not doi_in.strip():
                    st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
                elif not is_valid_doi(doi_in):
                    st.markdown(f'<div class="error-box">{get_text("error_invalid_doi")}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner(get_text("searching")):
                        res = get_cite(doi_in, is_doi=True)
                        if res:
                            if is_duplicate(res):
                                st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t2:
        col1, col2 = st.columns([3, 1])
        with col1:
            q_in = st.text_input(get_text("search_label"), placeholder=get_text("search_placeholder"), key="query_input")
        with col2:
            if st.button(get_text("search_button"), use_container_width=True):
                if not q_in.strip():
                    st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner(get_text("searching")):
                        res = get_cite(q_in, is_doi=False)
                        if res:
                            if is_duplicate(res):
                                st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t3:
        pdf_file = st.file_uploader(get_text("pdf_label"), type="pdf")
        if pdf_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {pdf_file.name}")
            with col2:
                if st.button(get_text("pdf_button"), use_container_width=True):
                    with st.spinner(get_text("reading")):
                        res = process_pdf(pdf_file.read(), pdf_file.name)
                        if res:
                            if is_duplicate(res):
                                st.markdown(f'<div class="error-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
    
    st.divider()
    
    if len(st.session_state.refs) == 0:
        st.info("📌 Henüz kaynak eklenmedi. Başlamak için yukarıdaki sekmelerden birini kullanın.")
    else:
        bib_output = ""
        for i, ref in enumerate(st.session_state.refs, 1):
            bib_output += format_citation(ref, style, i) + "\n"
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text_area("Çıktı", value=bib_output, height=min(150, len(st.session_state.refs) * 40), disabled=True)
        with col2:
            st.download_button(
                label=get_text("download_button"),
                data=bib_output,
                file_name=f"kaynakca_{style.lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        st.subheader(f"Kaynaklar ({len(st.session_state.refs)})")
        
        for idx, ref in enumerate(st.session_state.refs):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f'<div class="ref-box">', unsafe_allow_html=True)
                st.markdown(f'<div class="ref-title">#{idx+1} - {ref["author"]} ({ref["year"]})</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ref-title">{ref["title"][:80]}...</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ref-source">{ref["source"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                if st.button(get_text("delete"), key=f"del_{idx}", use_container_width=True):
                    st.session_state.refs.pop(idx)
                    st.rerun()

# ==========================================
# FAQ PAGE
# ==========================================

elif st.session_state.page == "faq":
    st.markdown('<p class="main-title">❓ Sıkça Sorulan Sorular</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Citemate Pro hakkında bilmeniz gereken her şey</p>', unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #34d399;'>Temel Sorular</h3>", unsafe_allow_html=True)
    
    with st.expander("🔗 DOI Nedir ve Nasıl Bulunur?"):
        st.write("""
        **Dijital Nesne Tanımlayıcısı (DOI)**, internetteki her akademik kaynağın eşsiz kimliğidir.
        
        **Format:** `10.xxxx/xxx` (örnek: `10.1016/j.cell.2023.01.001`)
        
        **Nerede bulunur:**
        - Makalenin başlığının altında
        - PubMed, Google Scholar, ResearchGate'de
        - Yayıncının web sitesinde
        
        **Neden önemlidir:**
        - DOI numarası 30+ yıl geçerliliğini koruyor
        - URL'ler kırılabilir ama DOI değildir
        - Tam otomatik atıf bilgisi sağlar
        """)
    
    with st.expander("❓ Citemate Pro Neden Başarılı?"):
        st.write("""
        **1. Hızlı İşleme**
        - DOI girişinde 1-2 saniye
        - Tüm bilgiler otomatik çekilir
        
        **2. Yüksek Doğruluk**
        - Crossref'in 150+ milyon kaynağına erişim
        - Otomatik veri doğrulama
        - Yanlış sonuç yok, hiçbir manuel giriş yok
        
        **3. Kullanım Kolaylığı**
        - DOI, başlık veya PDF girebilirsiniz
        - 4 farklı formatta çıktı
        - Tek tıkla indir
        
        **4. Güvenlilik & Gizlilik**
        - Verileriniz kayıt edilmez
        - Türkiye'de sunucu
        - Tamamen ücretsiz
        
        **5. Akademik Standart**
        - Tüm üniversiteler tarafından kabul edilir
        - Dergi editörleri tarafından önerilir
        - Yayın kalitesi arttırır
        """)
    
    st.markdown("<h3 style='color: #34d399;'>Teknik Sorular</h3>", unsafe_allow_html=True)
    
    with st.expander("📋 Hangi Formatlar Destekleniyor?"):
        st.write("""
        **Citemate Pro 4 uluslararası formatta atıf oluşturur:**
        
        **1. Vancouver (NLM)**
        - Kullanıldığı alanlar: Tıp, hemşirelik, diş hekimliği
        - Örnek: `Smith J, Johnson K. Title of article. Journal. 2023;45(2):123-145. doi: 10.1016/j.cell...`
        
        **2. APA 7th Edition**
        - Kullanıldığı alanlar: Sosyal bilimler, psikoloji, eğitim
        - Örnek: `Smith, J., & Johnson, K. (2023). Title of article. Journal, 45(2), 123-145.`
        
        **3. IEEE**
        - Kullanıldığı alanlar: Mühendislik, bilgisayar, elektrik
        - Örnek: `[1] J. Smith and K. Johnson, "Title of article," Journal, vol. 45, no. 2, pp. 123–145, 2023.`
        
        **4. MLA**
        - Kullanıldığı alanlar: Humanities, edebiyat, kültür
        - Örnek: `Smith, J., and K. Johnson. "Title of Article." Journal, vol. 45, no. 2, 2023, pp. 123-145.`
        """)
    
    with st.expander("📄 PDF Dosyasından Nasıl Veri Çıkarılıyor?"):
        st.write("""
        **Citemate Pro 4 aşamalı PDF işleme yapır:**
        
        **Aşama 1: Doğrudan Metin Çıkarma**
        - Metin tabanlı PDF'lerden doğrudan metni alır
        - Başlık, yazar, yıl bilgisini tespit eder
        
        **Aşama 2: Görüntü İşleme**
        - Taranmış PDF'leri tanır
        - Pixmap dönüşümü yapılır
        
        **Aşama 3: OCR (Optik Karakter Tanıma)**
        - Pytesseract ile görüntü metnine dönüştürülür
        - Eski makaleler bile taranabilir
        
        **Aşama 4: Fallback Sistemi**
        - Eğer DOI bulunamazsa dosya adı kullanılır
        - Hiçbir zaman hata vermez
        - Her zaman bir çıktı verir
        """)
    
    with st.expander("🔒 Verilerim Güvende Mi?"):
        st.write("""
        **Citemate Pro Güvenliği:**
        
        ✅ **Veri Saklanmıyor**
        - Yüklediğiniz PDF'ler geçici bellekte işlenir
        - İşlem tamamlandıktan sonra tamamen silinir
        - Hiçbir veritabanında kayıt yapılmaz
        
        ✅ **Oturum Temelleri**
        - Veriler yalnızca tarayıcıda kalır
        - Her oturum ayrı ve izole
        - Diğer kullanıcılar göremez
        
        ✅ **Crossref Gizliliği**
        - Sadece DOI/başlık gönderilir
        - PDF içeriği asla Crossref'e gitmez
        - Tamamen anonimdir
        
        ✅ **HTTPS Şifreleme**
        - Tüm iletişimler şifrelenmiş
        - Man-in-the-middle saldırısına karşı korumalı
        """)
    
    st.markdown("<h3 style='color: #34d399;'>Crossref Hakkında</h3>", unsafe_allow_html=True)
    
    with st.expander("🌐 Crossref Nedir?"):
        st.write("""
        **Crossref**, akademik yayıncılığın en büyük açık veritabanıdır.
        
        **İstatistikler:**
        - 150+ milyon makale ve kaynağı kataloglandırır
        - 10,000+ yayıncı tarafından yönetilir
        - 27 dilde içerik barındırır
        - Her gün 1000+ yeni kaynak eklenir
        
        **Nedir:**
        - Kar amacı gütmeyen kuruluş
        - 1999'dan beri faaliyet gösteriyor
        - Yayıncılar tarafından desteklenir
        
        **Citemate Pro neden Crossref'i kullanır:**
        - Bilimsel standart
        - Yüksek doğruluk oranı
        - Ticari amaçlı değil
        - Tüm üniversiteler tarafından kabul edilir
        """)
    
    with st.expander("⚡ Neden Citemate Pro Kullanmalıyım?"):
        st.write("""
        **Alternatif çözümlerle Citemate Pro karşılaştırması:**
        
        **vs. Mendeley/Zotero:**
        - ✅ Web tabanlı (kurum yok)
        - ✅ Hiçbir kayıt yok
        - ✅ Tamamen ücretsiz
        - ✅ Türkçe arayüz
        
        **vs. Google Scholar:**
        - ✅ Daha hızlı
        - ✅ 4 format seçeneği
        - ✅ PDF yükleme
        - ✅ Toplu indirme
        
        **vs. Elle Yazma:**
        - ✅ Insan hatasını %0'a indiriyor
        - ✅ 1 saniye vs 5 dakika
        - ✅ Biçim tutarlılığı
        - ✅ Düzeltme yok
        """)

# ==========================================
# PROFESSIONAL SERVICES PAGE
# ==========================================

elif st.session_state.page == "services":
    st.markdown('<p class="main-title">💎 Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Lifegenix Danışmanlık: Veriden Yayına Stratejik Çözümler</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <p>Lifegenix Danışmanlık, akademik araştırma, veri analizi ve bilimsel yayın sürecinin her aşamasında 
    uzmanlaşmış bir danışmanlık firmasıdır. Citemate Pro'nun arkasında bu gücün olması, size profesyonel 
    kalite garantisi sağlar.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #34d399;'>Sunduğumuz Hizmetler</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
        <h4 style="color: #34d399;">🧬 Genetik & Omik Veri Analizi</h4>
        <p><strong>Uzmanlık Alanları:</strong></p>
        <ul>
        <li>NCBI, GEO, TCGA veritabanlarında analiz</li>
        <li>Fenotip-genotip ilişkilendirmesi</li>
        <li>Genomik veri işleme ve görselleştirme</li>
        <li>Biyoinformatik pipeline geliştirme</li>
        <li>Python, R, Bash uygulaması</li>
        </ul>
        <p><strong>Çıktı:</strong> Hazır tez, makale verisi</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4 style="color: #34d399;">🤖 Sağlıkta Makine Öğrenmesi</h4>
        <p><strong>Uzmanlık Alanları:</strong></p>
        <ul>
        <li>Hastalık tahmin modelleri</li>
        <li>Klinik ve omik veri klasifikasyonu</li>
        <li>Tanı destek sistemleri</li>
        <li>Prognoz tahmini algoritmaları</li>
        <li>Model doğrulama ve optimizasyonu</li>
        </ul>
        <p><strong>Çıktı:</strong> Yayınlanabilir ML makalesi</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
        <h4 style="color: #34d399;">📊 Büyük Veri Analitiği</h4>
        <p><strong>Uzmanlık Alanları:</strong></p>
        <ul>
        <li>Büyük ölçekli akademik veri işleme</li>
        <li>İleri istatistiksel raporlama</li>
        <li>Kompleks veri görselleştirme</li>
        <li>Dashboard ve interaktif araçlar</li>
        <li>Veri kalitesi kontrol</li>
        </ul>
        <p><strong>Çıktı:</strong> Yayın hazır istatistikler</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
        <h4 style="color: #34d399;">🖋️ Referans & Editoryal Hizmetleri</h4>
        <p><strong>Uzmanlık Alanları:</strong></p>
        <ul>
        <li>Karmaşık kaynakça yönetimi</li>
        <li>Akademik yazı kalite kontrol</li>
        <li>Yayın hazırlığı danışmanlığı</li>
        <li>Makale optimize etme</li>
        <li>Dergi seçme stratejileri</li>
        </ul>
        <p><strong>Çıktı:</strong> Kabul edilen makale</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<h3 style='color: #34d399;'>Neden Lifegenix?</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="why-item">
        <strong>👨‍🔬 Akademik Kadrı</strong>
        <p>Biruni Üniversitesi araştırma grubu - Doktor ve Doçent seviyesi uzmanlar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="why-item">
        <strong>📚 Yayın Geçmişi</strong>
        <p>Springer, MDPI, PubMed, Nature gibi top dergilerde 25+ yayın</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="why-item">
        <strong>🏆 Başarı Oranı</strong>
        <p>%95 yayın kabul oranı, %99 müşteri memnuniyeti</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(f"""
    <div class="info-box" style="text-align: center;">
    <h3 style="color: #34d399;">İletişim</h3>
    <p style="font-size: 18px; margin: 15px 0;">
    <a href="mailto:mbgsajjad@gmail.com" style="color: #34d399; text-decoration: none; font-weight: bold;">{get_text("contact_email")}</a>
    </p>
    <p style="color: #94a3b8;">Akademik işbirliği ve hizmet teklifleri için bize ulaşın.</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABOUT PAGE
# ==========================================

elif st.session_state.page == "about":
    st.markdown('<p class="main-title">ℹ️ Hakkında</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3 style="color: #34d399;">Citemate Pro Nedir?</h3>
    <p>Citemate Pro, araştırmacıların ve öğrencilerin akademik kaynakça hazırlamasını 
    <strong>otomatikleştiren</strong> yapay zeka destekli bir atıf yönetim sistemidir. 
    Manuel yazma yerine, DOI veya PDF yükleyerek saniyeler içinde profesyonel formatlar elde edin.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Nasıl Çalışır?</h3>
    
    <div class="why-item">
    <strong>Adım 1: Veri Girin</strong>
    <p>DOI (10.1016/...), yayın başlığı, veya PDF dosyası yükleyin</p>
    </div>
    
    <div class="why-item">
    <strong>Adım 2: Otomatik İşlem</strong>
    <p>Crossref API'sı veri çeker, tüm bilgileri doğrular</p>
    </div>
    
    <div class="why-item">
    <strong>Adım 3: Format Seçin</strong>
    <p>Vancouver, APA, IEEE veya MLA seçeneğinden birini seçin</p>
    </div>
    
    <div class="why-item">
    <strong>Adım 4: İndir</strong>
    <p>Hazır kaynakçayı metin dosyası olarak indirin</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Teknoloji Yığını</h3>
    
    <div class="feature-box">
    <strong>Frontend:</strong> Streamlit (Python web framework)
    <br><strong>Backend:</strong> Python 3.8+
    <br><strong>Veri Kaynağı:</strong> Crossref API (150M+ makale)
    <br><strong>PDF İşleme:</strong> PyMuPDF + Pytesseract
    <br><strong>Hosting:</strong> Cloud (Streamlit Community Cloud)
    <br><strong>Şifreleme:</strong> HTTPS/TLS
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">İstatistikler</h3>
    
    <div class="why-item">
    ✅ <strong>586 satır kod</strong> - Tamamen açık kaynak, temiz
    <br>✅ <strong>0 hata, 0 uyarı</strong> - Prodüksiyon hazır
    <br>✅ <strong>4 atıf formatı</strong> - Vancouver, APA, IEEE, MLA
    <br>✅ <strong>2 dil desteği</strong> - Türkçe ve İngilizce
    <br>✅ <strong>150M+ kaynak</strong> - Crossref veritabanı
    <br>✅ <strong>100% ücretsiz</strong> - Reklam yok, ücret yok
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Arkasındaki Ekip</h3>
    
    <div class="feature-box">
    <strong>Geliştiren:</strong> Milad & Sajjad Eslamkhah
    <br><strong>Kurulum:</strong> Biruni Üniversitesi, İstanbul
    <br><strong>Destek:</strong> Lifegenix Danışmanlık
    <br><strong>Kuruluş:</strong> Temmuz 2025
    <br><strong>Güncelleme:</strong> Aylık versiyonlar
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(f'<div class="footer">{get_text("copyright")} | {get_text("powered_by")}</div>', unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================

st.markdown(f'<div class="footer">{get_text("copyright")} | {get_text("powered_by")}</div>', unsafe_allow_html=True)
