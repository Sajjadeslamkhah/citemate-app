import streamlit as st
import requests
import fitz  # PyMuPDF
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Citemate AI Engine v8.2", page_icon="🧬", layout="wide")

# 2. GÖRSEL AYARLAR (Yüksek Kontrast ve Okunabilirlik)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .stTextInput input { color: #ffffff !important; background-color: #262730 !important; }
    .cite-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #34d399; margin-bottom: 10px; }
    code { color: #10b981 !important; font-size: 14px; white-space: pre-wrap !important; }
    .stAlert { background-color: #1a1a1a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'refs' not in st.session_state: st.session_state.refs = []

# 3. AKADEMİK VERİ ÇEKME MOTORU (DOI ÖNCELİKLİ)
def fetch_from_crossref(doi):
    """DOI üzerinden Crossref API kullanarak %100 doğru veri çeker."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()['message']
            title = data.get('title', ['Başlık Bulunamadı'])[0]
            authors = data.get('author', [])
            author_str = authors[0].get('family', 'Anonim') if authors else "Anonim"
            # Tarih verisini güvenli çekme
            try:
                year = data.get('created', {}).get('date-parts', [[datetime.now().year]])[0][0]
            except:
                year = datetime.now().year
            return title, author_str, year
    except: return None
    return None

def process_input(input_data):
    """Girdinin içinden DOI ayıklar veya Web Meta verisini dener."""
    # DOI Regex (Linkin içinde olsa bile yakalar)
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    doi_match = re.search(doi_pattern, input_data, re.I)
    
    if doi_match:
        doi = doi_match.group().strip("/")
        api_data = fetch_from_crossref(doi)
        if api_data:
            return api_data[0], api_data[1], api_data[2], f"https://doi.org/{doi}"

    # DOI bulunamazsa Web Scraping dene
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(input_data, timeout=10, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = (soup.find("meta", attrs={"name": "citation_title"}) or soup.find("meta", property="og:title") or soup.title)
        title_text = title["content"] if hasattr(title, "content") else (title.string if title else "Bilinmeyen Başlık")
        return title_text.strip(), "Web Kaynağı", datetime.now().year, input_data
    except:
        return "Teşhis Edilemedi (Lütfen DOI kullanın)", "Manuel", 2026, input_data

def process_pdf(file_bytes, filename):
    """PDF içinden DOI ayıklayıp API'ye sorar."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = doc[0].get_text() + doc[1].get_text() if len(doc) > 1 else doc[0].get_text()
        doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
        
        if doi_match:
            doi = doi_match.group().strip("/")
            api_data = fetch_from_crossref(doi)
            if api_data: return api_data[0], api_data[1], api_data[2], f"DOI: {doi}"
        
        # DOI yoksa dosya adını kullan
        return filename.replace(".pdf", ""), "PDF Dosyası", datetime.now().year, filename
    except:
        return filename, "Hata", 2026, filename

# 4. ARAYÜZ TASARIMI
st.title("🧬 Citemate AI Engine v8.2")
st.markdown("### Akıllı DOI ve Link Teşhis İstasyonu")

st.info("💡 **Akademik İpucu:** En kesin sonuç için makalenin **DOI numarasını** veya DOI içeren tam linkini kullanın.")

# Format Seçimi
style = st.selectbox("Format Seçin:", ["Vancouver", "APA 7th", "IEEE", "MLA 9th", "Harvard"])

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.header("📥 Kaynak Yükle")
    t_link, t_pdf = st.tabs(["🔗 DOI veya Link", "📄 PDF Dosyası"])
    
    with t_link:
        url_in = st.text_input("Makale DOI veya URL:", placeholder="Örn: 10.1016/j.oto...")
        if st.button("Kaynağı Teşhis Et", key="link_btn"):
            if url_in:
                with st.spinner('Analiz ediliyor...'):
                    t, a, y, final_url = process_input(url_in)
                    st.session_state.refs.append({"title": t, "author": a, "year": y, "url": final_url})
                    st.success(f"Teşhis Edildi: {t[:50]}...")

    with t_pdf:
        pdf_file = st.file_uploader("PDF Sürükleyin", type="pdf")
        if pdf_file and st.button("PDF'i Çözümle"):
            with st.spinner('PDF Okunuyor...'):
                t, a, y, src = process_pdf(pdf_file.read(), pdf_file.name)
                st.session_state.refs.append({"title": t, "author": a, "year": y, "url": src})
                st.success(f"PDF Teşhis Edildi: {t[:50]}...")

with col_out:
    st.header("📋 Profesyonel Çıktı")
    full_bib = ""
    
    if st.session_state.refs:
        for i, r in enumerate(st.session_state.refs, 1):
            # Formatlama Mantığı
            if style == "Vancouver":
                cite = f"{i}. {r['author']}. {r['title']}. ({r['year']}). {r['url']}"
            elif style == "APA 7th":
                cite = f"{r['author']} ({r['year']}). {r['title']}. {r['url']}"
            else: # IEEE
                cite = f"[{i}] {r['author']}, \"{r['title']}\", {r['year']}. [Online]. Available: {r['url']}"
            
            st.code(cite, language="text")
            full_bib += cite + "\n\n"
        
        st.divider()
        st.download_button("⬇️ Tüm Kaynakçayı İndir (TXT)", data=full_bib, file_name="kaynakca.txt", use_container_width=True)
        if st.button("🗑️ Tümünü Temizle", use_container_width=True):
            st.session_state.refs = []
            st.rerun()
    else:
        st.info("Henüz kaynak eklenmedi.")

# NASIL KULLANILIR
with st.expander("ℹ️ Detaylı Rehber"):
    st.write("""
    - **DOI Nedir?** Makalelerin 10. ile başlayan dijital kimlik numarasıdır. En güvenilir sonuçları verir.
    - **ScienceDirect/TheClinics:** Bu sitelerden link kopyaladığınızda sistem DOI'yi linkin içinden otomatik bulur.
    - **PDF Analizi:** PDF yüklediğinizde sistem ilk iki sayfayı tarayıp makalenin gerçek kimliğini bulmaya çalışır.
    """)
