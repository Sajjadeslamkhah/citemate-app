import streamlit as st
import requests
import re
from datetime import datetime
import os
from typing import Optional, Dict, List
import html
from urllib.parse import quote

# Safely import PyMuPDF
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# ==========================================
# 1. LANGUAGE DICTIONARY (Complete Localization)
# ==========================================

LANGUAGES = {
    "TR": {
        "app_title": "Citemate Pro | Elite Atıf Zekası",
        "app_subtitle": "Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi",
        "sidebar_brand": "Citemate Pro",
        "sidebar_caption": "Elite Akademik Çözümler | Lifegenix Tarafından",
        "menu_label": "SİSTEM MENÜSÜ",
        "menu_citation_engine": "🏠 Atıf Motoru",
        "menu_services": "💎 Profesyonel Hizmetler",
        "contact_title": "📩 Bize Ulaşın",
        "contact_desc": "Akademik işbirliği ve kurumsal analiz teklifleri için ulaşın.",
        "contact_btn": "✉️ Mesaj Gönder",
        "copyright": "© 2026 Lifegenix Danışmanlık tarafından kurulmuştur. Tüm hakları saklıdır.",
        "info_text": "Citemate Pro, araştırmacıların ve öğrencilerin kaynakça hazırlama yükünü hafifletmek için tasarlanmış, yapay zeka destekli bir atıf düzenleme motorudur. DOI numarası, yayın başlığı veya doğrudan PDF dosyanızı kullanarak saniyeler içinde hatasız; Vancouver, APA, IEEE ve MLA formatlarında profesyonel referanslar oluşturur. Karmaşık akademik standartları otomatiğe bağlayarak, enerjinizi sadece araştırmanıza odaklamanızı sağlar.",
        "format_label": "Tercih Edilen Standard:",
        "tab_doi": "🔗 DOI Entegrasyonu",
        "tab_search": "🔍 Global Arama",
        "tab_pdf": "📄 Akıllı PDF Analizi",
        "doi_label": "DOI Numarası:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Kaynağı İşle",
        "search_label": "Yayın Başlığı:",
        "search_placeholder": "Tam başlığı giriniz...",
        "search_button": "Veritabanında Ara",
        "pdf_label": "PDF Yükle",
        "pdf_help": "PDF'den otomatik olarak DOI çıkarılır",
        "pdf_button": "Metadataları Çözümle",
        "bibliography_title": "Kaynakça Çıktı",
        "bibliography_label": "Kaynakça (İndir veya Kopyala):",
        "download_button": "Kaynakçayı İndir",
        "copy_button": "Kopyala (Ctrl+C)",
        "clear_button": "Tüm Kayıtları Temizle",
        "confirm_delete": "Eminiz?",
        "sources_title": "Eklenen Kaynaklar",
        "delete_source": "Sil",
        "faq_title": "Sıkça Sorulan Sorular",
        "faq_doi": "DOI Nedir?",
        "faq_doi_ans": "Dijital Nesne Tanımlayıcısı (DOI), makalelerin internetteki kalıcı kimliğidir. 10.xxxx/xxx formatındadır.",
        "faq_formats": "Hangi formatlar destekleniyor?",
        "faq_formats_ans": "Vancouver, APA 7, IEEE ve MLA standartlarını tam uyumlu destekliyoruz.",
        "faq_pdf": "PDF dosyalarından nasıl veri çıkarılıyor?",
        "faq_pdf_ans": "PDF'den DOI otomatik olarak çıkarılır ve Crossref veritabanından metadata alınır.",
        "why_title": "Neden Citemate Pro?",
        "why_speed": "Hız: DOI ile saniyeler içinde atıf",
        "why_accuracy": "Doğruluk: Global Crossref veritabanı ile senkronize",
        "why_free": "Ücretsiz: Araştırmacılar için tamamen ücretsiz",
        "why_auto": "Otomatik: Formatlama tamamen otomatik",
        "why_secure": "Güvenli: Verileriniz gizli kalır",
        "services_title": "Profesyonel Hizmetler",
        "services_subtitle": "Lifegenix Danışmanlık: Veriden Yayına Stratejik Çözümler",
        "service_genetic": "Genetik Veri Analizi",
        "service_genetic_desc": "NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve fenotip-genotip ilişkilendirmesi.",
        "service_ml": "Sağlıkta Makine Öğrenmesi",
        "service_ml_desc": "Klinik ve omik veriler kullanılarak geliştirilen hastalık tahmin, sınıflandırma ve yapay zeka modelleri.",
        "service_bigdata": "Büyük Veri Analitiği",
        "service_bigdata_desc": "Büyük ölçekli akademik verilerin Python tabanlı ileri istatistiksel raporlanması ve görselleştirilmesi.",
        "service_editorial": "Referans Yazımı & Editoryal",
        "service_editorial_desc": "Karmaşık yayınların referans yönetiminin Lifegenix uzmanlığıyla yüksek standartta düzenlenmesi.",
        "error_invalid_doi": "❌ Geçersiz DOI formatı. Örnek: 10.1016/j.cell...",
        "error_empty_input": "❌ Lütfen bir giriş yapın",
        "error_invalid_format": "❌ Geçersiz formatı",
        "error_no_results": "❌ Sonuç bulunamadı",
        "error_timeout": "⏱️ İstek timeout oldu (10s)",
        "error_connection": "🌐 Bağlantı hatası - interneti kontrol edin",
        "error_json": "JSON ayrıştırma hatası",
        "error_parsing": "Veri ayrıştırma hatası",
        "error_pdf": "PDF işleme hatası",
        "error_pymupdf": "📦 PyMuPDF yüklü değil. Çalıştırın: pip install pymupdf",
        "error_no_doi": "Dosyada DOI tanımlayıcı bulunamadı",
        "success_added": "✅ Kaynak başarıyla eklendi!",
        "warning_duplicate": "⚠️ Bu kaynak zaten eklendi!",
        "warning_copied": "✅ Metin kopyalandı! Ctrl+V ile yapıştır",
        "warning_cleared": "✅ Tüm kaynaklar silindi",
        "searching": "Aranıyor...",
        "reading": "Okunuyor...",
        "analyzing": "Analiz ediliyor...",
    },
    "EN": {
        "app_title": "Citemate Pro | Elite Citation Intelligence",
        "app_subtitle": "Seamless Citation Management for Academic Excellence",
        "sidebar_brand": "Citemate Pro",
        "sidebar_caption": "Elite Academic Solutions | Powered by Lifegenix",
        "menu_label": "SYSTEM MENU",
        "menu_citation_engine": "🏠 Citation Engine",
        "menu_services": "💎 Professional Services",
        "contact_title": "📩 Contact Us",
        "contact_desc": "Reach out for academic collaboration and analysis offers.",
        "contact_btn": "✉️ Send Message",
        "copyright": "© 2026 Lifegenix Consulting. All rights reserved.",
        "info_text": "Citemate Pro is an AI-powered citation editing engine designed to help researchers and students lighten the burden of bibliography preparation. Using DOI numbers, publication titles, or PDF files directly, it creates flawless professional references in Vancouver, APA, IEEE, and MLA formats within seconds. By automating complex academic standards, it lets you focus your energy solely on your research.",
        "format_label": "Preferred Citation Style:",
        "tab_doi": "🔗 DOI Integration",
        "tab_search": "🔍 Global Search",
        "tab_pdf": "📄 Smart PDF Analysis",
        "doi_label": "DOI Number:",
        "doi_placeholder": "10.1016/j.cell...",
        "doi_button": "Process Source",
        "search_label": "Publication Title:",
        "search_placeholder": "Enter full title...",
        "search_button": "Search Database",
        "pdf_label": "Upload PDF",
        "pdf_help": "DOI is automatically extracted from PDF",
        "pdf_button": "Analyze Metadata",
        "bibliography_title": "Bibliography Output",
        "bibliography_label": "Bibliography (Download or Copy):",
        "download_button": "Download Bibliography",
        "copy_button": "Copy (Ctrl+C)",
        "clear_button": "Clear All Records",
        "confirm_delete": "Are you sure?",
        "sources_title": "Added Sources",
        "delete_source": "Delete",
        "faq_title": "Frequently Asked Questions",
        "faq_doi": "What is DOI?",
        "faq_doi_ans": "Digital Object Identifier (DOI) is the permanent identifier of articles on the internet. Format: 10.xxxx/xxx",
        "faq_formats": "Which formats are supported?",
        "faq_formats_ans": "We fully support Vancouver, APA 7, IEEE, and MLA standards.",
        "faq_pdf": "How is data extracted from PDF files?",
        "faq_pdf_ans": "DOI is automatically extracted from PDF and metadata is fetched from Crossref database.",
        "why_title": "Why Citemate Pro?",
        "why_speed": "Speed: Citations in seconds with DOI",
        "why_accuracy": "Accuracy: Synchronized with Global Crossref database",
        "why_free": "Free: Completely free access for researchers",
        "why_auto": "Automated: Completely automatic formatting",
        "why_secure": "Secure: Your data remains private",
        "services_title": "Professional Services",
        "services_subtitle": "Lifegenix Consulting: Strategic Solutions from Data to Publication",
        "service_genetic": "Genetic Data Analysis",
        "service_genetic_desc": "Python-based processing of NCBI, GEO, and TCGA large datasets and phenotype-genotype correlation.",
        "service_ml": "Machine Learning in Healthcare",
        "service_ml_desc": "Disease prediction, classification, and AI models developed using clinical and omic data.",
        "service_bigdata": "Big Data Analytics",
        "service_bigdata_desc": "Python-based advanced statistical reporting and visualization of large-scale academic data.",
        "service_editorial": "Reference Writing & Editorial",
        "service_editorial_desc": "Reference management of complex publications organized to high standards with Lifegenix expertise.",
        "error_invalid_doi": "❌ Invalid DOI format. Example: 10.1016/j.cell...",
        "error_empty_input": "❌ Please provide an input",
        "error_invalid_format": "❌ Invalid format",
        "error_no_results": "❌ No results found",
        "error_timeout": "⏱️ Request timeout (10s)",
        "error_connection": "🌐 Connection error - check internet",
        "error_json": "JSON parsing error",
        "error_parsing": "Data parsing error",
        "error_pdf": "PDF processing error",
        "error_pymupdf": "📦 PyMuPDF not installed. Run: pip install pymupdf",
        "error_no_doi": "No DOI identifier found in file",
        "success_added": "✅ Source successfully added!",
        "warning_duplicate": "⚠️ This source already exists!",
        "warning_copied": "✅ Text copied! Use Ctrl+V to paste",
        "warning_cleared": "✅ All sources cleared",
        "searching": "Searching...",
        "reading": "Reading...",
        "analyzing": "Analyzing...",
    }
}

