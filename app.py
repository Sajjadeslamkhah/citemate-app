import streamlit as st
import re
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import random
import string

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Citemate - Academic Citation Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CITATION STYLE ENUM
# ============================================================================
class CitationStyle(Enum):
    """Available citation styles"""
    VANCOUVER = "Vancouver"
    APA_NUMERIC = "APA (Numeric)"
    APA_AUTHOR_DATE = "APA (Author-Date)"
    HARVARD = "Harvard"
    MLA = "MLA"
    CHICAGO = "Chicago"

# ============================================================================
# CUSTOM STYLING
# ============================================================================
CUSTOM_CSS = """
<style>
    * {
        font-family: 'Times New Roman', 'Times', serif;
    }
    
    .editor-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        min-height: 500px;
        line-height: 1.5;
        font-size: 15px;
    }
    
    .reference-panel {
        background-color: #ecf0f1;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        line-height: 1.5;
    }
    
    .bibliography-panel {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #27ae60;
        line-height: 1.6;
        margin-top: 20px;
    }
    
    .source-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #3498db;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .source-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        transition: all 0.2s ease;
    }
    
    .citation-tag {
        background-color: #fff3cd;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
        color: #333;
        font-family: 'Courier New', monospace;
        cursor: pointer;
    }
    
    .citation-tag:hover {
        background-color: #ffe69c;
        transform: scale(1.05);
    }
    
    .citation-number {
        background-color: #d4edda;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: bold;
        color: #155724;
        font-family: 'Courier New', monospace;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #27ae60;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #34495e;
        margin-top: 20px;
    }
    
    h3 {
        color: #7f8c8d;
    }
    
    .stButton > button {
        background-color: #27ae60;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #229954;
    }
    
    .bibliography-entry {
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #ecf0f1;
        line-height: 1.7;
    }
    
    .bibliography-entry:last-child {
        border-bottom: none;
    }
    
    .format-badge {
        display: inline-block;
        background-color: #e8f4f8;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: #2c3e50;
        margin-left: 8px;
        font-weight: bold;
    }
    
    .quick-insert-btn {
        background-color: #3498db;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        font-size: 12px;
        font-weight: bold;
        transition: all 0.2s;
    }
    
    .quick-insert-btn:hover {
        background-color: #2980b9;
        transform: scale(1.05);
    }
    
    .tab-style {
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    
    .source-number {
        display: inline-block;
        background-color: #27ae60;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: bold;
        margin-right: 10px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def initialize_session_state():
    """Initialize all session state variables."""
    if 'references' not in st.session_state:
        st.session_state.references = []
    if 'editor_text' not in st.session_state:
        st.session_state.editor_text = ""
    if 'citation_style' not in st.session_state:
        st.session_state.citation_style = CitationStyle.APA_NUMERIC.value
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'selected_source' not in st.session_state:
        st.session_state.selected_source = None
    if 'cursor_position' not in st.session_state:
        st.session_state.cursor_position = 0

initialize_session_state()

# ============================================================================
# CITATION FORMATTING FUNCTIONS
# ============================================================================

def extract_author_from_url(url: str) -> str:
    """Extract author name from URL or return generic name."""
    if "pubmed" in url.lower():
        return "Author"
    elif "scholar" in url.lower():
        return "Scholar"
    else:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return domain.replace("www.", "").title()

def get_domain_name(url: str) -> str:
    """Extract clean domain name from URL."""
    if "pubmed" in url.lower():
        return "PubMed Central"
    elif "scholar" in url.lower():
        return "Google Scholar"
    elif "doi.org" in url.lower():
        return "DOI"
    else:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        return domain.replace("www.", "")

def format_citation(source: Dict, style: str, citation_number: Optional[int] = None) -> str:
    """Format a citation based on the selected style."""
    url = source.get('url', '')
    domain = get_domain_name(url)
    author = source.get('author', extract_author_from_url(url))
    year = datetime.now().year
    access_date = datetime.now().strftime("%Y-%m-%d")
    
    if style == CitationStyle.VANCOUVER.value:
        return f"{author}. {domain}. Available from: {url}. [Accessed {access_date}]."
    
    elif style == CitationStyle.APA_NUMERIC.value:
        return f"({citation_number}) {author}. {domain}. Retrieved from {url} on {access_date}."
    
    elif style == CitationStyle.APA_AUTHOR_DATE.value:
        return f"{author}, {year}. {domain}. Retrieved from {url}"
    
    elif style == CitationStyle.HARVARD.value:
        return f"{author}, {year}. {domain}. [online] Available at: {url} (Accessed: {access_date})."
    
    elif style == CitationStyle.MLA.value:
        return f"{author}. \"{domain}.\" Accessed {access_date}. {url}."
    
    elif style == CitationStyle.CHICAGO.value:
        return f"{author}. \"{domain}.\" Accessed {access_date}. https://{url.replace('https://', '').replace('http://', '')}."
    
    else:
        return f"{domain}. {url}"

def format_bibliography_entry(source: Dict, style: str, entry_number: int) -> str:
    """Format complete bibliography entry with proper formatting."""
    url = source.get('url', '')
    domain = get_domain_name(url)
    author = source.get('author', extract_author_from_url(url))
    year = datetime.now().year
    access_date = datetime.now().strftime("%B %d, %Y")
    
    if style == CitationStyle.VANCOUVER.value:
        return (f"{entry_number}. {author}. {domain}. Available from: {url}. "
                f"[Accessed {access_date}].")
    
    elif style == CitationStyle.APA_NUMERIC.value:
        return (f"{entry_number}. {author}. ({year}). {domain}. Retrieved from {url}")
    
    elif style == CitationStyle.APA_AUTHOR_DATE.value:
        return (f"{author}, {year}. {domain}. Retrieved from {url}")
    
    elif style == CitationStyle.HARVARD.value:
        return (f"{author}, {year}. {domain}. [online] Available at: {url} "
                f"(Accessed: {access_date}).")
    
    elif style == CitationStyle.MLA.value:
        return (f"{author}. \"{domain}.\" Accessed {access_date}, {year}. {url}.")
    
    elif style == CitationStyle.CHICAGO.value:
        return (f"{author}. \"{domain}.\" Accessed {access_date}. {url}.")
    
    else:
        return f"{entry_number}. {domain}. {url}"

# ============================================================================
# CITATION REPLACEMENT ENGINE
# ============================================================================
def replace_cite_tags(text: str, num_references: int, style: str) -> str:
    """Replace [cite] placeholders with citations in the appropriate format."""
    if num_references == 0:
        return text
    
    cite_pattern = r'\[cite\]'
    cite_matches = list(re.finditer(cite_pattern, text))
    
    replacements_to_make = min(len(cite_matches), num_references)
    
    result = text
    for i in range(replacements_to_make - 1, -1, -1):
        match = cite_matches[i]
        citation_number = i + 1
        
        if style == CitationStyle.APA_AUTHOR_DATE.value:
            citation_text = "(Author, 2024)"
        else:
            citation_text = f"({citation_number})"
        
        result = (
            result[:match.start()] +
            citation_text +
            result[match.end():]
        )
    
    return result

def highlight_cite_preview(text: str) -> str:
    """Create a preview version with highlighting."""
    highlighted = re.sub(
        r'\[cite\]',
        '<span class="citation-tag">[cite]</span>',
        text
    )
    highlighted = re.sub(
        r'\((\d+)\)',
        r'<span class="citation-number">(\1)</span>',
        highlighted
    )
    return highlighted

# ============================================================================
# SOURCE MANAGEMENT FUNCTIONS
# ============================================================================
def add_reference(url: str, author: str = "", style: str = None) -> bool:
    """Add a new reference."""
    if not url or not url.strip():
        st.error("Lütfen geçerli bir URL girin")
        return False
    
    if not (url.startswith("http://") or url.startswith("https://") or "doi" in url.lower()):
        st.error("Lütfen geçerli bir URL girin (http/https ile başlamalı veya DOI içermeli)")
        return False
    
    if any(ref['url'] == url for ref in st.session_state.references):
        st.warning("Bu kaynak zaten eklenmiş")
        return False
    
    if not author or author.strip() == "":
        author = extract_author_from_url(url)
    
    reference = {
        'id': len(st.session_state.references) + 1,
        'url': url,
        'author': author,
        'style': style or st.session_state.citation_style,
        'added_at': datetime.now().isoformat()
    }
    
    st.session_state.references.append(reference)
    st.session_state.last_update = datetime.now()
    return True

def remove_reference(ref_id: int):
    """Remove a reference by ID."""
    st.session_state.references = [
        ref for ref in st.session_state.references if ref['id'] != ref_id
    ]
    st.session_state.last_update = datetime.now()

def move_reference_up(ref_id: int):
    """Move reference up in the list."""
    refs = st.session_state.references
    for i, ref in enumerate(refs):
        if ref['id'] == ref_id and i > 0:
            refs[i], refs[i-1] = refs[i-1], refs[i]
            st.session_state.last_update = datetime.now()
            break

def move_reference_down(ref_id: int):
    """Move reference down in the list."""
    refs = st.session_state.references
    for i, ref in enumerate(refs):
        if ref['id'] == ref_id and i < len(refs) - 1:
            refs[i], refs[i+1] = refs[i+1], refs[i]
            st.session_state.last_update = datetime.now()
            break

def insert_citation_at_cursor(citation_text: str):
    """Insert citation at cursor position in editor."""
    current_text = st.session_state.editor_text
    cursor_pos = st.session_state.cursor_position
    
    new_text = (
        current_text[:cursor_pos] +
        citation_text +
        current_text[cursor_pos:]
    )
    st.session_state.editor_text = new_text
    st.session_state.cursor_position = cursor_pos + len(citation_text)

# ============================================================================
# MAIN LAYOUT
# ============================================================================
st.markdown("# 📚 Citemate")
st.markdown("### Profesyonel Akademik Kaynak Yönetimi")
st.markdown("---")

# Create three-column layout for format selection
col1, col2, col3 = st.columns([2, 4, 2])

with col1:
    st.markdown("#### 📋 Alıntı Formatı")

with col2:
    # Citation format selector with tabs
    format_options = [style.value for style in CitationStyle]
    selected_format = st.selectbox(
        label="Format seçin:",
        options=format_options,
        index=1,
        key="format_selector",
        label_visibility="collapsed"
    )
    st.session_state.citation_style = selected_format

with col3:
    st.markdown("")

# Create two-column layout for editor and references
col_left, col_right = st.columns([6, 4], gap="large")

# ============================================================================
# LEFT COLUMN: ACADEMIC EDITOR
# ============================================================================
with col_left:
    st.markdown("### ✍️ Akademik Editör")
    
    editor_text = st.text_area(
        label="Yazı yazın",
        value=st.session_state.editor_text,
        height=450,
        placeholder="Akademik yazınızı burada yazın...\n\n[cite] yer tutucularını kullanarak alıntılarınızı işaretleyin.",
        help="[cite] kullanarak alıntı yerlerini işaretleyin",
        key="text_input"
    )
    
    st.session_state.editor_text = editor_text
    
    # Preview section
    st.markdown("### 📖 Canlı Önizleme")
    
    num_refs = len(st.session_state.references)
    processed_text = replace_cite_tags(editor_text, num_refs, st.session_state.citation_style)
    highlighted_preview = highlight_cite_preview(processed_text)
    
    preview_container = st.container()
    with preview_container:
        st.markdown(
            f'<div class="editor-container">{highlighted_preview.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True
        )
    
    # Statistics
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        word_count = len(editor_text.split())
        st.metric("Kelime Sayısı", word_count)
    with col_stats2:
        cite_count = len(re.findall(r'\[cite\]', editor_text))
        st.metric("Alıntı Yer Tutucu", cite_count)
    with col_stats3:
        ref_count = len(st.session_state.references)
        st.metric("Eklenen Kaynaklar", ref_count)

# ============================================================================
# RIGHT COLUMN: SOURCE & REFERENCE MANAGEMENT
# ============================================================================
with col_right:
    st.markdown("### 📖 Kaynak Yönetimi")
    
    # Input section
    st.markdown("#### ➕ Yeni Kaynak Ekle")
    
    input_col1, input_col2 = st.columns([3, 2])
    
    with input_col1:
        source_url = st.text_input(
            label="Kaynak URL",
            placeholder="https://pubmed.ncbi.nlm.nih.gov/...",
            help="PubMed, Google Scholar, DOI veya akademik kaynak URL'si"
        )
    
    with input_col2:
        author_name = st.text_input(
            label="Yazar",
            placeholder="İsteğe bağlı",
            help="Yazar adı (otomatik algılanır)"
        )
    
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("➕ Kaynak Ekle", use_container_width=True, type="primary"):
            if add_reference(source_url, author_name, st.session_state.citation_style):
                st.success("✅ Kaynak eklendi!")
                st.rerun()
    
    with button_col2:
        if st.button("[cite] Ekle", use_container_width=True):
            insert_citation_at_cursor("[cite]")
            st.success("Metin içine [cite] eklendi")
            st.rerun()
    
    st.markdown("---")
    
    # References list
    st.markdown("#### 📋 Eklenen Kaynaklar")
    
    if st.session_state.references:
        st.info(f"**Toplam Kaynak: {len(st.session_state.references)}**")
        
        for idx, ref in enumerate(st.session_state.references, 1):
            with st.container():
                st.markdown(f'<div class="source-card">', unsafe_allow_html=True)
                
                # Source number and info
                col_num, col_info = st.columns([0.8, 5])
                
                with col_num:
                    st.markdown(f'<div class="source-number">{idx}</div>', unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"**{ref['author']}**")
                    st.markdown(f"<small>{ref['url']}</small>", unsafe_allow_html=True)
                
                # Action buttons
                button_col1, button_col2, button_col3, button_col4, button_col5 = st.columns(5)
                
                with button_col1:
                    if st.button("🔼", key=f"up_{ref['id']}", use_container_width=True, help="Yukarı taşı"):
                        move_reference_up(ref['id'])
                        st.rerun()
                
                with button_col2:
                    if st.button("🔽", key=f"down_{ref['id']}", use_container_width=True, help="Aşağı taşı"):
                        move_reference_down(ref['id'])
                        st.rerun()
                
                with button_col3:
                    if st.button("📌", key=f"insert_{ref['id']}", use_container_width=True, help="Metin içine ekle"):
                        insert_citation_at_cursor("[cite]")
                        st.session_state.selected_source = idx
                        st.success(f"[cite] eklendi - Kaynak #{idx}")
                        st.rerun()
                
                with button_col4:
                    if st.button("📋", key=f"copy_{ref['id']}", use_container_width=True, help="Kopyala"):
                        citation_text = format_citation(ref, st.session_state.citation_style, idx)
                        st.code(citation_text, language="text")
                
                with button_col5:
                    if st.button("🗑️", key=f"delete_{ref['id']}", use_container_width=True, help="Sil"):
                        remove_reference(ref['id'])
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Bibliography section
        st.markdown("---")
        st.markdown("### 📚 Kaynakça")
        
        with st.container():
            st.markdown(f'<div class="bibliography-panel">', unsafe_allow_html=True)
            
            for idx, ref in enumerate(st.session_state.references, 1):
                bib_entry = format_bibliography_entry(ref, st.session_state.citation_style, idx)
                st.markdown(f'<div class="bibliography-entry">{bib_entry}</div>', 
                           unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export section
        st.markdown("---")
        st.markdown("#### 💾 Kaynakçayı İndir")
        
        bibliography_text = f"Kaynakça ({st.session_state.citation_style})\n"
        bibliography_text += "=" * 50 + "\n\n"
        
        for idx, ref in enumerate(st.session_state.references, 1):
            bib_entry = format_bibliography_entry(ref, st.session_state.citation_style, idx)
            bibliography_text += bib_entry + "\n\n"
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📋 Kopyala", use_container_width=True):
                st.code(bibliography_text, language="text")
        
        with col_export2:
            st.download_button(
                label="⬇️ İndir (TXT)",
                data=bibliography_text,
                file_name="kaynakca.txt",
                mime="text/plain",
                use_container_width=True
            )
        
    else:
        st.info("📌 Henüz kaynak eklenmemiş. Yukarıda ilk kaynağınızı ekleyin!")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(
        f"<small>**Citemate v2.0** | {st.session_state.citation_style}</small>",
        unsafe_allow_html=True
    )

with footer_col2:
    if st.session_state.last_update:
        update_time = st.session_state.last_update.strftime("%H:%M:%S")
        st.markdown(f"<small>Son güncelleme: {update_time}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small>Başlamaya hazır</small>", unsafe_allow_html=True)

with footer_col3:
    st.markdown(
        "<small>💡 İpucu: [cite] yer tutucularını kullanın</small>",
        unsafe_allow_html=True
    )

# ============================================================================
# SIDEBAR: HELP & SETTINGS
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar & Yardım")
    
    col_clear1, col_clear2 = st.columns(2)
    with col_clear1:
        if st.button("🔄 Tümünü Temizle", use_container_width=True):
            st.session_state.references = []
            st.session_state.editor_text = ""
            st.session_state.last_update = None
            st.success("Veriler temizlendi!")
            st.rerun()
    
    with col_clear2:
        if st.button("✂️ Metni Temizle", use_container_width=True):
            st.session_state.editor_text = ""
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 Rehber")
    
    with st.expander("🚀 Başlarken"):
        st.markdown("""
        1. **Format seçin**: Üstte alıntı formatını seçin
        2. **Metni yazın**: Sol panelde yazınızı yazın
        3. **[cite] ekleyin**: Alıntı yapmak istediğiniz yerlere [cite] yazın
        4. **Kaynak ekleyin**: Sağ panelde kaynak URL'si ekleyin
        5. **Alıntılar otomatik güncellenir**: (1), (2), vb. şeklinde
        6. **Kaynakçayı indirin**: Hazır kaynakçayı metin dosyası olarak indirin
        """)
    
    with st.expander("📋 Alıntı Formatları"):
        st.markdown("""
        **Vancouver**: Tıbbi makaleler için sayısal alıntılar
        
        **APA (Numeric)**: Sayısal referanslarla APA stili
        
        **APA (Author-Date)**: Yazar-tarih sistemi
        
        **Harvard**: İngiltere'de popüler, APA benzeri
        
        **MLA**: Modern Language Association formatı
        
        **Chicago**: Tarih ve sosyal bilimler için
        """)
    
    with st.expander("💡 İpuçları"):
        st.markdown("""
        ✅ **📌 Metin İçine Ekle**: Kaynakları doğrudan metin içine ekleyin
        
        ✅ **🔼🔽 Yeniden Sırala**: Kaynakların sırasını değiştirin
        
        ✅ **📚 Kaynakça**: Otomatik format kaynakçası oluşturulur
        
        ✅ **📋 Format Değiştir**: İstediğiniz zaman formatı değiştirebilirsiniz
        
        ✅ **⬇️ İndir**: Kaynakçayı metin dosyası olarak indirin
        """)
    
    with st.expander("🔗 Desteklenen Kaynaklar"):
        st.markdown("""
        ✅ PubMed Central  
        ✅ Google Scholar  
        ✅ DOI Bağlantıları  
        ✅ Akademik URL'ler  
        ✅ Tüm Web Kaynakları
        """)
    
    st.markdown("---")
    st.markdown(
        "<small>Akademik yazarlar için ❤️ ile yapıldı</small>",
        unsafe_allow_html=True
    )
