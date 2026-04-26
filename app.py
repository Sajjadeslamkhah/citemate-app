import streamlit as st
import requests
import re
from datetime import datetime
import os

# Safely import PyMuPDF
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(
    page_title="Citemate Pro | Elite Citation Intelligence",
    page_icon="🎓",
    layout="wide"
)

def add_seo_safe():
    """Add safe SEO meta tags without XSS risk"""
    meta = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Citemate Pro: Akademik atif yonetimi ve kaynakca duzenleme">
    <meta name="keywords" content="atif, kaynakca, vancouver, apa, ieee, mla, akademik">
    """
    st.components.v1.html(meta, height=0)

add_seo_safe()

# ==========================================
# 2. HAFIZA BASLATMA (SESSION STATE)
# ==========================================
def init_session_state():
    """Initialize all session state variables"""
    if 'refs' not in st.session_state:
        st.session_state.refs = []
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Atif Motoru"
    if 'lang' not in st.session_state:
        st.session_state.lang = "Türkçe"
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

init_session_state()

# ==========================================
# 3. TASARIM VE KURUMSAL KİMLİK
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
# 4. YARDIMCI FONKSIYONLAR
# ==========================================

def is_valid_doi(doi_str: str) -> bool:
    """Validate DOI format"""
    doi_pattern = r'^10\.\d{4,}/[^\s]+$'
    return bool(re.match(doi_pattern, doi_str.strip()))

def extract_doi_from_text(text: str) -> str:
    """Extract DOI from text"""
    doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', text, re.I)
    return doi_match.group().strip("/") if doi_match else None

def get_author_string(item: dict) -> str:
    """Extract author name properly from Crossref data"""
    try:
        authors = item.get('author', [])
        if not authors:
            return "Anonim"
        
        author1 = authors[0]
        first_name = author1.get('family') or author1.get('literal', 'Anonim')
        
        if len(authors) > 1:
            return f"{first_name} et al."
        
        return first_name
    except:
        return "Anonim"

def get_year(item: dict) -> str:
    """Extract publication year from Crossref item"""
    try:
        for key in ['published-online', 'published-print', 'created', 'issued']:
            if key in item and isinstance(item[key], dict):
                date_parts = item[key].get('date-parts')
                if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
                    year = date_parts[0][0]
                    if isinstance(year, int) and 1900 < year < 2100:
                        return str(year)
    except:
        pass
    
    return str(datetime.now().year)

def is_duplicate_reference(new_ref: dict) -> bool:
    """Check if reference already exists"""
    for existing in st.session_state.refs:
        # Check by URL
        if new_ref.get('url') and existing.get('url'):
            if new_ref['url'].lower() == existing['url'].lower():
                return True
        
        # Check by title
        if new_ref.get('title') and existing.get('title'):
            if new_ref['title'].lower() == existing['title'].lower():
                return True
    
    return False

def format_citation(ref: dict, style: str, index: int) -> str:
    """Format citation in selected style"""
    author = ref.get('author', 'Anonim')
    title = ref.get('title', 'Baslik Yok')
    year = ref.get('year', '2026')
    url = ref.get('url', '')
    
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

def generate_bibliography(refs: list, style: str) -> str:
    """Generate complete bibliography"""
    output = f"KAYNAKÇA / BIBLIOGRAPHY ({style})\n"
    output += "=" * 60 + "\n\n"
    
    for i, ref in enumerate(refs, 1):
        cite = format_citation(ref, style, i)
        output += f"{cite}\n\n"
    
    return output

# ==========================================
# 5. MOTOR FONKSİYONLARI
# ==========================================

def get_cite(query: str, is_doi: bool = False) -> dict:
    """
    Fetch metadata from Crossref API
    FIXED: Proper DOI/Query parsing, error handling
    """
    try:
        if is_doi:
            url = f"https://api.crossref.org/works/{query}"
        else:
            url = f"https://api.crossref.org/works?query={query}&rows=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'message' not in data:
            st.markdown('<div class="error-box">API yanit formati hatalı</div>', unsafe_allow_html=True)
            return None
        
        message = data['message']
        
        # Handle DOI vs Query response structure
        if is_doi:
            item = message  # Direct item for DOI
        else:
            if 'items' not in message or len(message['items']) == 0:
                st.markdown('<div class="error-box">Sonuç bulunamadi</div>', unsafe_allow_html=True)
                return None
            item = message['items'][0]
        
        # Extract title
        title = None
        if 'title' in item:
            titles = item['title']
            title = titles[0] if isinstance(titles, list) and len(titles) > 0 else titles
        
        if not title:
            title = "Baslik Bulunamadi"
        
        # Get author - FIXED
        author = get_author_string(item)
        
        # Get year - FIXED
        year = get_year(item)
        
        # Get DOI or URL
        url_final = None
        if 'DOI' in item:
            url_final = f"https://doi.org/{item['DOI']}"
        elif 'URL' in item:
            url_final = item['URL']
        else:
            url_final = f"https://crossref.org/{item.get('ID', 'unknown')}"
        
        return {
            "title": title[:200],
            "author": author,
            "year": year,
            "url": url_final,
            "source": "Crossref"
        }
    
    except requests.exceptions.Timeout:
        st.markdown('<div class="error-box">Istek timeout oldu (10s)</div>', unsafe_allow_html=True)
        return None
    
    except requests.exceptions.ConnectionError:
        st.markdown('<div class="error-box">Baglanti hatasi - interneti kontrol edin</div>', unsafe_allow_html=True)
        return None
    
    except requests.exceptions.HTTPError as e:
        st.markdown(f'<div class="error-box">HTTP Hatasi: {e.response.status_code}</div>', unsafe_allow_html=True)
        return None
    
    except ValueError:
        st.markdown('<div class="error-box">JSON ayristirma hatasi</div>', unsafe_allow_html=True)
        return None
    
    except KeyError as e:
        st.markdown(f'<div class="error-box">Veri ayristirma hatasi: {str(e)}</div>', unsafe_allow_html=True)
        return None
    
    except Exception as e:
        st.markdown(f'<div class="error-box">Beklenmeyen hata: {str(e)[:100]}</div>', unsafe_allow_html=True)
        return None

def process_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Process PDF file and extract metadata
    FIXED: PyMuPDF check, better error handling
    """
    if fitz is None:
        st.markdown('<div class="error-box">PyMuPDF yuklü degil. Calistirin: pip install pymupdf</div>', unsafe_allow_html=True)
        return None
    
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Extract text from first 3 pages
        text = ""
        for i in range(min(len(doc), 3)):
            try:
                text += doc[i].get_text()
            except:
                pass
        
        # Try to find DOI
        doi = extract_doi_from_text(text)
        
        if doi:
            # Found DOI, fetch from Crossref
            result = get_cite(doi, is_doi=True)
            if result:
                result["source"] = "PDF + Crossref"
                return result
        
        # If no DOI found, extract title from text
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 15]
        
        return {
            "title": lines[0][:200] if lines else filename,
            "author": "PDF Dokuman",
            "year": str(datetime.now().year),
            "url": filename,
            "source": "PDF Text"
        }
    
    except Exception as e:
        st.markdown(f'<div class="error-box">PDF isleme hatasi: {str(e)[:100]}</div>', unsafe_allow_html=True)
        return None

