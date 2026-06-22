import streamlit as st
import base64



from modules.pdf_processor import extract_text
from modules.metadata_extractor import extract_metadata, detect_abstract
from modules.text_analyzer import (
    extract_main_content,
    summarize,
    detect_problem_statement,
    detect_research_objective,
    detect_key_contribution
)
from modules.section_parser import extract_sections
from modules.paper_classifier import classify_domain, classify_type
from utils.text_cleaner import clean_text, clean_summary_text

# ------------------------------------------------
# THEME INITIALIZATION
# ------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="PaperLens",
    page_icon="📄",
    layout="wide"
)

# ------------------------------------------------
# LOAD CSS
# ------------------------------------------------

with open("assets/styles.css") as f:
    css = f.read()

if st.session_state.theme == "dark":
    dark_theme = """
    .stApp {
        background-color: #0f172a;
        color: white;
    }

    .navbar {
        background: #111827;
        color: white;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }

    .insight-card {
        background: #1e293b;
        color: white;
        border: 1px solid #334155;
    }

    .stFileUploader {
        background: #1e293b;
        color: white;
    }

    .stSelectbox > div > div {
        background: #1e293b;
        color: white;
    }

    iframe {
        border: 1px solid #334155;
    }
    """

    css += dark_theme

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
# ------------------------------------------------
# THEME TOGGLE
# ------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "light"

col1, col2 = st.columns([8, 1])

with col2:
    theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"

# Toggle function
def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

# Theme button
st.button(theme_icon, on_click=toggle_theme)
# ------------------------------------------------
# NAVBAR
# ------------------------------------------------

st.markdown("""
<div class="navbar">
📄 PaperLens
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("""
<div style='text-align:center;margin-top:30px;margin-bottom:40px'>
<h1>🤖 Intelligent Research Paper Analyzer</h1>
<p style='font-size:18px'>
Upload a research paper and instantly extract insights using AI
</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------
# UPLOAD SECTION
# ------------------------------------------------

st.markdown("## 📥 Upload Research Paper")

col1, col2, col3 = st.columns([1,2,1])

with col2:

    uploaded_file = st.file_uploader(
        "Upload Research Paper PDF",
        type=["pdf"]
    )

    if uploaded_file:

        st.subheader("📄 Paper Preview")

        # Reset file pointer and get bytes safely
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.getvalue()

        b64_pdf = base64.b64encode(pdf_bytes).decode()

        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{b64_pdf}"
        width="100%" height="500"></iframe>
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

    summary_length = st.selectbox(
        "Select Summary Length",
        ["Short", "Medium", "Detailed"]
    )

    analyze_button = st.button(
        "🔍 Analyze Paper",
        use_container_width=True
    )


# ------------------------------------------------
# MAIN ANALYSIS
# ------------------------------------------------

if uploaded_file and analyze_button:

    with st.spinner("Analyzing Research Paper..."):

        text, num_pages = extract_text(uploaded_file)

        word_count = len(text.split())

        title, authors, year = extract_metadata(text)

        abstract = detect_abstract(text)

        cleaned_text = clean_text(text)

        main_content = extract_main_content(cleaned_text)

        sections = extract_sections(cleaned_text)

        # SUMMARY
        if abstract and len(abstract) > 100:
            summary_text = abstract + "\n\n" + main_content
        else:
            summary_text = main_content

        summary = summarize(summary_text, summary_length)

        problem_statement = detect_problem_statement(main_content)

        research_objective = detect_research_objective(main_content)

        key_contribution = detect_key_contribution(main_content)

        domain = classify_domain(cleaned_text)

        paper_type = classify_type(cleaned_text)

    st.success("Analysis Complete!")


# ------------------------------------------------
# TABS
# ------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Paper Info",
        "🧠 Summary",
        "📑 Section-wise Summary",
        "📚 Full Text"
    ])


# ------------------------------------------------
# TAB 1
# ------------------------------------------------

    with tab1:

        st.subheader("Paper Metadata")

        st.write("**Title:**", title)
        st.write("**Authors:**", authors)
        st.write("**Year:**", year)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Pages", num_pages)

        with col2:
            st.metric("Word Count", word_count)

        st.divider()

        st.subheader("📌 Paper Classification")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"<div class='insight-card'><b>Domain</b><br>{domain}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='insight-card'><b>Type</b><br>{paper_type}</div>", unsafe_allow_html=True)


# ------------------------------------------------
# TAB 2
# ------------------------------------------------

    with tab2:

        st.subheader("AI Generated Summary")

        st.success(summary)

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🔎 Problem Statement")
            st.markdown(f"<div class='insight-card'>{problem_statement}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("### 🎯 Research Objective")
            st.markdown(f"<div class='insight-card'>{research_objective}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("### 📊 Key Contribution")
            st.markdown(f"<div class='insight-card'>{key_contribution}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.download_button(
            "⬇ Download Summary",
            summary,
            file_name="research_summary.txt",
            use_container_width=True
        )


# ------------------------------------------------
# TAB 3
# ------------------------------------------------

    # ------------------------------------------------
# TAB 3 - SECTION-WISE SUMMARY
# ------------------------------------------------

    with tab3:

        st.subheader("📑 Section-wise Summary")

        if sections and len(sections) > 0:

            for name, content in sections.items():
                if not content or len(content.strip()) < 100:
                    continue

                # Generate AI summary for each section
                section_summary = summarize(content[:7000], summary_length)
                section_summary = clean_summary_text(section_summary)

                # Nice consistent card design
                st.markdown(f"""
                <div class="insight-card">
                    <h4 style="color: #1e40af; margin-top: 0; border-bottom: 2px solid #bfdbfe; padding-bottom: 10px;">
                        {name}
                    </h4>
                    <p style="line-height: 1.7; color: #374151;">{section_summary}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.info("No clear sections detected in this paper. Try with a different research paper.")


# ------------------------------------------------
# TAB 4
# ------------------------------------------------

    with tab4:

        with st.expander("View Extracted Text"):

            st.write(cleaned_text[:5000])


# ------------------------------------------------
# FOOTER
# ------------------------------------------------

st.markdown("""
<hr>
<p style='text-align:center;color:gray'>
PaperLens
</p>
""", unsafe_allow_html=True)