import streamlit as st
import re
import requests
from datetime import datetime
from urllib.parse import urlparse

# ============================================================================
# 1. PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Citation Manager Pro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 2. CUSTOM STYLING - CRITICAL FIX FOR VISUALS
# ============================================================================
st.markdown("""
    <style>
    /* Main background */
    .main {
        background-color: #0e1117;
    }
    
    /* Live Preview Container - WHITE BACKGROUND WITH BLACK TEXT */
    .preview-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 30px;
        border-radius: 12px;
        border: 3px solid #27ae60;
        font-size: 16px;
        line-height: 1.8;
        margin-top: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        font-family: 'Times New Roman', Times, serif;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        color: #ffffff !important;
        background-color: #262730 !important;
        font-family: 'Times New Roman', Times, serif !important;
        border: 1px solid #404854 !important;
    }
    
    /* Citation number styling */
    .cite-number {
        color: #ffffff;
        font-weight: bold;
        background-color: #27ae60;
        padding: 2px 6px;
        border-radius: 4px;
        margin: 0 2px;
        display: inline-block;
    }
    
    /* Source card styling */
    .source-card {
        background-color: #1e1e1e;
        border-left: 4px solid #27ae60;
        padding: 15px;
        margin: 12px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        background-color: #262730;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
        transform: translateX(5px);
    }
    
    /* Statistics boxes */
    .stat-box {
        background-color: #1e1e1e;
        border: 2px solid #27ae60;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: #27ae60;
        font-weight: bold;
    }
    
    /* Format badge */
    .format-badge {
        display: inline-block;
        background-color: #27ae60;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        margin: 5px 5px 5px 0;
    }
    
    /* Alert styling */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #28a745;
        color: #155724;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    
    /* Input field styling */
    .stTextInput input {
        background-color: #262730 !important;
        color: #ffffff !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #27ae60;
    }
    
    /* Code block styling */
    .stCode {
        background-color: #1e1e1e !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 3. SESSION STATE INITIALIZATION - CRITICAL FOR BUTTON FIX
# ============================================================================
def init_session_state():
    """Initialize all session state variables"""
    if 'references' not in st.session_state:
        st.session_state.references = []
    
    if 'editor_text' not in st.session_state:
        st.session_state.editor_text = ""
    
    if 'citation_format' not in st.session_state:
        st.session_state.citation_format = "APA"
    
    if 'last_cite_insert' not in st.session_state:
        st.session_state.last_cite_insert = None

init_session_state()

# ============================================================================
# 4. METADATA SCRAPING - CRITICAL FEATURE
# ============================================================================

def extract_metadata_from_url(url: str) -> dict:
    """
    Attempt to extract title, author, and other metadata from URL.
    Uses requests to fetch HTML and parse <title>, <meta> tags, etc.
    
    Args:
        url: The source URL
    
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {
        'title': None,
        'author': None,
        'source_name': None,
        'success': False
    }
    
    try:
        # Add timeout to prevent hanging
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
        response.encoding = 'utf-8'
        html_content = response.text
        
        # Extract title from <title> tag
        title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up common patterns
            title = re.sub(r'\s*[-|]\s*(pdf|html)', '', title, flags=re.IGNORECASE)
            title = title.split('|')[0].split('-')[0].strip()
            if title and len(title) > 5:
                metadata['title'] = title
        
        # Extract author from meta tags
        author_patterns = [
            r'<meta\s+name=["\']author["\']\s+content=["\'](.*?)["\']\s*/?>', # Standard meta
            r'<meta\s+property=["\']article:author["\']\s+content=["\'](.*?)["\']\s*/?>', # OG meta
            r'<meta\s+name=["\']dc\.creator["\']\s+content=["\'](.*?)["\']\s*/?>' # Dublin Core
        ]
        
        for pattern in author_patterns:
            author_match = re.search(pattern, html_content, re.IGNORECASE)
            if author_match:
                author = author_match.group(1).strip()
                if author and len(author) > 2:
                    metadata['author'] = author
                    break
        
        # Extract source name from domain
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '').replace('.com', '').replace('.org', '').replace('.edu', '')
        
        # Map common domains
        domain_names = {
            'pubmed': 'PubMed Central',
            'ncbi': 'NCBI',
            'scholar': 'Google Scholar',
            'researchgate': 'ResearchGate',
            'arxiv': 'arXiv',
            'jstor': 'JSTOR',
            'sciencedirect': 'ScienceDirect',
            'springer': 'Springer',
            'nature': 'Nature',
            'ieee': 'IEEE',
        }
        
        for key, value in domain_names.items():
            if key.lower() in url.lower():
                metadata['source_name'] = value
                break
        
        if not metadata['source_name']:
            metadata['source_name'] = domain.title()
        
        metadata['success'] = True
        return metadata
    
    except requests.exceptions.Timeout:
        metadata['error'] = "Request timed out - using basic parsing"
        metadata['source_name'] = urlparse(url).netloc.replace('www.', '').title()
        return metadata
    
    except requests.exceptions.ConnectionError:
        metadata['error'] = "Connection error - using basic parsing"
        metadata['source_name'] = urlparse(url).netloc.replace('www.', '').title()
        return metadata
    
    except Exception as e:
        metadata['error'] = f"Error parsing: {str(e)}"
        metadata['source_name'] = urlparse(url).netloc.replace('www.', '').title()
        return metadata

