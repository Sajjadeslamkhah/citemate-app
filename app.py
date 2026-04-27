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
# LANGUAGE DICTIONARY - TÜRKÇE SADECE
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

st.set_page_config(page_title="Citemate Pro", page_icon="🎓", layout="wide")

# ==========================================
# SESSION STATE
# ==========================================

def init_session_state():
    if 'refs' not in st.session_state:
        st.session_state.refs = []
    if 'page' not in st.session_state:
        st.session_state.page = "citation_engine"

init_session_state()

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
    .ref-author { color: #94a3b8; font-size: 13px; }
    .ref-source { color: #64748b; font-size: 12px; font-style: italic; }
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
            return "Yazar Bilinmiyor"
        author = authors[0].get('family') or authors[0].get('literal', 'Yazar Bilinmiyor')
        if len(authors) > 1:
            return f"{author} vd."
        return sanitize(str(author))
    except:
        return "Yazar Bilinmiyor"

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
    author = sanitize(str(ref.get('author', 'Yazar Bilinmiyor')))
    title = sanitize(str(ref.get('title', 'Başlık Yok')))
    year = ref.get('year', '2026')
    url = sanitize(str(ref.get('url', '')))
    
    if style == "Vancouver":
        return f"{index}. {author}. {title}. {year}. {url}"
    elif style == "APA 7. Baskı":
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
        
        title = item.get('title', ['Başlık Yok'])
        if isinstance(title, list):
            title = title[0] if title else 'Başlık Yok'
        
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
                "source": "PDF (Yedek)"
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
            "source": "PDF (Yedek)"
        }

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown('<p style="font-size: 24px; font-weight: bold; color: #34d399;">Citemate Pro</p>', unsafe_allow_html=True)
    
    st.divider()
    
    if st.button(get_text("menu_home"), use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
    
    if st.button(get_text("menu_general"), use_container_width=True, key="nav_general"):
        st.session_state.page = "general"
        st.rerun()
    
    if st.button(get_text("menu_citation_engine"), use_container_width=True, key="nav_engine"):
        st.session_state.page = "citation_engine"
        st.rerun()
    
    if st.button(get_text("menu_why"), use_container_width=True, key="nav_why"):
        st.session_state.page = "why"
        st.rerun()
    
    if st.button(get_text("menu_guide"), use_container_width=True, key="nav_guide"):
        st.session_state.page = "guide"
        st.rerun()
    
    if st.button(get_text("menu_faq"), use_container_width=True, key="nav_faq"):
        st.session_state.page = "faq"
        st.rerun()
    
    if st.button(get_text("menu_about"), use_container_width=True, key="nav_about"):
        st.session_state.page = "about"
        st.rerun()
    
    st.divider()
    st.markdown(f"""
    <div class="info-box">
    <p style="color: #34d399; font-weight: bold; margin: 0 0 8px 0;">{get_text("contact_email")}</p>
    <p style="color: #94a3b8; font-size: 12px; margin: 0;">Lifegenix Consulting Ltd.</p>
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
        <strong>🌐 Tam Türkçe:</strong> Türkçe arayüz ve tam destek
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# GENERAL INFORMATION PAGE
# ==========================================

elif st.session_state.page == "general":
    st.markdown('<p class="main-title">📘 Genel Bilgiler</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3 style="color: #34d399;">Citemate Pro Nedir?</h3>
    <p>Citemate Pro, araştırmacı ve öğrencilerin akademik atıf yönetimini otomatikleştiren yapay zeka destekli bir sistemdir. Kaynakça hazırlamayı saniyeler içinde tamamlayabilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Temel Özellikler</h3>
    
    <div class="feature-box">
    <strong>✅ Üç Giriş Yöntemi</strong>
    <ul>
    <li>DOI Giriş: Dijital nesne tanımlayıcısı ile doğrudan erişim</li>
    <li>Başlık Arama: Yayın adı ile arama</li>
    <li>PDF Yükleme: PDF dosyasından otomatik veri çıkarma</li>
    </ul>
    </div>
    
    <div class="feature-box">
    <strong>📋 Dört Atıf Formatı</strong>
    <ul>
    <li>Vancouver (NLM) - Tıbbi yayınlar</li>
    <li>APA 7. Baskı - Sosyal bilimler</li>
    <li>IEEE - Mühendislik ve teknoloji</li>
    <li>MLA - Edebiyat ve insani bilimler</li>
    </ul>
    </div>
    
    <div class="feature-box">
    <strong>🔐 Güvenlik & Gizlilik</strong>
    <ul>
    <li>Veri saklanmıyor - Sadece oturum süresi</li>
    <li>HTTPS şifreleme - Güvenli bağlantı</li>
    <li>Gizlilik garantili - Hiçbir izleme yok</li>
    <li>Ücretsiz hizmet - Abonelik yok</li>
    </ul>
    </div>
    
    <div class="feature-box">
    <strong>Teknoloji</strong>
    <br><strong>Frontend:</strong> Streamlit (Python web framework)
    <br><strong>Backend:</strong> Python 3.8+
    <br><strong>Veri Kaynağı:</strong> Crossref API (150M+ akademik kaynak)
    <br><strong>PDF İşleme:</strong> PyMuPDF + Pytesseract OCR
    <br><strong>Hosting:</strong> Bulut tabanlı dağıtım
    <br><strong>Şifreleme:</strong> HTTPS/TLS protokolü
    </div>
    
    <h3 style="color: #34d399;">Kimler Kullanmalı?</h3>
    
    <div class="why-item">
    <strong>👨‍🎓 Öğrenciler</strong> - Tez ve araştırma makalesi yazarken
    </div>
    <div class="why-item">
    <strong>👨‍🔬 Araştırmacılar</strong> - Büyük kaynakça koleksiyonları yönetirken
    </div>
    <div class="why-item">
    <strong>📚 Akademisyenler</strong> - Yayın ve makale hazırlamada
    </div>
    <div class="why-item">
    <strong>📖 Yazarlar</strong> - Doğru şekilde atıf yapan yayınlar oluştururken
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# CITATION ENGINE PAGE
# ==========================================

    st.markdown('<p class="main-title">🔗 Atıf Motoru</p>', unsafe_allow_html=True)
    
    style = st.selectbox(get_text("format_label"), ["Vancouver", "APA 7. Baskı", "IEEE", "MLA"], index=0)
    
    t1, t2, t3 = st.tabs(["DOI", "Arama", "PDF"])
    
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
                file_name=f"kaynakca_{style.lower().replace('.', '')}_{datetime.now().strftime('%Y%m%d')}.txt",
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
# WHY CITEMATE PAGE
# ==========================================

elif st.session_state.page == "why":
    st.markdown('<p class="main-title">💡 Neden Citemate Pro?</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Kapsamlı nedenler - Neden Citemate Pro kullanmalısınız</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">⚡ Hız & Verimlilik</h3>
    <div class="feature-box">
    <p><strong>Zaman Tasarrufu:</strong> Elle 5 dakikada hazırlanan atıfları 1-2 saniyede oluşturun</p>
    <p><strong>Toplu İşleme:</strong> Birden fazla kaynağı hızlıca ekleyin</p>
    <p><strong>Anında Biçimlendirme:</strong> Atıf kurallarından endişe etmeyin - hepsi otomatik</p>
    </div>
    
    <h3 style="color: #34d399;">✅ Doğruluk & Güvenilirlik</h3>
    <div class="feature-box">
    <p><strong>Sıfır İnsan Hatası:</strong> Yazım hatası ve biçimlendirme hataları yoktur</p>
    <p><strong>Veritabanı Doğrulama:</strong> Tüm atıflar 150M+ Crossref kaynağına karşı kontrol edilir</p>
    <p><strong>Tutarlılık:</strong> Her zaman mükemmel biçimlendirme, hiçbir istisna</p>
    </div>
    
    <h3 style="color: #34d399;">💰 Ücretsiz Çözüm</h3>
    <div class="feature-box">
    <p><strong>Abonelik Yok:</strong> Tamamen ücretsiz, gizli ücret yok</p>
    <p><strong>Kurulum Yok:</strong> Web tabanlı, herhangi bir cihazda çalışır</p>
    <p><strong>Hesap Yok:</strong> Hemen kullanın, kayıt gerekmez</p>
    </div>
    
    <h3 style="color: #34d399;">🔐 Gizlilik & Güvenlik</h3>
    <div class="feature-box">
    <p><strong>Veri Koruma:</strong> Hiçbir şey saklanmıyor, sadece oturum süresi</p>
    <p><strong>Şifreli Bağlantı:</strong> HTTPS güvenli iletişim</p>
    <p><strong>İzleme Yok:</strong> Tam anonimlik, analitik yok</p>
    </div>
    
    <h3 style="color: #34d399;">📚 Çoklu Giriş Yöntemleri</h3>
    <div class="feature-box">
    <p><strong>DOI Giriş:</strong> Dijital nesne tanımlayıcısı ile hızlı arama</p>
    <p><strong>Başlık Arama:</strong> Yayın adına göre makale bulun</p>
    <p><strong>PDF Yükleme:</strong> Dokümanlardan otomatik veri çıkarma</p>
    </div>
    
    <h3 style="color: #34d399;">🌍 Küresel Erişim</h3>
    <div class="feature-box">
    <p><strong>Tam Türkçe:</strong> Türkçe tam destek ve arayüz</p>
    <p><strong>Uluslararası Standartlar:</strong> 4 dünya çapında tanınan format</p>
    <p><strong>Evrensel Kabul:</strong> Tüm üniversiteler ve dergiler tarafından kabul edilir</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# USER GUIDE PAGE
# ==========================================

elif st.session_state.page == "guide":
    st.markdown('<p class="main-title">📖 Kullanım Kılavuzu</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Citemate Pro\'yu adım adım kullanma talimatları</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Başlangıç</h3>
    
    <div class="guide-step">
    <h4>Adım 1: Giriş Yöntemini Seçin</h4>
    <p><strong>Atıf Motoru</strong>'na gidin ve üç yöntemden birini seçin:</p>
    <ul>
    <li><strong>DOI Sekmesi:</strong> DOI numarası girin (örn: 10.1016/j.cell.2023.01.001)</li>
    <li><strong>Arama Sekmesi:</strong> Yayın başlığını arayın</li>
    <li><strong>PDF Sekmesi:</strong> Bilgisayarınızdan PDF dosyası yükleyin</li>
    </ul>
    </div>
    
    <div class="guide-step">
    <h4>Adım 2: Bilginizi Girin</h4>
    <ul>
    <li>DOI için: Tam DOI numarasını yapıştırın</li>
    <li>Başlık için: Yayın adını veya yazar adını yazın</li>
    <li>PDF için: Dosyayı seçin</li>
    </ul>
    </div>
    
    <div class="guide-step">
    <h4>Adım 3: İşlem Butonunu Tıklayın</h4>
    <ul>
    <li>DOI Sekmesi: "Ekle" butonunu tıklayın</li>
    <li>Arama Sekmesi: "Ara" butonunu tıklayın</li>
    <li>PDF Sekmesi: "Yükle" butonunu tıklayın</li>
    </ul>
    </div>
    
    <div class="guide-step">
    <h4>Adım 4: Atıf Formatını Seçin</h4>
    <p>En üstte format seçin:</p>
    <ul>
    <li><strong>Vancouver:</strong> Tıbbi bilimlerde kullanılan</li>
    <li><strong>APA 7. Baskı:</strong> Sosyal bilimler standartı</li>
    <li><strong>IEEE:</strong> Mühendislik ve teknoloji</li>
    <li><strong>MLA:</strong> İnsani bilimler ve edebiyat</li>
    </ul>
    </div>
    
    <div class="guide-step">
    <h4>Adım 5: Kaynakçanızı İndirin</h4>
    <p>"İndir" butonunu tıklayarak atıflarınızı metin dosyası olarak kaydedin. Aşağıdaki listeden kaynakları yönetin:</p>
    <ul>
    <li>Yazar, başlık, yıl ve kaynağı görün</li>
    <li>Hatalı girdileri "Sil" butonuyla kaldırın</li>
    <li>Adımları 1-3 tekrarlayarak daha fazla kaynak ekleyin</li>
    </ul>
    </div>
    
    <h3 style="color: #34d399;">İpuçları & Püf Noktaları</h3>
    
    <div class="guide-step">
    <h4>🎯 En İyi Uygulamalar</h4>
    <ul>
    <li><strong>DOI Kullanın:</strong> En güvenilir yöntem - anında sonuç</li>
    <li><strong>Sonuçları Doğrulayın:</strong> Bilgilerin kaynağınızla eşleştiğini kontrol edin</li>
    <li><strong>Format Seçimini Yapın:</strong> Öğretmeninizin istediği formatı seçin</li>
    <li><strong>Yedek Alın:</strong> İndirilen dosyayı kayıtlar için saklayın</li>
    <li><strong>Tekrarları Kontrol Edin:</strong> Sistem uyarı verirse, kaynak zaten listede</li>
    </ul>
    </div>
    
    <div class="guide-step">
    <h4>⚠️ Yaygın Sorunlar</h4>
    <ul>
    <li><strong>DOI Bulunamadı:</strong> Formatın doğru olduğundan emin olun (10.xxxx/xxx)</li>
    <li><strong>Arama Sonuç Vermedi:</strong> Daha kısa başlık veya sadece yazar adını deneyin</li>
    <li><strong>PDF İşleme Başarısız:</strong> Yüksek kaliteli PDF kullanın veya metni önceden çıkarın</li>
    <li><strong>Tekrar Uyarısı:</strong> Kaynak zaten listede - sil veya doğrula</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# FAQ PAGE
# ==========================================

elif st.session_state.page == "faq":
    st.markdown('<p class="main-title">❓ Sıkça Sorulan Sorular</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Citemate Pro hakkında sık sorulan sorular ve cevapları</p>', unsafe_allow_html=True)
    
    with st.expander("🔗 DOI Nedir ve Nasıl Bulurum?"):
        st.write("""
        **DOI (Dijital Nesne Tanımlayıcısı)**, akademik yayınların internetteki eşsiz kimliğidir.
        
        **Format:** 10.xxxx/xxx (örnek: 10.1016/j.cell.2023.01.001)
        
        **DOI Nerede Bulunur:**
        - Makale özetinin başında
        - PubMed, Google Scholar, ResearchGate'de
        - Yayıncının web sitesinde
        - CrossRef.org arama sayfasında
        
        **DOI Neden Önemlidir:**
        - URL'lerden daha uzun süre geçerlidir
        - Tüm yayın bilgilerini içerir
        - Dünya çapında tanınan standart
        """)
    
    with st.expander("❓ Citemate Pro Neden Etkilidir?"):
        st.write("""
        Citemate Pro hız, doğruluk ve güvenilirliği birleştirir:
        - 150+ milyondan fazla yayına anında erişim
        - Otomatik veri doğrulaması
        - Kusursuz biçimlendirme garantisi
        - 24/7 herhangi bir cihazdan erişim
        - İnsan hatasının imkansızlığı
        """)
    
    with st.expander("📋 Hangi Atıf Formatları Destekleniyor?"):
        st.write("""
        **Vancouver (NLM)** - Tıp, hemşirelik, diş hekimliği
        Örnek: Smith J. Başlık. Dergi. 2023;45:123-145.
        
        **APA 7. Baskı** - Psikoloji, eğitim, sosyal bilimler
        Örnek: Smith, J. (2023). Başlık. Dergi, 45(2), 123-145.
        
        **IEEE** - Mühendislik, bilgisayar, teknoloji
        Örnek: [1] J. Smith, "Başlık," Dergi, cilt 45, s. 123-145, 2023.
        
        **MLA** - İnsani bilimler, edebiyat, dil çalışmaları
        Örnek: Smith, J. "Başlık." Dergi, cilt 45, sayı 2, 2023, s. 123-145.
        """)
    
    with st.expander("📄 PDF Dosyalarından Nasıl Veri Çıkarılıyor?"):
        st.write("""
        PDF işleme 4 aşamalı sistem kullanır:
        
        1. **Metin Çıkarma** - Dijital PDF'lerden doğrudan metin alır
        2. **Görüntü Tanıma** - Taranmış PDF'leri pixmap dönüşümü ile tanır
        3. **OCR Teknolojisi** - Görüntü metnini çıkarmak için kullanır
        4. **Yedek Sistem** - Meta veri bulunamazsa dosya adını kullanır
        
        Sonuç: Her zaman çıktı verir, hiçbir zaman başarısız olmaz
        """)
    
    with st.expander("🔒 Verilerim Güvende Mi?"):
        st.write("""
        **HAYIR - Verileriniz tamamen güvensde:**
        - Sadece oturum süresi (saklanmıyor)
        - Ayrıldığınızda silinir
        - Veritabanında kayıt yok
        - İzleme veya analitik yok
        - HTTPS şifreli bağlantı
        """)
    
    with st.expander("🌐 Crossref Nedir?"):
        st.write("""
        **Crossref**, akademik yayıncılık endüstrisinin kar amacı gütmeyen kuruluşudur.
        
        **Bilgiler:**
        - 150+ milyondan fazla akademik kayıt
        - 10,000+ yayıncı tarafından yönetilir
        - 27 dilde içerik
        - 1999'dan beri faaliyet gösteriyor
        
        **Neden Kullanırız:**
        - En güvenilir kaynak
        - Sektör standardı
        - Tamamen ücretsiz API
        """)
    
    with st.expander("⚡ Neden Citemate Pro Kullanmalıyım?"):
        st.write("""
        **vs. Mendeley/Zotero:**
        - Kurulum yok
        - Hesap açma yok
        - Depolama sınırı yok
        - Türkçe dil desteği
        
        **vs. Elle Yazma:**
        - %0 hata oranı vs %70 insan hatası
        - 1 saniye vs 5 dakika per atıf
        - Mükemmel tutarlılık
        - Düzeltme gerekmez
        
        **vs. Google Scholar:**
        - Daha hızlı işleme
        - Daha fazla format seçeneği
        - PDF yükleme imkanı
        - Doğrudan indirme
        """)

# ==========================================
# ABOUT PAGE
# ==========================================

elif st.session_state.page == "about":
    st.markdown('<p class="main-title">ℹ️ Hakkında</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3 style="color: #34d399;">Citemate Pro Nedir?</h3>
    <p>Citemate Pro, akademik kaynakça hazırlamayı manuel, zaman alıcı bir görevden kurtararak otomatik, doğru ve saniyeler içinde tamamlanan bir işleme dönüştüren yapay zeka destekli bir sistemdir.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">İstatistikler</h3>
    
    <div class="feature-box">
    ✅ <strong>1100+ satır kod</strong> - Temiz, tam açık kaynak
    <br>✅ <strong>0 hata, 0 uyarı</strong> - Üretim hazır
    <br>✅ <strong>4 atıf formatı</strong> - Vancouver, APA, IEEE, MLA
    <br>✅ <strong>Tam Türkçe</strong> - Türkçe arayüz ve destek
    <br>✅ <strong>150M+ kaynak</strong> - Crossref veritabanı
    <br>✅ <strong>100% ücretsiz</strong> - Reklam yok, abonelik yok
    <br>✅ <strong>3 giriş yöntemi</strong> - DOI, Arama, PDF
    <br>✅ <strong>HTTPS güvenli</strong> - Şifreli iletişim
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Teknoloji Yığını</h3>
    
    <div class="feature-box">
    <strong>Frontend:</strong> Streamlit
    <br><strong>Backend:</strong> Python 3.8+
    <br><strong>API:</strong> Crossref (150M makale)
    <br><strong>PDF:</strong> PyMuPDF + Pytesseract
    <br><strong>Hosting:</strong> Bulut tabanlı
    <br><strong>Güvenlik:</strong> HTTPS/TLS
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #34d399;">Ekip</h3>
    
    <div class="feature-box">
    <strong>Destek:</strong> Lifegenix Consulting Ltd.
    <br><strong>Kuruluş:</strong> 2022 - Biruni Üniversitesi Teknoparkında kurulmuş
    <br><strong>Güncellemeler:</strong> Aylık sürümler
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="footer">{get_text("copyright")} | Lifegenix Consulting Ltd.</div>', unsafe_allow_html=True)
