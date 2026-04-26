import streamlit as st
import requests
import re
import fitz  # PyMuPDF
import base64

# ==========================================
# 1. SAYFA YAPILANDIRMASI & SEO
# ==========================================
st.set_page_config(page_title="Citemate Pro | Global Academic Intelligence", page_icon="🎓", layout="wide")

# ==========================================
# 2. LOGO ENTEGRASYONU (BASE64)
# ==========================================
def get_base64_logo(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

logo_b64 = get_base64_logo("Logo.jpg")

# ==========================================
# 3. TASARIM VE KURUMSAL STİL (CSS)
# ==========================================
MY_EMAIL = "mbgsajjad@gmail.com"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; }}
    .main-title {{ font-size: 58px !important; font-weight: 900 !important; color: #34d399; margin-bottom: 0px; }}
    .sub-title {{ color: #f8fafc; font-size: 20px; margin-bottom: 35px; font-weight: 300; }}
    .info-box {{ background-color: rgba(52, 211, 153, 0.05); padding: 22px; border-radius: 12px; border: 1px dashed rgba(52, 211, 153, 0.3); margin-bottom: 35px; }}
    .service-card {{ 
        background: #161b22; padding: 25px; border-radius: 18px; border-top: 4px solid #34d399; 
        margin-bottom: 20px; min-height: 220px; transition: 0.3s;
    }}
    .service-card:hover {{ transform: translateY(-5px); border-color: #10b981; }}
    .feature-tag {{ background: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 6px; }}
    .footer {{ color: #64748b; font-size: 14px; text-align: center; margin-top: 80px; padding: 25px; border-top: 1px solid #1e293b; }}
    .sidebar-logo-img {{ display: block; margin: 0 auto 20px auto; width: 180px; border-radius: 12px; box-shadow: 0px 4px 20px rgba(52, 211, 153, 0.2); }}
    .guide-step {{ color: #34d399; font-weight: bold; font-size: 18px; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. YAN MENÜ (NAVİGASYON)
# ==========================================
with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/jpeg;base64,{logo_b64}" class="sidebar-logo-img">', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:28px; font-weight:bold; color:#34d399; text-align:center;">🎓 Citemate Pro</p>', unsafe_allow_html=True)
    
    st.divider()
    lang_col1, lang_col2 = st.columns(2)
    if lang_col1.button("🇹🇷 TR"): st.session_state.lang = "Türkçe"
    if lang_col2.button("🇺🇸 EN"): st.session_state.lang = "English"
    
    st.divider()
    page_selection = st.radio("SİSTEM MENÜSÜ", ["🏠 Atıf Motoru", "💎 Profesyonel Hizmetler"], label_visibility="collapsed")
    
    st.divider()
    st.markdown(f'<div style="background:#1e293b;padding:18px;border-radius:12px;border:1px solid #334155;text-align:center;"><p style="color:#34d399;font-weight:bold;margin-bottom:8px;">📩 Bize Ulaşın</p><a href="mailto:{MY_EMAIL}" style="display:block;background:#34d399;color:black;padding:10px;border-radius:8px;font-weight:bold;text-decoration:none;">Mesaj Gönder</a></div>', unsafe_allow_html=True)

# ==========================================
# 5. AKILLI VERİ MOTORU
# ==========================================
if 'refs' not in st.session_state: st.session_state.refs = []
if 'lang' not in st.session_state: st.session_state.lang = "Türkçe"

def get_academic_metadata(query, is_doi=False):
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    try:
        clean_q = re.search(doi_pattern, query, re.I).group() if is_doi else query
        url = f"https://api.crossref.org/works/{clean_q}" if is_doi else f"https://api.crossref.org/works?query={query}&rows=1"
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
    st.markdown(f'<p class="sub-title">{"Akademik Mükemmeliyet İçin Kusursuz Atıf Yönetimi" if st.session_state.lang == "Türkçe" else "Elite Academic Citation Engine"}</p>', unsafe_allow_html=True)

    # ✅ BİLGİLENDİRME MESAJI
    st.markdown("""
        <div class="info-box">
            <p style="color: #e2e8f0; font-size: 16px; line-height: 1.6; margin-bottom: 0;">
                <b>Citemate Pro</b>, araştırmacıların ve öğrencilerin kaynakça hazırlama yükünü hafifletmek için tasarlanmış, 
                yapay zeka destekli bir <b>atıf düzenleme motorudur.</b> DOI numarası, yayın başlığı veya doğrudan PDF dosyanızı 
                kullanarak saniyeler içinde hatasız; Vancouver, APA ve IEEE formatlarında profesyonel referanslar oluşturur. 
                Karmaşık akademik standartları otomatiğe bağlayarak, enerjinizi sadece araştırmanıza odaklamanızı sağlar.
            </p>
        </div>
    """, unsafe_allow_html=True)

    style = st.selectbox("Bibliyografik Format:", ["Vancouver (NLM)", "APA 7th Edition", "IEEE", "Nature", "AMA"])
    t1, t2, t3, t4 = st.tabs(["🔗 DOI / PMID", "🔍 Başlık Arama", "📄 PDF Analizi", "📖 Kullanım Kılavuzu"])
    
    with t1:
        doi_in = st.text_input("DOI Girin:", key="f_doi")
        if st.button("Listeye Ekle", key="btn_d"):
            res = get_academic_metadata(doi_in, True)
            if res: st.session_state.refs.append(res); st.rerun()

    with t2:
        q_in = st.text_input("Yayın Adı Girin:", key="f_q")
        if st.button("Global Ara ve Ekle", key="btn_s"):
            res = get_academic_metadata(q_in, False)
            if res: st.session_state.refs.append(res); st.rerun()

    with t3:
        f_pdf = st.file_uploader("PDF Yükle (Maks 10MB)", type="pdf")
        if f_pdf and st.button("Otomatik Veri Çek"):
            try:
                with fitz.open(stream=f_pdf.read(), filetype="pdf") as doc:
                    txt = "".join([p.get_text() for p in doc[:3]])
                    match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', txt, re.I)
                    if match:
                        res = get_academic_metadata(match.group(), True)
                        if res: st.session_state.refs.append(res); st.rerun()
                    else: st.warning("DOI tespit edilemedi.")
            except: st.error("PDF işleme hatası.")

    # ✅ KULLANIM KILAVUZU (YENİ)
    with t4:
        st.markdown(f"### 📖 {'Citemate Pro Nasıl Kullanılır?' if st.session_state.lang == 'Türkçe' else 'How to Use Citemate Pro?'}")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown('<p class="guide-step">1. Yöntem Seçin</p>DOI numarasını girin, makale adıyla arama yapın veya doğrudan PDF dosyanızı yükleyin.', unsafe_allow_html=True)
            st.markdown('<p class="guide-step">2. Format Belirleyin</p>Üstteki menüden Vancouver, APA veya IEEE gibi ihtiyacınız olan akademik stili seçin.', unsafe_allow_html=True)
        with col_g2:
            st.markdown('<p class="guide-step">3. Listeye Ekleyin</p>İşlenen kaynaklar otomatik olarak listenize eklenir ve kopyalanabilir hale gelir.', unsafe_allow_html=True)
            st.markdown('<p class="guide-step">4. Dışa Aktarın</p>İşiniz bittiğinde tüm listeyi tek tıkla .txt dosyası olarak bilgisayarınıza indirin.', unsafe_allow_html=True)

    if st.session_state.refs:
        st.divider()
        txt_out = ""
        for i, r in enumerate(st.session_state.refs, 1):
            v_i = f"{r['vol']}({r['issue']})" if r['vol'] and r['issue'] else r['vol']
            p_g = f":{r['page']}" if r['page'] else ""
            if "Vancouver" in style: cite = f"{i}. {r['author']}. {r['title']}. {r['journal']}. {r['year']};{v_i}{p_g}. doi:{r['doi']}"
            elif "APA" in style: cite = f"{r['author']} ({r['year']}). {r['title']}. {r['journal']}, {v_i}{p_g}. https://doi.org/{r['doi']}"
            else: cite = f"[{i}] {r['author']}, \"{r['title']},\" {r['journal']}, vol. {r['vol']}, no. {r['issue']}, pp. {r['page']}, {r['year']}."
            st.code(cite, language="text")
            txt_out += cite + "\n"
        
        c_1, c_2 = st.columns(2)
        with c_1: st.download_button("📥 Kaynakçayı TXT Olarak İndir", txt_out, use_container_width=True)
        with c_2: 
            if st.button("🗑️ Listeyi Temizle", use_container_width=True): 
                st.session_state.refs = []; st.rerun()

    # ✅ SSS & NEDEN CITEMATE
    st.divider()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"### ❓ {'Sıkça Sorulan Sorular'}")
        with st.expander("PubMed ve Google Scholar uyumlu mu?"): st.write("Kesinlikle. Motorumuz makalelerin en güncel metadata verilerini kullanarak global veritabanlarıyla uyumlu çalışır.")
        with st.expander("Dosyalarım kaydediliyor mu?"): st.write("Hayır. Gizliliğiniz bizim için önemlidir; yüklediğiniz PDF'ler sadece veri çekme işlemi sırasında geçici olarak işlenir ve saklanmaz.")
    with col_f2:
        st.markdown(f"### 🚀 {'Neden Citemate?'}")
        st.write("✓ **Hız:** Saatler süren manuel kaynakça hazırlama işlemini saniyelere indirir.")
        st.write("✓ **Hassasiyet:** Cilt, sayı ve sayfa numaralarını Crossref çekirdeğinden hatasız çeker.")
        st.write("✓ **Entegrasyon:** Lifegenix'in profesyonel biyoinformatik altyapısı ile desteklenmektedir.")

# --- SAYFA 2: PROFESYONEL HİZMETLER (4 KART) ---
elif page_selection == "💎 Profesyonel Hizmetler":
    st.markdown('<p class="main-title">Profesyonel Hizmetler</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">Lifegenix Danışmanlık: Biyoinformatik ve Büyük Veri</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="service-card"><h3>🧬 Genetik Veri Analizi</h3><p>NCBI, GEO ve TCGA büyük veri setlerinin Python tabanlı işlenmesi ve sağkalım analizleri.</p><span class="feature-tag">TCGA</span><span class="feature-tag">GEO</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🤖 Sağlıkta Makine Öğrenimi</h3><p>Klinik veri modelleme, Python tabanlı hastalık sınıflandırma ve yapay zeka modelleri.</p><span class="feature-tag">Python</span><span class="feature-tag">ML/AI</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="service-card"><h3>📊 Büyük Veri Analitiği</h3><p>Karmaşık akademik veri setlerinin ileri istatistiksel raporlanması ve görselleştirilmesi.</p><span class="feature-tag">Big Data</span><span class="feature-tag">Stats</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="service-card"><h3>🖋️ Akademik Yazım & Editoryal</h3><p>Uluslararası standartlarda referans yönetimi ve yayına hazırlık danışmanlığı.</p><span class="feature-tag">Editorial</span><span class="feature-tag">Publication</span></div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Lifegenix Danışmanlık | Akademik Dürüstlük</div>', unsafe_allow_html=True)
