import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Citemate Engine v5", page_icon="📚", layout="wide")

# 2. RENK VE TEMA DÜZELTMESİ (Her temada okunabilir)
st.markdown("""
    <style>
    /* Başlıklar ve metinler için net renkler */
    h1, h2, h3, p, span { color: #ffffff !important; }
    .stTabs [data-baseweb="tab-list"] button { color: white; font-size: 18px; }
    .cite-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #4CAF50;
        margin-bottom: 15px;
    }
    .instruction-box { background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 5px solid #ff4b4b; }
    code { color: #ffbd45 !important; background-color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. HAFIZA YÖNETİMİ
if 'references' not in st.session_state: st.session_state.references = []

# 4. YARDIMCI FONKSİYONLAR
def get_title(url):
    try:
        res = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.title.string.strip() if soup.title else url
    except: return url

def add_multiple_sources(input_str, source_type):
    urls = [u.strip() for u in input_str.split('\n') if u.strip()]
    added_count = 0
    for u in urls:
        # Mükerrer Kontrolü
        if not any(r['url'] == u for r in st.session_state.references):
            title = get_title(u)
            st.session_state.references.append({
                "url": u, "title": title, "type": source_type,
                "year": datetime.now().year, "access": datetime.now().strftime("%d.%m.%Y")
            })
            added_count += 1
    return added_count

# 5. ARAYÜZ
st.title("📚 Citemate v5.0")
st.subheader("Akademik Kaynak ve Atıf Dönüştürücü")

# NASIL KULLANILIR SEKİSİ
with st.expander("❓ Nasıl Kullanılır? (Rehber)"):
    st.markdown("""
    1. **Format Seçin:** En üstteki menüden hedef formatınızı belirleyin.
    2. **Kaynak Ekleyin:** Linkleri veya PDF bağlantılarını ilgili sekmeye **alt alta** yapıştırın.
    3. **Toplu İşlem:** 'Hepsini İşle' butonuna basın, sistem mükerrer olanları ayıklar.
    4. **Sonuçları Alın:** Her kaynağın altında hem **Metin İçi (In-text)** hem de **Kaynakça (Bibliography)** halini göreceksiniz.
    """)

# FORMAT VE TÜR SEÇİMİ
sel_format = st.selectbox("Hedef Akademik Format:", ["Vancouver", "APA 7th", "Harvard", "MLA"])

tab1, tab2 = st.tabs(["🔗 Web Linkleri Ekle", "📄 PDF Bağlantıları Ekle"])

with tab1:
    urls_input = st.text_area("Web linklerini her satıra bir tane gelecek şekilde yapıştırın:", height=150)
    if st.button("Linkleri Toplu İşle", type="primary"):
        count = add_multiple_sources(urls_input, "Web")
        st.success(f"{count} yeni web kaynağı eklendi!")

with tab2:
    pdf_input = st.text_area("PDF (DOI/Direct) linklerini alt alta yapıştırın:", height=150)
    if st.button("PDF'leri Toplu İşle", type="primary"):
        count = add_multiple_sources(pdf_input, "PDF")
        st.success(f"{count} yeni PDF kaynağı eklendi!")

st.divider()

# 6. SONUÇLAR: METİN İÇİ VE KAYNAKÇA
st.header("📋 Dönüştürülmüş Kaynaklar")

if st.session_state.references:
    for idx, ref in enumerate(st.session_state.references, 1):
        with st.container():
            st.markdown(f"### Kaynak #{idx} ({ref['type']})")
            
            # Format Mantığı
            if sel_format == "Vancouver":
                in_text = f"({idx})"
                bib = f"{idx}. {ref['title']}. Available at: {ref['url']} (Accessed: {ref['access']})"
            else: # APA Örneği
                in_text = f"(Anon, {ref['year']})"
                bib = f"{ref['title']}. ({ref['year']}). Retrieved from {ref['url']}"

            # GÖRSEL KARTLAR
            col_a, col_b = st.columns(2)
            with col_a:
                st.info("**Metin İçinde Yazımı:**")
                st.code(in_text, language="text")
            with col_b:
                st.success("**Kaynakça Yazımı:**")
                st.code(bib, language="text")
            st.divider()

    if st.button("🗑️ Tüm Listeyi Temizle"):
        st.session_state.references = []
        st.rerun()
else:
    st.info("Henüz kaynak eklenmedi. Linkleri yukarıdaki alanlara yapıştırıp 'İşle' butonuna basın.")
