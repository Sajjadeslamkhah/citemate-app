import streamlit as st
import requests
import re
import fitz  # PyMuPDF
import base64 # Logo entegrasyonu için gerekli

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Elite Academic Citation", page_icon="🎓", layout="wide")

# ==========================================
# LOGO ENTEGRASYONU (Base64 Teknolojisi)
# ==========================================
# Bu fonksiyon, resim dosyasını GitHub/Render'a yüklemeden doğrudan koda gömer.
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# UYARI: 'image_1.png' dosyasının 'app.py' ile aynı klasörde olduğundan emin olun.
# Eğer dosyayı assets/ klasörüne koyduysanız yolu 'assets/image_1.png' yapın.
try:
    logo_base64 = get_base64_of_bin_file('image_1.png')
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="sidebar-logo">'
except FileNotFoundError:
    # Eğer logo dosyası bulunamazsa site hata vermez, sadece yer tutucu gösterir.
    logo_html = '<p style="color:#34d399; font-weight:bold; text-align:center;">[ LOGO ]</p>'

# ==========================================
# 2. KRİTİK HAFIZA BAŞLATMA (Hata Giderici)
# ==========================================
if 'refs' not in st.session_state:
    st.session_state.refs = []
if 'lang' not in st.session_state:
    st.session_state.lang = "Türkçe"

# ==========================================
# 3. TASARIM (CSS) & Renk Uyumu
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 58px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 0px; }}
    .service-card {{ background: #161b22; padding: 22px; border-radius: 15px; border-left: 4px solid #34d399; margin-bottom: 15px; }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 3px 10px; border-radius: 5px; font-size: 10px; font-weight: bold; margin-right: 5px; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 60px; padding: 20px; border-top: 1px solid #1e293b; }}
    
    /* Logo Stil ve Renk Uyumu */
    .sidebar-logo {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px; /* Logo genişliği */
        margin-bottom: 15px;
        border-radius: 10px;
        /* Koyu lacivert logoyu yeşil temayla bütünleştirmek için hafif bir gölge */
        box-shadow: 0px 4px 15px rgba(52, 211, 153, 0.3); 
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ (NAVİGASYON)
# ==========================================
with st.sidebar:
    # LOGO BURAYA EKLENDİ
    st.markdown(logo_html, unsafe_allow_html=True)
    
    st.markdown('<p style="font-size:26px; font-weight:bold; color:#34d399; text-align:center;">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    st.divider()
    
    # Dil Seçimi
    c1, c2 = st.columns(2)
    if c1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"
    if c2.button("🇺🇸 EN"): st.session_state.lang = "English"
    
    st.divider()
    page_selection = st.radio("MENÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    
    st.divider()
    st.markdown(f"""
        <div style="background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155;">
            <p style="color: #34d399; font-weight: bold; margin-bottom: 5px; text-align:center;">📩 Bize Ulaşın</p>
            <a href="mailto:{MY_EMAIL}" style="display: block; background: #34d399; color: black; text-align: center; padding: 10px; border-radius: 8px; font-weight: bold; text-decoration: none;">Mesaj Gönder</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. METADATA MOTORU (BİLİMSEL DERİNLİK)
# ==========================================
def fetch_academic_data(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_query = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_query}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
        res = requests.get(url, timeout=10).json()
        item = res['message'] if is_doi else res['message']['items'][0]
        
        authors = item.get('author', [])
        formatted_authors = [f"{a.get('family', '')} {a.get('given', '')[:1]}" for a in authors[:6]]
        author_str = ", ".join(formatted_authors)
        if len(authors) > 6: author_str += " et et."
        
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
# 6. SAYFA İÇERİKLERİ
# ==========================================

if page_selection == "🏠 Atıf Motoru":
    st.markdown('<p class="main-title">🎓 Atıf Motoru</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#94a3b8; margin-bottom:30px;">{"Global Akademik Veritabanı Entegrasyonu" if st.session_state.lang == "Türkçe" else "Global Academic Database Integration"}</p>', unsafe_allow_html=True)

    style = st.selectbox("Bibliyografik Format:", ["Vancouver (NLM)", "APA 7th", "IEEE"])
    t1, t2, t3 = st.tabs(["🔗 DOI / PMID", "🔍 Başlık Arama", "📄 PDF Analizi"])
    
    with t1:
        doi_in = st.text_input("DOI Girin:", key="doi_field")
        if st.button("Kaynağı Ekle", key="btn_doi"):
            res = fetch_academic_data(doi_in, True)
            if res: 
                st.session_state.refs.append(res)
                st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı:", key="q_field")
        if st.button("Ara ve Ekle", key="btn_q"):
            res = fetch_academic_data(q_in, False)
            if res: 
                st.session_state.refs.append(res)
                st.rerun()

    with t3:
        f = st.file_uploader("PDF Yükle (Maks 10MB)", type="pdf")
        if f and st.button("Otomatik Veri Çek", key="btn_pdf"):
            try:
                with fitz.open(stream=f.read(), filetype="pdf") as doc:
                    text = "".join([p.get_text() for p in doc[:3]])
                    match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
                    if match:
                        res = fetch_academic_data(match.group(), True)
                        if res: 
                            st.session_state.refs.append(res)
                            st.rerun()
                    else: st.warning("DOI bulunamadı.")
            except Exception as e:
                st.error(f"PDF işleme hatası oluştu.")
    
    if len(st.session_state.refs) > 0:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            vol_iss = f"{r['vol']}({r['issue']})" if r['vol'] and r['issue'] else r['vol']
            pgs = f":{r['page']}" if r['page'] else ""
            
            if "Vancouver" in style:
                cite = f"{i}. {r['author']}. {r['title']}. {r['journal']}. {r['year']};{vol_iss}{pgs}. doi:{r['doi']}"
            elif "APA" in style:
                cite = f"{r['author']} ({r['year']}). {r['title']}. {r['journal']}, {vol_iss}{pgs}. https://doi.org/{r['doi']}"
            else: # IEEE
                cite = f"[{i}] {r['author']}, \"{r['title']},\" {r['journal']}, vol. {r['vol']}, no. {r['issue']}, pp. {r['page']}, {r['year']}."
            
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        c_d1, c_d2 = st.columns(2)
        with c_c1: st.download_button("📥 TXT Olarak İndir", txt_out, use_container_width=True)
        with c_c2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []
                st.rerun()

elif page_selection == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; margin-bottom:30px;">Lifegenix Danışmanlık: Biyoinformatik ve Akademik Analiz</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div class="service-card"><h3 style="color:#34d399; margin-top:0;">🧬 Genetik Veri Analizi</h3><p style="color:#cbd5e1; font-size:14px;">NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve sağkalım analizleri.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class="service-card"><h3 style="color:#34d399; margin-top:0;">📊 Büyük Veri Analitiği</h3><p style="color:#cbd5e1; font-size:14px;">Karmaşık akademik veri setlerinin ileri istatistiksel raporlanması ve görselleştirilmesi.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)

# FOOTER
st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük</div>', unsafe_allow_html=True)
