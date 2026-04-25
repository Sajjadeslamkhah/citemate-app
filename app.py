import streamlit as st
import re
from datetime import datetime
from typing import List, Dict, Tuple
import json

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
# CUSTOM STYLING
# ============================================================================
CUSTOM_CSS = """
<style>
    /* Overall app styling */
    * {
        font-family: 'Times New Roman', 'Times', serif;
    }
    
    /* Editor container */
    .editor-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        min-height: 600px;
        line-height: 1.5;
    }
    
    /* Reference panel */
    .reference-panel {
        background-color: #ecf0f1;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        line-height: 1.5;
    }
    
    /* Bibliography styling */
    .bibliography {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #bdc3c7;
        margin-top: 15px;
        line-height: 1.6;
    }
    
    .reference-item {
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .reference-item:last-child {
        border-bottom: none;
    }
    
    .citation-tag {
        background-color: #fff3cd;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
        color: #333;
        font-family: 'Courier New', monospace;
    }
    
    .citation-number {
        background-color: #d4edda;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: bold;
        color: #155724;
        font-family: 'Courier New', monospace;
    }
    
    /* Heading styles */
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
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'Times New Roman', 'Times', serif;
        line-height: 1.5;
    }
    
    /* Button styling */
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
    
    /* Warning/Info boxes */
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: #ecf0f1;
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
    if 'citation_format' not in st.session_state:
        st.session_state.citation_format = "Vancouver"
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

initialize_session_state()

# ============================================================================
# CITATION FORMATTING FUNCTIONS
# ============================================================================
def format_citation(source_url: str, format_type: str) -> str:
    """
    Format a citation based on the selected format.
    
    Args:
        source_url: The URL or DOI of the source
        format_type: The citation format (Vancouver, APA, Harvard, MLA)
    
    Returns:
        Formatted citation string
    """
    # Extract domain/title from URL for display
    if "pubmed" in source_url.lower():
        source_name = "PubMed Central"
    elif "scholar" in source_url.lower():
        source_name = "Google Scholar"
    elif "doi.org" in source_url.lower():
        source_name = f"DOI: {source_url.split('doi.org/')[-1]}"
    else:
        # Extract domain name
        source_name = source_url.replace("https://", "").replace("http://", "").split("/")[0]
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    if format_type == "Vancouver":
        return f"{source_name}. Available from: {source_url}. [Accessed {timestamp}]."
    elif format_type == "APA":
        return f"Retrieved from {source_url} on {timestamp}."
    elif format_type == "Harvard":
        return f"[online] Available at: {source_url} (Accessed: {timestamp})."
    elif format_type == "MLA":
        return f"{source_name}, www.{source_name.lower()}.com. Accessed {timestamp}."
    else:
        return f"{source_name}. {source_url}"

# ============================================================================
# CITATION REPLACEMENT ENGINE
# ============================================================================
def replace_cite_tags(text: str, num_references: int) -> str:
    """
    Replace [cite] placeholders with numerical citations (1), (2), etc.
    Only replaces as many tags as there are references.
    
    Args:
        text: The original text with [cite] placeholders
        num_references: The number of references available
    
    Returns:
        Text with [cite] tags replaced by numerical citations
    """
    if num_references == 0:
        return text
    
    # Find all [cite] tags
    cite_pattern = r'\[cite\]'
    cite_matches = list(re.finditer(cite_pattern, text))
    
    # Only replace as many [cite] tags as there are references
    replacements_to_make = min(len(cite_matches), num_references)
    
    result = text
    # Replace from the end to the beginning to avoid index shifting
    for i in range(replacements_to_make - 1, -1, -1):
        match = cite_matches[i]
        citation_number = i + 1
        result = (
            result[:match.start()] +
            f"({citation_number})" +
            result[match.end():]
        )
    
    return result

def highlight_cite_preview(text: str) -> str:
    """
    Create a preview version of the text with visual highlighting of cite tags.
    
    Args:
        text: The text to highlight
    
    Returns:
        HTML string with highlighted cite tags
    """
    # Escape HTML and highlight [cite] tags
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
def add_reference(url: str, format_type: str) -> bool:
    """
    Add a new reference to the session state.
    
    Args:
        url: The source URL
        format_type: The citation format
    
    Returns:
        True if reference was added successfully
    """
    if not url or not url.strip():
        st.error("Please enter a valid URL")
        return False
    
    # Validate URL format
    if not (url.startswith("http://") or url.startswith("https://") or "doi" in url.lower()):
        st.error("Please enter a valid URL (starting with http/https or containing DOI)")
        return False
    
    # Check for duplicates
    if any(ref['url'] == url for ref in st.session_state.references):
        st.warning("This source has already been added")
        return False
    
    # Create reference object
    reference = {
        'id': len(st.session_state.references) + 1,
        'url': url,
        'format': format_type,
        'formatted_citation': format_citation(url, format_type),
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
    """Move a reference up in the list."""
    refs = st.session_state.references
    for i, ref in enumerate(refs):
        if ref['id'] == ref_id and i > 0:
            refs[i], refs[i-1] = refs[i-1], refs[i]
            st.session_state.last_update = datetime.now()
            break

def move_reference_down(ref_id: int):
    """Move a reference down in the list."""
    refs = st.session_state.references
    for i, ref in enumerate(refs):
        if ref['id'] == ref_id and i < len(refs) - 1:
            refs[i], refs[i+1] = refs[i+1], refs[i]
            st.session_state.last_update = datetime.now()
            break

# ============================================================================
# MAIN LAYOUT
# ============================================================================
# Header
st.markdown("# 📚 Citemate")
st.markdown("### Professional Academic Citation Management for Streamlit")
st.markdown("---")

# Create two-column layout
col_left, col_right = st.columns([6, 4], gap="large")

# ============================================================================
# LEFT COLUMN: ACADEMIC EDITOR
# ============================================================================
with col_left:
    st.markdown("### ✍️ Academic Editor")
    
    # Text editor
    editor_text = st.text_area(
        label="Write your academic content here",
        value=st.session_state.editor_text,
        height=600,
        placeholder="Start writing your academic paper...\n\nUse [cite] as a placeholder for citations that will be numbered automatically.",
        help="Use [cite] as a placeholder. It will be replaced with numbered citations (1), (2), etc.",
        key="text_input"
    )
    
    # Update session state
    st.session_state.editor_text = editor_text
    
    # Preview section with dynamic citation replacement
    st.markdown("### 📖 Live Preview")
    
    num_refs = len(st.session_state.references)
    processed_text = replace_cite_tags(editor_text, num_refs)
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
        st.metric("Word Count", word_count)
    with col_stats2:
        cite_count = len(re.findall(r'\[cite\]', editor_text))
        st.metric("Citation Placeholders", cite_count)
    with col_stats3:
        ref_count = len(st.session_state.references)
        st.metric("References Added", ref_count)

# ============================================================================
# RIGHT COLUMN: SOURCE & REFERENCE MANAGEMENT
# ============================================================================
with col_right:
    st.markdown("### 📖 Source & Reference Management")
    
    # Input section
    st.markdown("#### Add New Source")
    
    input_col1, input_col2 = st.columns([3, 2])
    
    with input_col1:
        source_url = st.text_input(
            label="Source URL",
            placeholder="https://pubmed.ncbi.nlm.nih.gov/... or DOI link",
            help="Enter PubMed, Google Scholar, DOI, or any academic source URL"
        )
    
    with input_col2:
        citation_format = st.selectbox(
            label="Citation Format",
            options=["Vancouver", "APA", "Harvard", "MLA"],
            index=0,
            help="Select your preferred citation format"
        )
    
    # Add source button
    if st.button("➕ Add Source", use_container_width=True, type="primary"):
        if add_reference(source_url, citation_format):
            st.success("Source added successfully! 📎")
            st.rerun()
        else:
            st.error("Failed to add source. Please check the URL.")
    
    st.markdown("---")
    
    # References list
    st.markdown("#### 📋 References")
    
    if st.session_state.references:
        # Display count
        st.info(f"**Total References: {len(st.session_state.references)}**")
        
        # Create a bibliography container
        st.markdown('<div class="bibliography">', unsafe_allow_html=True)
        
        for idx, ref in enumerate(st.session_state.references, 1):
            with st.container():
                st.markdown(f'<div class="reference-item">', unsafe_allow_html=True)
                
                # Reference number and formatted citation
                st.markdown(f"**({idx})** {ref['formatted_citation']}")
                
                # Source URL
                st.markdown(f"<small>**Source:** {ref['url']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small>**Format:** {ref['format']}</small>", unsafe_allow_html=True)
                
                # Action buttons
                button_col1, button_col2, button_col3, button_col4 = st.columns(4)
                
                with button_col1:
                    if st.button(
                        "🔼",
                        key=f"up_{ref['id']}",
                        help="Move up",
                        use_container_width=True
                    ):
                        move_reference_up(ref['id'])
                        st.rerun()
                
                with button_col2:
                    if st.button(
                        "🔽",
                        key=f"down_{ref['id']}",
                        help="Move down",
                        use_container_width=True
                    ):
                        move_reference_down(ref['id'])
                        st.rerun()
                
                with button_col3:
                    if st.button(
                        "📋",
                        key=f"copy_{ref['id']}",
                        help="Copy citation",
                        use_container_width=True
                    ):
                        st.write(f"Copy this: `({idx})`")
                
                with button_col4:
                    if st.button(
                        "🗑️",
                        key=f"delete_{ref['id']}",
                        help="Delete reference",
                        use_container_width=True
                    ):
                        remove_reference(ref['id'])
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export section
        st.markdown("---")
        st.markdown("#### 💾 Export Bibliography")
        
        # Generate formatted bibliography
        bibliography_text = "**References**\n\n"
        for idx, ref in enumerate(st.session_state.references, 1):
            bibliography_text += f"{idx}. {ref['formatted_citation']}\n\n"
        
        # Copy to clipboard button
        if st.button("📋 Copy Bibliography", use_container_width=True):
            st.code(bibliography_text, language="text")
        
        # Download as text
        st.download_button(
            label="⬇️ Download Bibliography (TXT)",
            data=bibliography_text,
            file_name="bibliography.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    else:
        st.info("📌 No references added yet. Add your first source above to get started!")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(
        "<small>**Citemate v1.0** | Professional Citation Management</small>",
        unsafe_allow_html=True
    )

with footer_col2:
    if st.session_state.last_update:
        update_time = st.session_state.last_update.strftime("%H:%M:%S")
        st.markdown(f"<small>Last updated: {update_time}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small>Ready to start</small>", unsafe_allow_html=True)

with footer_col3:
    st.markdown(
        "<small>💡 Tip: Use [cite] for each citation you want to add</small>",
        unsafe_allow_html=True
    )

# ============================================================================
# SIDEBAR: HELP & SETTINGS
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings & Help")
    
    # Clear all data option
    if st.button("🔄 Clear All Data", use_container_width=True):
        st.session_state.references = []
        st.session_state.editor_text = ""
        st.session_state.last_update = None
        st.success("All data cleared!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 How to Use Citemate")
    
    with st.expander("Getting Started"):
        st.markdown("""
        1. **Write your content** in the left panel
        2. **Add `[cite]` placeholders** where you want citations
        3. **Add sources** in the right panel using URLs
        4. **Citations update automatically** as numbered references
        5. **Export your bibliography** when ready
        """)
    
    with st.expander("Citation Formats"):
        st.markdown("""
        - **Vancouver**: Numeric citations, common in medical papers
        - **APA**: Author-date system, widely used in social sciences
        - **Harvard**: Similar to APA, popular in UK institutions
        - **MLA**: Modern Language Association format
        """)
    
    with st.expander("Tips & Tricks"):
        st.markdown("""
        - **Reorder references** using up/down arrows
        - **View live preview** as you type
        - **Word count** updates automatically
        - **Only matched citations** are replaced (e.g., 3 sources = first 3 [cite] tags replaced)
        - **Export bibliography** in plain text format
        """)
    
    with st.expander("Supported Sources"):
        st.markdown("""
        ✅ PubMed Central  
        ✅ Google Scholar  
        ✅ DOI links  
        ✅ Any academic URL  
        """)
    
    st.markdown("---")
    st.markdown(
        "<small>Made with ❤️ for academic writers</small>",
        unsafe_allow_html=True
    )
