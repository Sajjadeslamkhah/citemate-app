import streamlit as st
import re
from datetime import datetime

# ============================================================================
# 1. SAYFA AYARLARI
# ============================================================================
st.set_page_config(
    page_title="Citemate Pro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 2. GÖRSEL DÜZENLEME
# ============================================================================
st.markdown("""
    <style>
    .main { 
        background-color: #0e1117; 
    }
    
    /* Canlı Önizleme Kutusu */
    .preview-container { 
        background-color: #ffffff !important; 
        color: #1a1a1a !important; 
        padding: 25px; 
        border-radius: 12px; 
        border: 2px solid #27ae60;
        font-size: 16px;
        line-height: 1.8;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        font-family: 'Times New Roman', Times, serif;
    }
    
    /* Editör yazı rengi */
    .stTextArea textarea { 
        color: #ffffff !important; 
        background-color: #262730 !important; 
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    /* Atıf numarası stili */
    .cite-num { 
        color: #27ae60; 
        font-weight: bold; 
        background: #e8f5e9; 
        padding: 3px 6px; 
        border-radius: 3px; 
        margin: 0 2px;
    }
    
    /* Kaynakça kartı */
    .reference-card {
        background-color: #1e1e1e;
        border-left: 4px solid #27ae60;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .reference-card:hover {
        background-color: #262730;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
    }
    
    /* Format türü badge */
    .format-badge {
        display: inline-block;
        background-color: #27ae60;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
    }
    
    /* Statistik kutusu */
    .stat-box {
        background-color: #1e1e1e;
        border: 1px solid #27ae60;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: #27ae60;
    }
    
    /* Placeholder stil */
    .placeholder-text {
        color: #888;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 3. HAFIZA YÖNETİMİ
# ============================================================================
if 'references' not in st.session_state:
    st.session_state.references = []
if 'editor_text' not in st.session_state:
    st.session_state.editor_text = ""
if 'citation_format' not in st.session_state:
    st.session_state.citation_format = "APA"
if 'selected_refs' not in st.session_state:
    st.session_state.selected_refs = []

# ============================================================================
# 4. FORMAT FONKSİYONLARI
# ============================================================================

def format_citation(ref, citation_format, index):
    """Kaynağı seçilen formata göre biçimlendir"""
    url = ref['url']
    author = ref['author']
    year = ref['year']
    
    if citation_format == "APA":
        return f"{author} ({year}). Retrieved from {url}"
    
    elif citation_format == "MLA":
        return f"{author}. {year}. {url}"
    
    elif citation_format == "Vancouver":
        return f"{index}. {author}. Available from: {url}. [Accessed {datetime.now().strftime('%Y-%m-%d')}]."
    
    elif citation_format == "Harvard":
        return f"{author} {year}, {url}"
    
    elif citation_format == "Chicago":
        return f"{author}. Accessed {datetime.now().strftime('%B %d, %Y')}. {url}."
    
    return f"{author} ({year}). {url}"

# ============================================================================
# 5. YARDIMCI FONKSİYONLAR
# ============================================================================

def add_source(url, author):
    """Kaynağı ekle (mükerrer kontrolü ile)"""
    if not url or not url.strip():
        st.error("URL boş olamaz")
        return False
    
    existing_urls = [r['url'] for r in st.session_state.references]
    if url in existing_urls:
        st.warning(f"⚠️ Bu kaynak zaten ekli (Sıra: {existing_urls.index(url)+1})")
        return False
    
    st.session_state.references.append({
        "url": url.strip(),
        "author": author.strip() if author else "Anonim",
        "year": datetime.now().strftime("%Y"),
        "id": len(st.session_state.references) + 1
    })
    return True

def remove_source(index):
    """Kaynağı sil"""
    st.session_state.references.pop(index)

def get_bibliography():
    """Kaynakçayı oluştur"""
    if not st.session_state.references:
        return "Henüz kaynak eklenmemiş."
    
    bib = f"KAYNAKÇA ({st.session_state.citation_format})\n"
    bib += "=" * 50 + "\n\n"
    
    for idx, ref in enumerate(st.session_state.references, 1):
        formatted = format_citation(ref, st.session_state.citation_format, idx)
        bib += f"{idx}. {formatted}\n\n"
    
    return bib

# ============================================================================
# 6. ARAYÜZ - BAŞLIK
# ============================================================================
st.title("📚 Citemate Pro")
st.markdown("**Profesyonel Akademik Editör ve Kaynak Yönetim Sistemi**")
st.markdown("---")

# ============================================================================
# 7. FORMAT SEÇIMI (DÜZELTİLDİ - Artık çalışıyor)
# ============================================================================
col_format1, col_format2, col_format3, col_format4, col_format5 = st.columns(5)

with col_format1:
    if st.button("APA", use_container_width=True, 
                 type="primary" if st.session_state.citation_format == "APA" else "secondary"):
        st.session_state.citation_format = "APA"
        st.rerun()

with col_format2:
    if st.button("MLA", use_container_width=True,
                 type="primary" if st.session_state.citation_format == "MLA" else "secondary"):
        st.session_state.citation_format = "MLA"
        st.rerun()

with col_format3:
    if st.button("Vancouver", use_container_width=True,
                 type="primary" if st.session_state.citation_format == "Vancouver" else "secondary"):
        st.session_state.citation_format = "Vancouver"
        st.rerun()

with col_format4:
    if st.button("Harvard", use_container_width=True,
                 type="primary" if st.session_state.citation_format == "Harvard" else "secondary"):
        st.session_state.citation_format = "Harvard"
        st.rerun()

with col_format5:
    if st.button("Chicago", use_container_width=True,
                 type="primary" if st.session_state.citation_format == "Chicago" else "secondary"):
        st.session_state.citation_format = "Chicago"
        st.rerun()

st.markdown(f"<p style='text-align: center; color: #27ae60;'><b>Seçili Format: {st.session_state.citation_format}</b></p>", 
            unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# 8. ANA LAYOUT
# ============================================================================
col_left, col_right = st.columns([6, 4], gap="large")

# ============================================================================
# SOL SÜTUN: EDITOR VE ÖNIZLEME
# ============================================================================
with col_left:
    st.subheader("✍️ Akademik Editör")
    st.caption("Metin yazın ve [cite] etiketlerini kullanarak alıntılarınızı işaretleyin")
    
    # Metin girişi
    t_input = st.text_area(
        "Yazı alanı",
        value=st.session_state.editor_text,
        height=400,
        key="txt",
        placeholder="Metin yazın... [cite] kullanarak alıntıları işaretleyin"
    )
    st.session_state.editor_text = t_input
    
    # İstatistikler
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        word_count = len(st.session_state.editor_text.split())
        st.markdown(f"<div class='stat-box'><b>{word_count}</b><br>Kelime</div>", unsafe_allow_html=True)
    with col_stat2:
        cite_count = st.session_state.editor_text.count("[cite]")
        st.markdown(f"<div class='stat-box'><b>{cite_count}</b><br>[cite]</div>", unsafe_allow_html=True)
    with col_stat3:
        ref_count = len(st.session_state.references)
        st.markdown(f"<div class='stat-box'><b>{ref_count}</b><br>Kaynak</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Canlı Önizleme (DÜZELTILDI)
    st.markdown("### 📖 Canlı Önizleme")
    
    processed = st.session_state.editor_text
    cite_matches = re.findall(r'\[cite\]', processed)
    
    # [cite] etiketlerini numaralarla değiştir
    for idx in range(min(len(cite_matches), len(st.session_state.references))):
        processed = processed.replace("[cite]", f"<span class='cite-num'>({idx+1})</span>", 1)
    
    st.markdown(
        f'<div class="preview-container">{processed.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True
    )

# ============================================================================
# SAĞ SÜTUN: KAYNAK YÖNETİMİ
# ============================================================================
with col_right:
    st.subheader("🚀 Araçlar")
    
    # [cite] Ekle Butonu (TAMİRLENDİ)
    if st.button("➕ [cite] Ekle", use_container_width=True, key="cite_btn"):
        st.session_state.editor_text += " [cite]"
        st.rerun()
    
    st.divider()
    
    # Yeni Kaynak Ekleme
    st.subheader("📥 Yeni Kaynak Ekle")
    
    url_input = st.text_input("URL'yi yapıştırın", placeholder="https://example.com")
    author_input = st.text_input("Yazar Adı (Zorunlu değil)", placeholder="Adı Soyadı")
    
    if st.button("✅ Kaynağı Ekle", type="primary", use_container_width=True):
        if url_input:
            if add_source(url_input, author_input):
                st.success("✅ Kaynak başarıyla eklendi!")
                st.rerun()
        else:
            st.error("❌ Lütfen bir URL girin")
    
    st.divider()
    
    # Kaynakça Listesi (GELİŞTİRİLDİ)
    st.subheader("📋 Eklenen Kaynaklar")
    
    if st.session_state.references:
        st.info(f"📌 Toplam {len(st.session_state.references)} kaynak eklendi")
        
        for i, ref in enumerate(st.session_state.references):
            with st.container():
                st.markdown(
                    f"""
                    <div class='reference-card'>
                    <b>({i+1})</b> <b>{ref['author']}</b> - {ref['year']}
                    <br><small style='color: #888;'>{ref['url']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
                with col_btn1:
                    if st.button("🔗 Kopyala", key=f"copy_{i}", use_container_width=True):
                        formatted = format_citation(ref, st.session_state.citation_format, i+1)
                        st.info(f"Formatlanmış: {formatted}")
                
                with col_btn2:
                    if st.button("📌 [cite] Ekle", key=f"cite_ref_{i}", use_container_width=True):
                        st.session_state.editor_text += " [cite]"
                        st.rerun()
                
                with col_btn3:
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                        remove_source(i)
                        st.rerun()
    else:
        st.info("📌 Henüz kaynak eklenmemiş")

# ============================================================================
# 9. KAYNAKÇA BÖLÜMÜ (YENİ - PROFESYONEL)
# ============================================================================
st.markdown("---")
st.markdown("## 📚 Kaynakça")

if st.session_state.references:
    # Kaynakçayı göster
    bibliography = get_bibliography()
    
    col_bib1, col_bib2 = st.columns([3, 1])
    
    with col_bib1:
        st.code(bibliography, language="text")
    
    with col_bib2:
        # İndir butonu
        st.download_button(
            label="⬇️ İndir",
            data=bibliography,
            file_name=f"kaynakca_{st.session_state.citation_format.lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # Kopyala butonu
        if st.button("📋 Kopyala", use_container_width=True):
            st.success("📋 Kopyalandı (Ctrl+V ile yapıştırın)")
else:
    st.info("Kaynakça oluşturmak için kaynak ekleyin")

# ============================================================================
# 10. SIDEBAR: AYARLAR
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    
    if st.button("🗑️ Tümünü Sıfırla", use_container_width=True):
        st.session_state.references = []
        st.session_state.editor_text = ""
        st.success("✅ Tüm veriler silindi")
        st.rerun()
    
    st.divider()
    
    st.markdown("### 📖 Rehber")
    
    with st.expander("📋 Format Açıklamaları"):
        st.markdown("""
        **APA**: Sosyal bilimler, psikoloji
        
        **MLA**: Edebiyat, diller
        
        **Vancouver**: Tıbbi bilimler
        
        **Harvard**: Genel akademik
        
        **Chicago**: Tarih ve sosyal bilimler
        """)
    
    with st.expander("🎯 Nasıl Kullanılır?"):
        st.markdown("""
        1. Format seçin (APA, MLA, vb.)
        2. Metni yazın
        3. [cite] etiketlerini işaretleme için kullanın
        4. Kaynakları sağda ekleyin
        5. Kaynakça otomatik oluşturulur
        6. İndirin veya kopyalayın
        """)
    
    with st.expander("💡 İpuçları"):
        st.markdown("""
        - Aynı kaynağı birden fazla kez [cite] ile işaretleyebilirsiniz
        - Format değiştirirseniz kaynakça otomatik güncellenir
        - Mükerrer kaynaklar otomatik algılanır
        """)

# ============================================================================
# 11. FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 12px;'>"
    "Citemate Pro v2.0 | Profesyonel Akademik Editör"
    "</p>",
    unsafe_allow_html=True
)