# ==========================================
# 2. PAGE CONFIGURATION & SECURITY
# ==========================================

st.set_page_config(
    page_title="Citemate Pro | Elite Citation Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def add_seo_safe():
    """Add safe SEO meta tags without XSS risk"""
    meta = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Citemate Pro: Academic citation management and bibliography creation">
    <meta name="keywords" content="citation, bibliography, vancouver, apa, ieee, mla, academic">
    """
    st.components.v1.html(meta, height=0)

add_seo_safe()

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================

def init_session_state():
    """Initialize all session state variables safely"""
    if 'refs' not in st.session_state:
        st.session_state.refs = []
    if 'page' not in st.session_state:
        st.session_state.page = "citation_engine"
    if 'lang' not in st.session_state:
        st.session_state.lang = "TR"
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

init_session_state()

def get_text(key: str) -> str:
    """Get translated text safely"""
    lang = st.session_state.lang
    if lang not in LANGUAGES:
        lang = "TR"
    if key not in LANGUAGES[lang]:
        return key
    return LANGUAGES[lang][key]

# ==========================================
# 4. DESIGN AND STYLING
# ==========================================

MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-title { 
        font-size: 62px !important; 
        font-weight: 900 !important; 
        color: #34d399; 
        text-shadow: 0px 0px 25px rgba(52, 211, 153, 0.4); 
        margin-bottom: 0px; 
        letter-spacing: -1px; 
    }
    .sub-title { 
        color: #f8fafc; 
        font-size: 22px; 
        margin-bottom: 45px; 
        font-weight: 300; 
        letter-spacing: 1px; 
    }
    .sidebar-brand { 
        font-size: 28px !important; 
        font-weight: bold; 
        color: #34d399; 
        margin-bottom: 10px; 
    }
    .contact-container { 
        background: #1e293b; 
        padding: 18px; 
        border-radius: 15px; 
        margin-top: 25px; 
        border: 1px solid #334155; 
    }
    .contact-btn { 
        display: block; 
        background: #34d399; 
        color: black !important; 
        padding: 12px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold; 
        text-decoration: none; 
        margin-top: 10px; 
        transition: 0.3s ease; 
    }
    .contact-btn:hover { 
        background: #10b981; 
        transform: translateY(-2px); 
    }
    .info-box { 
        background-color: rgba(52, 211, 153, 0.05); 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px dashed rgba(52, 211, 153, 0.3); 
        margin-bottom: 35px; 
    }
    .service-card { 
        background: #161b22; 
        padding: 30px; 
        border-radius: 18px; 
        border-top: 5px solid #34d399; 
        margin-bottom: 25px; 
    }
    .feature-tag { 
        background: #064e3b; 
        color: #34d399; 
        padding: 5px 12px; 
        border-radius: 6px; 
        font-size: 11px; 
        font-weight: bold; 
        margin-right: 6px; 
        text-transform: uppercase; 
    }
    .footer { 
        color: #64748b; 
        font-size: 14px; 
        text-align: center; 
        margin-top: 80px; 
        padding: 25px; 
        border-top: 1px solid #1e293b; 
    }
    .error-box {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    .success-box {
        background-color: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        color: #86efac;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        color: #fcd34d;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 5. UTILITY FUNCTIONS (Security-Enhanced)
# ==========================================

def is_valid_doi(doi_str: str) -> bool:
    """Validate DOI format safely"""
    if not isinstance(doi_str, str):
        return False
    doi_pattern = r'^10\.\d{4,}/[^\s]+$'
    return bool(re.match(doi_pattern, doi_str.strip()))

def extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from text safely"""
    if not isinstance(text, str):
        return None
    doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
    return doi_match.group().strip("/") if doi_match else None

def sanitize_string(s: str, max_length: int = 500) -> str:
    """Sanitize string for security"""
    if not isinstance(s, str):
        return ""
    s = html.escape(s.strip())
    return s[:max_length]

def get_author_string(item: dict) -> str:
    """Extract author name safely"""
    try:
        if not isinstance(item, dict):
            return "Anonim"
        
        authors = item.get('author', [])
        if not isinstance(authors, list) or not authors:
            return "Anonim"
        
        author1 = authors[0]
        if not isinstance(author1, dict):
            return "Anonim"
        
        first_name = author1.get('family') or author1.get('literal', 'Anonim')
        first_name = sanitize_string(str(first_name))
        
        if len(authors) > 1:
            return f"{first_name} et al."
        
        return first_name
    except:
        return "Anonim"

def get_year(item: dict) -> str:
    """Extract publication year safely"""
    try:
        if not isinstance(item, dict):
            return str(datetime.now().year)
        
        for key in ['published-online', 'published-print', 'created', 'issued']:
            if key in item and isinstance(item[key], dict):
                date_parts = item[key].get('date-parts')
                if date_parts and isinstance(date_parts, list) and len(date_parts) > 0:
                    if isinstance(date_parts[0], list) and len(date_parts[0]) > 0:
                        year = date_parts[0][0]
                        if isinstance(year, int) and 1900 < year < 2100:
                            return str(year)
    except:
        pass
    
    return str(datetime.now().year)

def is_duplicate_reference(new_ref: dict) -> bool:
    """Check for duplicates safely"""
    if not isinstance(new_ref, dict):
        return False
    
    try:
        for existing in st.session_state.refs:
            if not isinstance(existing, dict):
                continue
            
            new_url = new_ref.get('url', '').lower().strip()
            existing_url = existing.get('url', '').lower().strip()
            
            if new_url and new_url == existing_url:
                return True
            
            new_title = str(new_ref.get('title', '')).lower().strip()
            existing_title = str(existing.get('title', '')).lower().strip()
            
            if new_title and len(new_title) > 10 and new_title == existing_title:
                return True
    except:
        pass
    
    return False

def format_citation(ref: dict, style: str, index: int) -> str:
    """Format citation safely"""
    if not isinstance(ref, dict) or not isinstance(style, str):
        return ""
    
    try:
        author = sanitize_string(str(ref.get('author', 'Anonim')))
        title = sanitize_string(str(ref.get('title', 'No Title')))
        year = sanitize_string(str(ref.get('year', '2026')))
        url = sanitize_string(str(ref.get('url', '')))
        
        if style == "Vancouver":
            return f"{index}. {author}. {title}. {year}. Available from: {url}"
        elif style == "APA 7th":
            return f"{author} ({year}). {title}. Retrieved from {url}"
        elif style == "IEEE":
            return f"[{index}] {author}, \"{title},\" {year}. [Online]. Available: {url}"
        elif style == "MLA":
            return f"{author}. \"{title}.\" {year}. Web. {url}."
        else:
            return f"{author} ({year}). {title}."
    except:
        return ""

def generate_bibliography(refs: list, style: str) -> str:
    """Generate bibliography safely"""
    if not isinstance(refs, list) or not isinstance(style, str):
        return ""
    
    try:
        output = f"{get_text('bibliography_title')} ({style})\n"
        output += "=" * 60 + "\n\n"
        
        for i, ref in enumerate(refs, 1):
            if not isinstance(ref, dict):
                continue
            cite = format_citation(ref, style, i)
            if cite:
                output += f"{cite}\n\n"
        
        return output
    except:
        return ""

# ==========================================
# 6. API FUNCTIONS (Security-Enhanced)
# ==========================================

def get_cite(query: str, is_doi: bool = False) -> Optional[dict]:
    """Fetch metadata from Crossref API safely"""
    if not isinstance(query, str) or not query.strip():
        st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
        return None
    
    query = sanitize_string(query, max_length=200)
    
    try:
        if is_doi:
            url = f"https://api.crossref.org/works/{quote(query, safe='')}"
        else:
            url = f"https://api.crossref.org/works?query={quote(query, safe='')}&rows=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'message' not in data:
            st.markdown(f'<div class="error-box">{get_text("error_parsing")}</div>', unsafe_allow_html=True)
            return None
        
        message = data['message']
        
        if is_doi:
            item = message
        else:
            if 'items' not in message or len(message['items']) == 0:
                st.markdown(f'<div class="error-box">{get_text("error_no_results")}</div>', unsafe_allow_html=True)
                return None
            item = message['items'][0]
        
        # Extract data safely
        title = None
        if 'title' in item:
            titles = item['title']
            if isinstance(titles, list) and len(titles) > 0:
                title = titles[0]
            elif isinstance(titles, str):
                title = titles
        
        title = sanitize_string(str(title or "No Title"), max_length=200)
        author = get_author_string(item)
        year = get_year(item)
        
        url_final = None
        if 'DOI' in item:
            url_final = f"https://doi.org/{sanitize_string(str(item['DOI']), max_length=100)}"
        elif 'URL' in item:
            url_final = sanitize_string(str(item['URL']), max_length=300)
        else:
            url_final = f"https://crossref.org/{sanitize_string(str(item.get('ID', 'unknown')), max_length=100)}"
        
        return {
            "title": title,
            "author": author,
            "year": year,
            "url": url_final,
            "source": "Crossref"
        }
    
    except requests.exceptions.Timeout:
        st.markdown(f'<div class="error-box">{get_text("error_timeout")}</div>', unsafe_allow_html=True)
        return None
    except requests.exceptions.ConnectionError:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
        return None
    except requests.exceptions.HTTPError:
        st.markdown(f'<div class="error-box">{get_text("error_connection")}</div>', unsafe_allow_html=True)
        return None
    except ValueError:
        st.markdown(f'<div class="error-box">{get_text("error_json")}</div>', unsafe_allow_html=True)
        return None
    except Exception:
        st.markdown(f'<div class="error-box">{get_text("error_parsing")}</div>', unsafe_allow_html=True)
        return None

def process_pdf(file_bytes: bytes, filename: str) -> Optional[dict]:
    """Process PDF safely"""
    if fitz is None:
        st.markdown(f'<div class="error-box">{get_text("error_pymupdf")}</div>', unsafe_allow_html=True)
        return None
    
    try:
        if not isinstance(file_bytes, bytes):
            return None
        
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        
        for i in range(min(len(doc), 3)):
            try:
                text += doc[i].get_text()
            except:
                pass
        
        doi = extract_doi_from_text(text)
        
        if doi and is_valid_doi(doi):
            result = get_cite(doi, is_doi=True)
            if result:
                result["source"] = "PDF + Crossref"
                return result
        
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        
        return {
            "title": sanitize_string(lines[0] if lines else filename, max_length=200),
            "author": "PDF Document",
            "year": str(datetime.now().year),
            "url": sanitize_string(filename, max_length=100),
            "source": "PDF Text"
        }
    
    except Exception:
        st.markdown(f'<div class="error-box">{get_text("error_pdf")}</div>', unsafe_allow_html=True)
        return None

# ==========================================
# 7. SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown(f'<p class="sidebar-brand">{get_text("sidebar_brand")}</p>', unsafe_allow_html=True)
    st.caption(get_text("sidebar_caption"))
    st.divider()
    
    # Language Selection
    lang_cols = st.columns(2)
    if lang_cols[0].button("🇹🇷 TR", use_container_width=True):
        st.session_state.lang = "TR"
        st.rerun()
    if lang_cols[1].button("🇺🇸 EN", use_container_width=True):
        st.session_state.lang = "EN"
        st.rerun()
    
    st.divider()
    
    # Navigation
    selection = st.radio(
        get_text("menu_label"),
        ["citation_engine", "services"],
        format_func=lambda x: get_text("menu_citation_engine") if x == "citation_engine" else get_text("menu_services"),
        label_visibility="collapsed"
    )
    st.session_state.page = selection
    
    st.divider()
    
    # Contact Section
    st.markdown(f"""
        <div class="contact-container">
            <p style="color: #34d399; font-weight: bold; margin-bottom: 5px; font-size: 17px;">{get_text("contact_title")}</p>
            <p style="color: #94a3b8; font-size: 13px;">{get_text("contact_desc")}</p>
            <a href="mailto:{MY_EMAIL}" class="contact-btn">{get_text("contact_btn")}</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown(f"© 2026 **Lifegenix Danişmanlık**<br>{get_text('copyright')}", unsafe_allow_html=True)

# ==========================================
# 8. PAGE CONTENT
# ==========================================

if st.session_state.page == "citation_engine":
    st.markdown('<p class="main-title">Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{get_text("app_subtitle")}</p>', unsafe_allow_html=True)
    
    # Information Box
    st.markdown(f"""
        <div class="info-box">
            <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
                {get_text("info_text")}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Format Selection
    style = st.selectbox(
        get_text("format_label"),
        ["Vancouver", "APA 7th", "IEEE", "MLA"],
        index=0
    )
    
    # Tabs for input methods
    t1, t2, t3 = st.tabs([get_text("tab_doi"), get_text("tab_search"), get_text("tab_pdf")])
    
    with t1:
        st.subheader(get_text("tab_doi"))
        doi_in = st.text_input(get_text("doi_label"), placeholder=get_text("doi_placeholder"), key="doi_input")
        
        col_doi1, col_doi2 = st.columns(2)
        with col_doi1:
            if st.button(get_text("doi_button"), key="btn_doi", use_container_width=True):
                if not doi_in.strip():
                    st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
                elif not is_valid_doi(doi_in):
                    st.markdown(f'<div class="error-box">{get_text("error_invalid_doi")}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner(get_text("searching")):
                        res = get_cite(doi_in, is_doi=True)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown(f'<div class="warning-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t2:
        st.subheader(get_text("tab_search"))
        q_in = st.text_input(get_text("search_label"), placeholder=get_text("search_placeholder"), key="query_input")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button(get_text("search_button"), key="btn_q", use_container_width=True):
                if not q_in.strip():
                    st.markdown(f'<div class="error-box">{get_text("error_empty_input")}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner(get_text("searching")):
                        res = get_cite(q_in, is_doi=False)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown(f'<div class="warning-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t3:
        st.subheader(get_text("tab_pdf"))
        pdf_file = st.file_uploader(get_text("pdf_label"), type="pdf", help=get_text("pdf_help"))
        
        if pdf_file:
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                if st.button(get_text("pdf_button"), key="btn_pdf", use_container_width=True):
                    with st.spinner(get_text("reading")):
                        res = process_pdf(pdf_file.read(), pdf_file.name)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown(f'<div class="warning-box">{get_text("warning_duplicate")}</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown(f'<div class="success-box">{get_text("success_added")}</div>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.markdown(f'<div class="error-box">{get_text("error_no_doi")}</div>', unsafe_allow_html=True)
    
    # Bibliography Output
    if len(st.session_state.refs) > 0:
        st.divider()
        st.subheader(get_text("bibliography_title"))
        
        # Display bibliography
        bibliography = generate_bibliography(st.session_state.refs, style)
        st.text_area(get_text("bibliography_label"), value=bibliography, height=300, disabled=True, key="bib_output")
        
        # Download and action buttons
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.download_button(
                label=get_text("download_button"),
                data=bibliography,
                file_name=f"kaynakca_{style.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_d2:
            if st.button(get_text("copy_button"), use_container_width=True):
                st.markdown(f'<div class="success-box">{get_text("warning_copied")}</div>', unsafe_allow_html=True)
        
        with col_d3:
            if st.button(get_text("clear_button"), use_container_width=True):
                if st.button(get_text("confirm_delete"), key="confirm_delete"):
                    st.session_state.refs = []
                    st.markdown(f'<div class="success-box">{get_text("warning_cleared")}</div>', unsafe_allow_html=True)
                    st.rerun()
        
        # Display source list
        st.subheader(f"{get_text('sources_title')} ({len(st.session_state.refs)})")
        
        for idx, ref in enumerate(st.session_state.refs, 1):
            col_ref1, col_ref2 = st.columns([4, 1])
            
            with col_ref1:
                st.markdown(f"""
                    **#{idx}** - {ref.get('author', 'Anonim')} ({ref.get('year', '2026')})
                    
                    {ref.get('title', 'No Title')[:100]}...
                    
                    *{ref.get('source', 'Source')}*
                """)
            
            with col_ref2:
                if st.button(get_text("delete_source"), key=f"del_{idx}", use_container_width=True):
                    st.session_state.refs.pop(idx - 1)
                    st.rerun()
    
    # FAQ Section
    st.divider()
    col_faq1, col_faq2 = st.columns(2)
    
    with col_faq1:
        st.markdown(f"### {get_text('faq_title')}")
        with st.expander(get_text("faq_doi")):
            st.write(get_text("faq_doi_ans"))
        with st.expander(get_text("faq_formats")):
            st.write(get_text("faq_formats_ans"))
        with st.expander(get_text("faq_pdf")):
            st.write(get_text("faq_pdf_ans"))
    
    with col_faq2:
        st.markdown(f"### {get_text('why_title')}")
        st.markdown(f"* {get_text('why_speed')}")
        st.markdown(f"* {get_text('why_accuracy')}")
        st.markdown(f"* {get_text('why_free')}")
        st.markdown(f"* {get_text('why_auto')}")
        st.markdown(f"* {get_text('why_secure')}")

elif st.session_state.page == "services":
    st.markdown(f'<p class="main-title">{get_text("services_title")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{get_text("services_subtitle")}</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="service-card">
            <h3>{get_text("service_genetic")}</h3>
            <p>{get_text("service_genetic_desc")}</p>
            <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">NCBI</span>
        </div>
        <div class="service-card">
            <h3>{get_text("service_ml")}</h3>
            <p>{get_text("service_ml_desc")}</p>
            <span class="feature-tag">Python</span><span class="feature-tag">ML / AI</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="service-card">
            <h3>{get_text("service_bigdata")}</h3>
            <p>{get_text("service_bigdata_desc")}</p>
            <span class="feature-tag">Big Data</span><span class="feature-tag">Python</span>
        </div>
        <div class="service-card">
            <h3>{get_text("service_editorial")}</h3>
            <p>{get_text("service_editorial_desc")}</p>
            <span class="feature-tag">Editorial Review</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 9. FOOTER
# ==========================================

st.markdown(f'<div class="footer">{get_text("copyright")}</div>', unsafe_allow_html=True)