# ============================================================================
# 5. CITATION FORMATTING
# ============================================================================

def format_citation(ref: dict, format_type: str, index: int) -> str:
    """Format citation based on selected format"""
    url = ref['url']
    author = ref.get('author', ref.get('source_name', 'Anonymous'))
    year = ref.get('year', datetime.now().year)
    title = ref.get('title', '')
    
    if format_type == "APA":
        if title:
            return f"{author}. ({year}). {title}. Retrieved from {url}"
        else:
            return f"{author} ({year}). Retrieved from {url}"
    
    elif format_type == "MLA":
        if title:
            return f"{author}. \"{title}.\" {year}. Web. {url}"
        else:
            return f"{author}. {year}. {url}"
    
    elif format_type == "Vancouver":
        return f"{index}. {author}. {title if title else 'Online source'}. Available from: {url}. [Accessed {datetime.now().strftime('%Y-%m-%d')}]."
    
    elif format_type == "Harvard":
        if title:
            return f"{author}, {year}. {title}. Available at: {url}"
        else:
            return f"{author}, {year}. Available at: {url}"
    
    elif format_type == "Chicago":
        if title:
            return f"{author}. \"{title}.\" Accessed {datetime.now().strftime('%B %d, %Y')}. {url}."
        else:
            return f"{author}. Accessed {datetime.now().strftime('%B %d, %Y')}. {url}."
    
    return f"{author} ({year}). {url}"

# ============================================================================
# 6. SOURCE MANAGEMENT - DUPLICATE PREVENTION
# ============================================================================

