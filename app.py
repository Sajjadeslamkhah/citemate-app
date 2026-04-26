import streamlit as st
import requests
import re
from datetime import datetime
import fitz  # PyMuPDF

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Academic Citation Engine", page_icon="🎓", layout="wide")

def add_seo():
    ga_id = "G-90YJBXFY8W" 
    meta_tags = """
        <meta name="description" content="Citemate Pro: Uluslararası akademik standartlarda (NLM, APA, IEEE) profesyonel atıf düzenleme motoru.">
        <meta name="keywords" content="vancouver style nlm, apa 7th manual, ieee citation, mendeley endnote export, tcga geo data analysis">
    """
    st.components.v1.html(f"{meta_tags}<script async src='https://www.googletagmanager.com/gtag/js?id={ga_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga_id}');</script>", height=0)

add_seo()

# ==========================================
# 2. HAFIZA & TASARIM (CSS)
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 62px !important; font-weight: 900 !important; color: #34d399; text-shadow: 0px 0px 25px rgba(52, 211, 153, 0.4); margin-bottom: 0px; }}
    .sub-title {{ color: #f8fafc; font-size: 22px; margin-bottom: 45px; font-weight: 300; }}
    .info-box {{ background-color: rgba(52, 211, 153, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin-bottom: 35px; }}
    .service-card {{ background: #161b22; padding: 25px; border-radius: 15px; border-top: 4px solid #34d399; margin-bottom: 20px; transition: 0.3s; min-height: 180px; }}
    .service-card:hover {{ transform: translateY(-5px); border-color: #10b981; }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 6px; text-transform: uppercase; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 80px; padding: 25px; border-top: 1px solid #1e293b; }}
    .sidebar-brand {{ font-size: 26px !important; font-weight: bold; color: #34d399; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. YAN MENÜ (NAVİGASYON)
# ==========================================
with st.sidebar:
    st.markdown('<p class="sidebar-brand">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.caption("Elite Academic Solutions | Powered by Lifegenix")
    st.divider()
    
    # Dil Butonları
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"
    if c2.button("🇺🇸 EN"): st.session_state.lang = "English"
    
    st.divider()
    page_selection = st.radio("SİSTEM MENÜSÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    
    st.divider()
    st.markdown(f"""
        <div style="background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155;">
            <p style="color: #34d399; font-weight: bold; margin-bottom: 5px;">📩 Bize Ulaşın</p>
            <p style="color: #94a3b8; font-size: 12px;">Akademik analiz ve iş birliği talepleri için:</p>
            <a href="mailto:{MY_EMAIL}" style="display: block; background: #34d399; color: black; text-align: center; padding: 10px; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 10px;">Mesaj Gönder</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. BİLİMSEL FORMATLAMA MOTORU
# ==========================================
def fetch_metadata(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        
        # Yazar formatlama (Surname I.)
        authors = item.get('author', [])
        formatted_authors = []
        for a in authors[:6]: # İlk 6 yazarı al (Akademik standart)
            formatted_authors.append(f"{a.get('family', '')} {a.get('given', '')[:1]}")
        author_str = ", ".join(formatted_authors)
        if len(authors) > 6: author_str += " et al"
        
        return {
            "title": item.get('title', ['Untitled'])[0],
            "author": author_str,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2026]])[0][0]),
            "journal": item.get('container-title', [''])[0],
            "vol": item.get('volume', ''),
            "issue": item.get('issue', ''),
            "page": item.get('page', ''),
            "doi": item.get('DOI', '')
        }
    except: return None

# ==========================================
# 5. SAYFA İÇERİKLERİ
# ==========================================

if page_selection == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Management"}</p>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
            <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
                <b>Citemate Pro</b>; PubMed, Google Scholar ve Mendeley uyumlu, tam bibliyografik veri seti sağlayan bir <b>bilimsel atıf motorudur.</b> 
                Makale kapağından veya DOI üzerinden saniyeler içinde uluslararası standartlarda (NLM/Vancouver, APA 7, IEEE) referanslar oluşturur.
            </p>
        </div>
    """, unsafe_allow_html=True)

    style = st.selectbox("Bibliyografik Format:", ["Vancouver (NLM)", "APA 7th", "IEEE", "MLA"])
    t1, t2, t3 = st.tabs(["🔗 DOI / PMID", "🔍 Başlık Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Girin (Örn: 10.1016/j.cell...):", key="doi_input")
        if st.button("Kaynağı Çözümle", key="doi_add"):
            res = fetch_metadata(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Tam Yayın Adı Girin:", key="search_input")
        if st.button("Global Veritabanında Ara", key="search_add"):
            res = fetch_metadata(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("Makale PDF Yükle (Maks 10MB)", type="pdf")
        if f and st.button("Otomatik Veri Çek"):
            try:
                doc = fitz.open(stream=f.read(), filetype="pdf")
                text = "".join([p.get_text() for p in doc[:3]])
                match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                if match:
                    res = fetch_metadata(match.group(), True)
                    if res: st.session_state.refs.append(res); st.rerun()
                else: st.warning("Metadata içerisinde DOI tespit edilemedi.")
            except: st.error("PDF işleme hatası.")
    
    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            # Bilimsel Detaylandırma
            vol_issue = f"{r['vol']}({r['issue']})" if r['vol'] and r['issue'] else r['vol']
            pages = f":{r['page']}" if r['page'] else ""
            
            if "Vancouver" in style:
                cite = f"{i}. {r['author']}. {r['title']}. {r['journal']}. {r['year']};{vol_issue}{pages}. doi:{r['doi']}"
            elif "APA" in style:
                cite = f"{r['author']} ({r['year']}). {r['title']}. {r['journal']}, {vol_issue}{pages}. https://doi.org/{r['doi']}"
            elif "IEEE" in style:
                cite = f"[{i}] {r['author']}, \"{r['title']},\" {r['journal']}, vol. {r['vol']}, no. {r['issue']}, pp. {r['page']}, {r['year']}."
            else:
                cite = f"{r['author']}. \"{r['title']}.\" {r['journal']}, vol. {r['vol']}, {r['year']}, pp. {r['page']}."
            
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        st.divider()
        c_c1, c_c2 = st.columns(2)
        with c_c1: st.download_button("📥 Kaynakçayı TXT Olarak İndir", txt_out, use_container_width=True)
        with c_c2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

elif page_selection == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Lifegenix Danışmanlık: Biyoinformatik ve Akademik Analiz Çözümleri</p>', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""<div class="service-card"><h3 style="color:#34d399;">🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve yorumlanması.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3 style="color:#34d399;">🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik veri modelleme, Python tabanlı hastalık sınıflandırma ve tahmine dayalı biyoinformatik sistemleri.</p><span class="feature-tag">Python</span><span class="feature-tag">ML/AI</span></div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown("""<div class="service-card"><h3 style="color:#34d399;">📊 Büyük Veri Analitiği</h3><p>Karmaşık akademik ve biyolojik veri setlerinin ileri istatistiksel raporlanması ve profesyonel görselleştirilmesi.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3 style="color:#34d399;">🖋️ Akademik Yazım & Editoryal</h3><p>Uluslararası standartlarda referans yönetimi (Mendeley, EndNote uyumlu) ve yayına hazırlık danışmanlığı.</p><span class="feature-tag">Editorial</span><span class="feature-tag">Publication</span></div>""", unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük ve Teknolojik Üstünlük</div>', unsafe_allow_html=True)