# ==========================================
# 6. YAN MENÜ (NAVİGASYON & İLETİŞİM)
# ==========================================
with st.sidebar:
    st.markdown('<p class="sidebar-brand">Citemate Pro</p>', unsafe_allow_html=True)
    st.caption("Elite Academic Solutions | Powered by Lifegenix")
    st.divider()
    
    # Language Selection
    lang_cols = st.columns(2)
    if lang_cols[0].button("TR", use_container_width=True):
        st.session_state.lang = "Türkçe"
        st.rerun()
    if lang_cols[1].button("EN", use_container_width=True):
        st.session_state.lang = "English"
        st.rerun()
    
    st.divider()
    
    # Navigation
    selection = st.radio(
        "Menu",
        ["🏠 Atif Motoru", "💎 Profesyonel Hizmetler"],
        label_visibility="collapsed"
    )
    st.session_state.page = selection
    
    st.divider()
    
    # Contact Section
    c_title = "📩 Bize Ulasin" if st.session_state.lang == "Türkçe" else "📩 Contact Us"
    c_desc = "Akademik islbrligi ve kurumsal analiz teklifleri icin ulasin." if st.session_state.lang == "Türkçe" else "Reach out for collaboration and analysis."
    c_btn = "Mesaj Gönder" if st.session_state.lang == "Türkçe" else "Send Message"
    
    st.markdown(f"""
        <div class="contact-container">
            <p style="color: #34d399; font-weight: bold; margin-bottom: 5px; font-size: 17px;">{c_title}</p>
            <p style="color: #94a3b8; font-size: 13px;">{c_desc}</p>
            <a href="mailto:{MY_EMAIL}" class="contact-btn">{c_btn}</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("© 2026 **Lifegenix Danismanlik**<br>Tum haklari saklıdır.", unsafe_allow_html=True)

# ==========================================
# 7. SAYFA İÇERİKLERİ
# ==========================================

if st.session_state.page == "🏠 Atif Motoru":
    st.markdown('<p class="main-title">Citemate Pro</p>', unsafe_allow_html=True)
    
    sub_title_text = "Akademik Mukemmeliyet Icin Kusursuz Atif Yonetimi" if st.session_state.lang == "Türkçe" else "Seamless Citation Management for Academic Excellence"
    st.markdown(f'<p class="sub-title">{sub_title_text}</p>', unsafe_allow_html=True)
    
    # Information Box
    st.markdown("""
        <div class="info-box">
            <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
                <b>Citemate Pro</b>, arastirmacilarin ve ogrencilerin kaynakca hazirlama yükünü hafifletmek icin tasarlandi, 
                yapay zeka destekli bir <b>atif düzenleme motorudur.</b> DOI numarası, yayin basligı veya dogrudan PDF dosyanizi 
                kullanarak saniyeler icinde hatasiz; Vancouver, APA, IEEE ve MLA formatlarinda profesyonel referanslar olusturur.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Format Selection
    style = st.selectbox(
        "Tercih Edilen Standard / Preferred Style:",
        ["Vancouver", "APA 7th", "IEEE", "MLA"],
        index=0
    )
    
    # Tabs for input methods
    t1, t2, t3 = st.tabs(["DOI Entegrasyonu", "Global Arama", "Akilli PDF Analizi"])
    
    with t1:
        st.subheader("DOI ile Kaynak Ekle")
        doi_in = st.text_input(
            "DOI Numarası:",
            placeholder="10.1016/j.cell...",
            key="doi_input"
        )
        
        col_doi1, col_doi2 = st.columns(2)
        with col_doi1:
            if st.button("Kaynagi Isle", key="btn_doi", use_container_width=True):
                if not doi_in.strip():
                    st.markdown('<div class="error-box">Lütfen bir DOI girin</div>', unsafe_allow_html=True)
                elif not is_valid_doi(doi_in):
                    st.markdown('<div class="error-box">Gecersiz DOI formatı. Örnek: 10.1016/j.cell...</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Aranıyor..."):
                        res = get_cite(doi_in, is_doi=True)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown('<div class="warning-box">Bu kaynak zaten eklendi!</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown('<div class="success-box">Kaynak basarıyla eklendi!</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t2:
        st.subheader("Baslik ile Arama")
        q_in = st.text_input(
            "Yayin Basligı:",
            placeholder="Tam basligı giriniz...",
            key="query_input"
        )
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Veritabanında Ara", key="btn_q", use_container_width=True):
                if not q_in.strip():
                    st.markdown('<div class="error-box">Lütfen bir baslik girin</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Aranıyor..."):
                        res = get_cite(q_in, is_doi=False)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown('<div class="warning-box">Bu kaynak zaten eklendi!</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown('<div class="success-box">Kaynak basarıyla eklendi!</div>', unsafe_allow_html=True)
                                st.rerun()
    
    with t3:
        st.subheader("PDF Analizi")
        pdf_file = st.file_uploader(
            "PDF Yükle",
            type="pdf",
            help="PDF'den otomatik olarak DOI çıkarılır"
        )
        
        if pdf_file:
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                if st.button("Metadatalari Çözümle", key="btn_pdf", use_container_width=True):
                    with st.spinner("Okunuyor..."):
                        res = process_pdf(pdf_file.read(), pdf_file.name)
                        if res:
                            if is_duplicate_reference(res):
                                st.markdown('<div class="warning-box">Bu kaynak zaten eklendi!</div>', unsafe_allow_html=True)
                            else:
                                st.session_state.refs.append(res)
                                st.markdown('<div class="success-box">Kaynak basarıyla eklendi!</div>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.markdown('<div class="error-box">Dosyada DOI tanımlayıcı bulunamadı</div>', unsafe_allow_html=True)
    
    # Bibliography Output
    if len(st.session_state.refs) > 0:
        st.divider()
        st.subheader("Kaynakça Çikti")
        
        # Display bibliography
        bibliography = generate_bibliography(st.session_state.refs, style)
        st.text_area(
            "Kaynakça (İndir veya Kopyala):",
            value=bibliography,
            height=300,
            disabled=True,
            key="bib_output"
        )
        
        # Download button
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.download_button(
                label="Kaynakçayı Indir",
                data=bibliography,
                file_name=f"kaynakca_{style.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_d2:
            if st.button("Kopyala (Ctrl+C)", use_container_width=True):
                st.markdown('<div class="success-box">Metin kopyalandı! Ctrl+V ile yapistir</div>', unsafe_allow_html=True)
        
        with col_d3:
            if st.button("Tüm Kayitlari Temizle", use_container_width=True):
                if st.button("Eminiz?", key="confirm_delete"):
                    st.session_state.refs = []
                    st.markdown('<div class="success-box">Tüm kaynaklar silindi</div>', unsafe_allow_html=True)
                    st.rerun()
        
        # Display source list
        st.subheader(f"Eklenen Kaynaklar ({len(st.session_state.refs)})")
        
        for idx, ref in enumerate(st.session_state.refs, 1):
            col_ref1, col_ref2 = st.columns([4, 1])
            
            with col_ref1:
                st.markdown(f"""
                    **#{idx}** - {ref['author']} ({ref['year']})
                    
                    {ref['title'][:100]}...
                    
                    *Kaynak: {ref['source']}*
                """)
            
            with col_ref2:
                if st.button("Sil", key=f"del_{idx}", use_container_width=True):
                    st.session_state.refs.pop(idx - 1)
                    st.rerun()
    
    # FAQ Section
    st.divider()
    col_faq1, col_faq2 = st.columns(2)
    
    with col_faq1:
        st.markdown("### Sık Sorulan Sorular")
        with st.expander("DOI Nedir?"):
            st.write("Dijital Nesne Tanımlayıcısı (DOI), makalelerin internetteki kalıcı kimliğidir. 10.xxxx/xxx formatındadır.")
        with st.expander("Hangi formatlar destekleniyor?"):
            st.write("Vancouver, APA 7, IEEE ve MLA standartlarını tam uyumlu destekliyoruz.")
        with st.expander("PDF dosyalarından nasıl veri çıkarılıyor?"):
            st.write("PDF'den DOI otomatik olarak çıkarılır ve Crossref veritabanından metadata alınır.")
    
    with col_faq2:
        st.markdown("### Neden Citemate Pro?")
        st.markdown("""
        - **Hiz:** DOI ile saniyeler içinde atif
        - **Dogruluk:** Global Crossref veritabanı ile senkronize
        - **Ücretsiz:** Arastirmacılar için tamamen ücretsiz
        - **Otomatik:** Formatlama tamamen otomatik
        - **Güvenli:** Verileriniz gizli kalır
        """)

elif st.session_state.page == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danismanlik: Veriden Yayin Stratejik Çözümler</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="service-card">
            <h3>Genetik Veri Analizi</h3>
            <p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve fenotip-genotip ilişkilendirmesi.</p>
            <span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span><span class="feature-tag">NCBI</span>
        </div>
        <div class="service-card">
            <h3>Saglikta Makine Ogrenmesi</h3>
            <p>Klinik ve omik veriler kullanılarak geliştirilen hastalık tahmin, sınıflandırma ve yapay zeka modelleri.</p>
            <span class="feature-tag">Python</span><span class="feature-tag">ML / AI</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="service-card">
            <h3>Büyük Veri Analitiği</h3>
            <p>Büyük ölçekli akademik verilerin Python tabanlı ileri istatistiksel raporlanması ve görselleştirilmesi.</p>
            <span class="feature-tag">Big Data</span><span class="feature-tag">Python</span>
        </div>
        <div class="service-card">
            <h3>Referans Yazımı & Editoryal</h3>
            <p>Karmaşık yayınların referans yönetiminin Lifegenix uzmanlığıyla yüksek standartta düzenlenmesi.</p>
            <span class="feature-tag">Editorial Review</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 8. FOOTER
# ==========================================
st.markdown('<div class="footer">© 2026 Lifegenix Danismanlik tarafından kurulmustur. Akademik dürüstlük ve teknolojik üstünlük ilkesiyle.</div>', unsafe_allow_html=True)