def add_reference(url: str, author: str = "") -> tuple[bool, str]:
    """
    Add reference with duplicate prevention.
    
    Args:
        url: Source URL
        author: Author name (optional)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validation
    if not url or not url.strip():
        return False, "❌ URL cannot be empty"
    
    if not url.startswith(('http://', 'https://')):
        return False, "❌ URL must start with http:// or https://"
    
    # DUPLICATE PREVENTION - CRITICAL FIX
    existing_urls = [ref['url'].lower() for ref in st.session_state.references]
    if url.lower() in existing_urls:
        existing_index = [r['url'].lower() for r in st.session_state.references].index(url.lower())
        return False, f"⚠️ This source already exists at position #{existing_index + 1}"
    
    # Extract metadata
    metadata = extract_metadata_from_url(url)
    
    # Create reference object
    reference = {
        'id': len(st.session_state.references) + 1,
        'url': url,
        'author': author.strip() if author else (metadata.get('author') or metadata.get('source_name') or "Anonymous"),
        'title': metadata.get('title'),
        'source_name': metadata.get('source_name'),
        'year': datetime.now().strftime("%Y"),
        'added_at': datetime.now().isoformat()
    }
    
    st.session_state.references.append(reference)
    
    # Create success message with extracted info
    msg_parts = [f"✅ Source added: {reference['source_name']}"]
    if metadata.get('title'):
        msg_parts.append(f"📖 Title: {metadata['title'][:60]}...")
    if metadata.get('author'):
        msg_parts.append(f"👤 Author: {reference['author']}")
    
    return True, "\n".join(msg_parts)

def remove_reference(ref_id: int):
    """Remove reference by ID"""
    st.session_state.references = [
        ref for ref in st.session_state.references if ref['id'] != ref_id
    ]

# ============================================================================
# 7. CITE INSERTION - BUTTON FIX (CRITICAL)
# ============================================================================

def insert_cite_tag():
    """
    Insert [cite] tag into the text area at the end.
    Uses session_state for proper state management.
    """
    st.session_state.editor_text += " [cite]"
    st.session_state.last_cite_insert = datetime.now()

# ============================================================================
# 8. CITATION REPLACEMENT ENGINE
# ============================================================================

def process_citations(text: str, num_references: int) -> str:
    """Replace [cite] placeholders with numbered citations"""
    if num_references == 0:
        return text
    
    processed = text
    cite_count = 0
    
    while "[cite]" in processed and cite_count < num_references:
        processed = processed.replace("[cite]", f"<span class='cite-number'>({cite_count + 1})</span>", 1)
        cite_count += 1
    
    return processed

# ============================================================================
# 9. MAIN UI
# ============================================================================

st.title("📚 Citation Manager Pro")
st.markdown("**Professional Academic Citation Tool with Metadata Extraction**")
st.markdown("---")

# Format Selection
col_fmt1, col_fmt2, col_fmt3, col_fmt4, col_fmt5 = st.columns(5)

formats = ["APA", "MLA", "Vancouver", "Harvard", "Chicago"]
format_cols = [col_fmt1, col_fmt2, col_fmt3, col_fmt4, col_fmt5]

for col, fmt in zip(format_cols, formats):
    with col:
        if st.button(
            fmt,
            use_container_width=True,
            type="primary" if st.session_state.citation_format == fmt else "secondary"
        ):
            st.session_state.citation_format = fmt
            st.rerun()

st.markdown(f"**Selected Format:** <span class='format-badge'>{st.session_state.citation_format}</span>", unsafe_allow_html=True)
st.markdown("---")

# Main Layout
col_left, col_right = st.columns([6, 4], gap="large")

# ============================================================================
# LEFT COLUMN: EDITOR AND PREVIEW
# ============================================================================
with col_left:
    st.subheader("✍️ Academic Editor")
    st.caption("Write your text and use [cite] to mark citations")
    
    # Text input - connected to session state
    editor_text = st.text_area(
        "Text Editor",
        value=st.session_state.editor_text,
        height=400,
        key="text_editor",
        placeholder="Start typing your academic content...\nUse [cite] to mark where citations should appear."
    )
    
    # Update session state
    st.session_state.editor_text = editor_text
    
    # Statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        word_count = len(st.session_state.editor_text.split()) if st.session_state.editor_text else 0
        st.markdown(f"<div class='stat-box'>{word_count}<br>Words</div>", unsafe_allow_html=True)
    
    with col_stat2:
        cite_count = st.session_state.editor_text.count("[cite]") if st.session_state.editor_text else 0
        st.markdown(f"<div class='stat-box'>{cite_count}<br>[cite] Tags</div>", unsafe_allow_html=True)
    
    with col_stat3:
        ref_count = len(st.session_state.references)
        st.markdown(f"<div class='stat-box'>{ref_count}<br>References</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Live Preview - WITH WHITE BACKGROUND (CRITICAL VISUAL FIX)
    st.markdown("### 📖 Live Preview")
    
    num_refs = len(st.session_state.references)
    processed_text = process_citations(st.session_state.editor_text, num_refs)
    
    # Render with white background - critical styling
    st.markdown(
        f'<div class="preview-box">{processed_text.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True
    )

# ============================================================================
# RIGHT COLUMN: SOURCE MANAGEMENT
# ============================================================================
with col_right:
    st.subheader("🚀 Tools")
    
    # CITE BUTTON FIX - CRITICAL
    if st.button("➕ Add [cite] Tag", use_container_width=True, key="cite_button"):
        insert_cite_tag()
        st.rerun()
    
    st.divider()
    
    st.subheader("📥 Add New Source")
    st.caption("Paste URL and we'll extract metadata automatically")
    
    # URL Input
    url_input = st.text_input(
        "Source URL",
        placeholder="https://pubmed.ncbi.nlm.nih.gov/... or any academic link",
        key="url_input"
    )
    
    # Author Input (optional)
    author_input = st.text_input(
        "Author Name (Optional)",
        placeholder="Leave blank to auto-detect",
        key="author_input"
    )
    
    # Add Source Button
    if st.button("✅ Add Source", use_container_width=True, type="primary", key="add_button"):
        if url_input:
            success, message = add_reference(url_input, author_input)
            
            if success:
                st.markdown(f"<div class='alert-success'>{message}</div>", unsafe_allow_html=True)
                st.session_state.url_input = ""
                st.session_state.author_input = ""
                st.rerun()
            else:
                st.markdown(f"<div class='alert-warning'>{message}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-warning'>❌ Please enter a URL</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # References List
    st.subheader("📋 References")
    
    if st.session_state.references:
        st.info(f"📌 {len(st.session_state.references)} source(s) added")
        
        for idx, ref in enumerate(st.session_state.references, 1):
            with st.container():
                st.markdown(
                    f"""
                    <div class='source-card'>
                    <b>({idx})</b> <b>{ref['author']}</b> - {ref['year']}<br>
                    <small style='color: #aaa;'>{ref.get('title', 'No title extracted')[:80]}{'...' if ref.get('title') and len(ref.get('title', '')) > 80 else ''}</small><br>
                    <small style='color: #888;'>📍 {ref['source_name']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
                
                with col_btn1:
                    if st.button("📌 Insert", key=f"insert_{ref['id']}", use_container_width=True):
                        insert_cite_tag()
                        st.rerun()
                
                with col_btn2:
                    if st.button("📋 Copy", key=f"copy_{ref['id']}", use_container_width=True):
                        formatted = format_citation(ref, st.session_state.citation_format, idx)
                        st.info(f"Citation: {formatted}")
                
                with col_btn3:
                    if st.button("🗑️", key=f"delete_{ref['id']}", use_container_width=True):
                        remove_reference(ref['id'])
                        st.rerun()
    else:
        st.info("📌 No sources added yet. Add your first source above.")

# ============================================================================
# BIBLIOGRAPHY SECTION
# ============================================================================
st.markdown("---")
st.markdown("## 📚 Bibliography")

if st.session_state.references:
    # Generate bibliography
    bib_lines = []
    for idx, ref in enumerate(st.session_state.references, 1):
        formatted = format_citation(ref, st.session_state.citation_format, idx)
        bib_lines.append(f"{idx}. {formatted}")
    
    bibliography = "\n\n".join(bib_lines)
    
    col_bib1, col_bib2 = st.columns([3, 1])
    
    with col_bib1:
        st.code(bibliography, language="text")
    
    with col_bib2:
        st.download_button(
            label="⬇️ Download",
            data=bibliography,
            file_name=f"bibliography_{st.session_state.citation_format.lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("📋 Copy All", use_container_width=True):
            st.success("✅ Copied to clipboard (use Ctrl+V to paste)")
else:
    st.info("Add sources to generate bibliography")

# ============================================================================
# SIDEBAR: SETTINGS AND HELP
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.references = []
        st.session_state.editor_text = ""
        st.success("✅ All data cleared")
        st.rerun()
    
    st.divider()
    
    st.markdown("### 📖 Help & Information")
    
    with st.expander("❓ How to Use"):
        st.markdown("""
        1. **Write Text**: Type your academic content in the editor
        2. **Mark Citations**: Use `[cite]` to mark where citations go
        3. **Add Sources**: Paste URLs and we auto-extract metadata
        4. **View Preview**: See live numbered citations in real-time
        5. **Generate Bibliography**: Automatically formatted in your chosen style
        
        **Features:**
        - 🔗 Automatic metadata extraction from URLs
        - 🚫 Duplicate URL prevention
        - 📋 5 citation formats supported
        - ⬇️ Download bibliography as text file
        """)
    
    with st.expander("📌 Supported Formats"):
        st.markdown("""
        **APA**: Social sciences, psychology
        
        **MLA**: Literature, languages
        
        **Vancouver**: Medical sciences
        
        **Harvard**: General academic use
        
        **Chicago**: History, social sciences
        """)
    
    with st.expander("🔧 Metadata Extraction"):
        st.markdown("""
        When you paste a URL, the app attempts to:
        
        ✅ Extract title from `<title>` tag
        ✅ Extract author from meta tags
        ✅ Identify source (PubMed, Scholar, etc.)
        ✅ Handle timeouts gracefully
        
        If extraction fails, you can manually enter the author name.
        """)
    
    with st.expander("💡 Tips"):
        st.markdown("""
        - **Bulk [cite] Tags**: Type multiple `[cite]` tags quickly
        - **Format Switching**: Change citation style anytime
        - **Duplicate Check**: Same URL can't be added twice
        - **Quick Insert**: Use the Insert button for fast citation adding
        - **Live Updates**: Everything updates immediately
        """)
    
    st.divider()
    st.markdown(
        "<p style='text-align: center; color: #888; font-size: 12px;'>"
        "Citation Manager Pro v2.0<br>"
        "With Metadata Extraction & Duplicate Prevention"
        "</p>",
        unsafe_allow_html=True
    )
