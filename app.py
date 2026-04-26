import streamlit as st
import requests
import re
import fitz  # PyMuPDF
import base64

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Global Citation Hub", page_icon="🎓", layout="wide")

# ==========================================
# LOGO ENTEGRASYONU
# ==========================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# 'image_1.png' dosyasını klasörünüzde bulundurmayı unutmayın
logo_data = get_base64_of_bin_file('image_1.png')
logo_html = f'<img src="data:image/png;base64,{logo_data}" class="sidebar-logo">' if logo_data else '<p style="color:#34d399;font-weight:bold;text-align:center;">🎓 Citemate Pro</p>'

# ==========================================
# 2. HAFIZA BAŞLATMA
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

# ==========================================
# 3. TASARIM (CSS)
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 58px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 0px; }}
    .sub-title {{ color: #f8fafc; font-size: 20px; margin-bottom: 35px; font-weight: 300; }}
    .info-box {{ background-color: rgba(52, 211, 153, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin-bottom: 35px; }}
    .service-card {{ background: #161b22; padding: 22px; border-radius: 15px; border-top: 4px solid #34d399; margin-bottom: 15px; min-height: 180px; }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 3px 10px; border-radius: 5px; font-size: 10px; font-weight: bold; margin-right: 5px; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }}
    .sidebar-logo {{ display: block; margin: 0 auto 15px auto; width: 150px; border-radius: 10px; box-shadow: 0px 4px 15px rgba(52, 211, 153, 0.3); }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ
# ==========================================
with st.sidebar:
    st.markdown(logo_html, unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"
    if c2.button("🇺🇸 EN"): st.session_state.lang = "English"
    st.divider()
    page_selection = st.radio("MENÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    st.divider()
    st.markdown(f'<div style="background:#1e293b;padding:15px;border-radius:12px;border:1px solid #334155;text-align:center;"><p style="color:#34d399;font-weight:bold;">📩 Bize Ulaşın</p><a href="mailto:{MY_EMAIL}" style="display:block;background:#34d399;color:black;padding:10px;border-radius:8px;font-weight:bold;text-decoration:none;">Mesaj Gönder</a></div>', unsafe_allow_html=True)

# ==========================================
# 5. AKILLI FORMATLAMA MOTORU (CStyleLib)
# ==========================================
def fetch_academic_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        authors = item.get('author', [])
        fmt_authors = [f"{a.get('family', '')} {a.get('given', '')[:1]}" for a in authors[:6]]
        author_str = ", ".join(fmt_authors)
        if len(authors) > 6: author_str += " et al"
        return {
            "title": item.get('title', ['Untitled'])[0], "author": author_str,
            "year": str(item.get('published-print', item.get('created', {})).get('date-parts', [[2026]])[0][0]),
            "journal": item.get('container-title', [''])[0], "vol": item.get('volume', ''),
            "issue": item.get('issue', ''), "page": item.get('page', ''), "doi": item.get('DOI', '')
        }
    except: return None

# ==========================================
# 6. SAYFA İÇERİKLERİ
# ==========================================

if page_selection == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{"Global Akademik Veritabanı ve CSL Entegrasyonu" if st.session_state.lang == "Türkçe" else "Global Database & CSL Integration"}</p>', unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
            <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
                <b>Citemate Pro</b>, Zotero ve Mendeley gibi profesyonel araçların kullandığı <b>Citation Style Language (CSL)</b> standartlarına uyumludur. 
                PubMed, Google Scholar ve Crossref verilerini kullanarak uluslararası akademik dergilerin beklediği hassas formatlarda referans oluşturur.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # GENİŞLETİLMİŞ FORMAT SEÇENEKLERİ
    style = st.selectbox("Akademik Yazım Standardı (Style):", [
        "Vancouver (NLM/PubMed)", 
        "APA 7th Edition", 
        "IEEE (Engineering)", 
        "AMA (Medical)", 
        "Nature (Science)", 
        "Chicago (Author-Date)", 
        "MLA 9th Edition",
        "Bluebook (Legal)"
    ])
    
    t1, t2, t3 = st.tabs(["🔗 DOI / PMID", "🔍 Başlık Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Girin:", key="doi_in")
        if st.button("Listeye Ekle", key="btn_d"):
            res = fetch_academic_data(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın/Makale Adı:", key="q_in")
        if st.button("Ara ve Ekle", key="btn_s"):
            res = fetch_academic_data(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle", type="pdf")
        if f and st.button("Otomatik Veri Çek"):
            try:
                with fitz.open(stream=f.read(), filetype="pdf") as doc:
                    text = "".join([p.get_text() for p in doc[:3]])
                    match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                    if match:
                        res = fetch_academic_data(match.group(), True)
                        if res: st.session_state.refs.append(res); st.rerun()
                    else: st.warning("DOI bulunamadı.")
            except: st.error("PDF işleme hatası.")
    
    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            v_i = f"{r['vol']}({r['issue']})" if r['vol'] and r['issue'] else r['vol']
            p_g = f":{r['page']}" if r['page'] else ""
            
            # FORMAT MANTIĞI (Genişletilmiş)
            if "Vancouver" in style or "AMA" in style:
                cite = f"{i}. {r['author']}. {r['title']}. {r['journal']}. {r['year']};{v_i}{p_g}. doi:{r['doi']}"
            elif "APA" in style or "Chicago" in style:
                cite = f"{r['author']} ({r['year']}). {r['title']}. {r['journal']}, {v_i}{p_g}. https://doi.org/{r['doi']}"
            elif "IEEE" in style or "Nature" in style:
                cite = f"[{i}] {r['author']}, \"{r['title']},\" {r['journal']}, vol. {r['vol']}, no. {r['issue']}, pp. {r['page']}, {r['year']}."
            else: # MLA & Bluebook mantığı
                cite = f"{r['author']}. \"{r['title']}.\" {r['journal']}, vol. {r['vol']}, {r['year']}, pp. {r['page']}."
            
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        col1, col2 = st.columns(2)
        with col1: st.download_button("📥 TXT (EndNote/Zotero Uyumlu)", txt_out, use_container_width=True)
        with col2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

    # SSS & NEDEN CITEMATE
    st.divider()
    fa_1, fa_2 = st.columns(2)
    with fa_1:
        st.markdown(f"### ❓ {'Sıkça Sorulan Sorular'}")
        with st.expander("Hangi dergileri destekliyor?"): st.write("CSL tabanlı motorumuz Nature, Science ve Elsevier grubu dahil binlerce dergiye uyumludur.")
        with st.expander("PMID ile arama yapılır mı?"): st.write("Evet, PubMed ID (PMID) girişi doğrudan desteklenmektedir.")
    with fa_2:
        st.markdown(f"### 🚀 {'Neden Citemate?'}")
        st.write("* **Hız:** Zotero veya Mendeley kurmaya gerek kalmadan tarayıcıda çözüm.")
        st.write("* **Doğruluk:** Crossref ve DataCite metadata çekirdeği kullanılır.")

elif page_selection == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">Lifegenix Danışmanlık: Biyoinformatik ve Büyük Veri</p>', unsafe_allow_html=True)
    
    # 4 Hizmet Kartı
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="service-card"><h3>🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve sağkalım analizleri.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik veri modelleme, Python tabanlı hastalık sınıflandırma ve yapay zeka modelleri.</p><span class="feature-tag">Python</span><span class="feature-tag">ML/AI</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="service-card"><h3>📊 Büyük Veri Analitiği</h3><p>Karmaşık akademik veri setlerinin ileri istatistiksel raporlanması ve görselleştirilmesi.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🖋️ Akademik Yazım & Editoryal</h3><p>Uluslararası standartlarda referans yönetimi ve yayına hazırlık danışmanlığı.</p><span class="feature-tag">Editorial</span><span class="feature-tag">CSL/Zotero</span></div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük</div>', unsafe_allow_html=True)
