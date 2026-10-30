"""
app.py
------
Streamlit user interface for the Hinglish AI Study Buddy.
Allows Indian college students to upload lecture notes or textbook chapters,
select a summary style, preview extracted text, and get an instant Hinglish revision guide.
"""

import streamlit as st
from pdf_utils import extract_text, PDFExtractionError
from summarizer import summarize, SummarizerError


# Configure Streamlit page settings
st.set_page_config(
    page_title="Hinglish AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for clean college-student aesthetic and readable typography
CUSTOM_CSS = """
<style>
    /* Card-like styling for summary result container */
    .summary-card {
        background-color: #f8f9fa;
        border-left: 5px solid #4f46e5;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
    }
    /* Subtle metric card tweaks */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        color: #4f46e5 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Function to render UI header and introduction
# Why: Welcomes the student with clear branding and context for exam preparation.
def render_header() -> None:
    """Renders the top banner and app description."""
    st.title("📚 Hinglish AI Study Buddy")
    st.markdown(
        "**College notes aur textbook chapters ko Hinglish me summarize karo — exam revision simplified! 🎯**"
    )
    st.divider()


# Function to render student guide in the sidebar
# Why: Provides quick guidance on how to choose between Short and Detailed modes.
def render_sidebar() -> None:
    """Renders helpful study tips and instructions in the left sidebar."""
    with st.sidebar:
        st.header("💡 How It Works")
        st.markdown(
            """
            1. **PDF Upload Karo:** Typed notes ya digital textbook chapter upload karein.
            2. **Style Chuniye:**
               - ⚡ **Short (10 Points):** Last-minute revision ke liye high-yield bullet points.
               - 📖 **Detailed (Topic-wise):** Complete topic breakdown with viva/exam tips.
            3. **Instant Revision:** Natural Hinglish me concepts samjhein!
            """
        )

        st.divider()
        st.subheader("📌 Tips for Best Results")
        st.info(
            "✅ Digital/typed PDFs best kaam karti hain.\n\n"
            "⚠️ Scanned handwritten photo-PDFs me text layer nahi hoti (Week 1 limitation)."
        )

        st.divider()
        st.caption("🚀 Built for B.Tech CSE-AI | Week 1: Core Summarizer")


# Main app function
# Why: Central reactive UI coordinating upload, extraction, preview, and summarization.
def main() -> None:
    render_sidebar()
    render_header()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Step 1: PDF File Uploader
        st.subheader("1. Apni Notes PDF Upload Karein")
        uploaded_file = st.file_uploader(
            "Choose a PDF file (digital notes or typed textbook chapter)",
            type=["pdf"],
            help="Upload typed PDFs. Scanned/image-only PDFs require OCR which is planned for upcoming weeks."
        )

        # Step 2: Summary Mode Selection
        st.subheader("2. Summary Ka Style Chuniye")
        summary_mode = st.radio(
            "Kis format me summary chahiye?",
            options=["Short (10 bullet points)", "Detailed (topic-wise)"],
            index=0,
            help="Short mode quick revision ke liye best hai; Detailed mode concepts deeply samajhne ke liye."
        )

        # Action Button
        st.write("")
        generate_btn = st.button("Generate Hinglish Summary 🚀", type="primary", use_container_width=True)

    with col2:
        st.subheader("3. Hinglish Summary & Notes Preview")

        if not generate_btn:
            st.info("👈 Left side se PDF upload karein aur 'Generate Hinglish Summary' par click karein.")
            return

        if uploaded_file is None:
            st.warning("⚠️ Kripya pehle ek PDF file upload karein!")
            return

        # Show spinner during processing
        with st.spinner("Notes padh rahe hain aur mast Hinglish summary bana rahe hain... ⏳"):
            try:
                # 1. Extract text from PDF
                extracted_text = extract_text(uploaded_file)
                original_word_count = len(extracted_text.split())

                # 2. Determine mode parameter
                mode_key = "short" if "Short" in summary_mode else "detailed"

                # 3. Call summarizer module
                hinglish_summary = summarize(extracted_text, mode=mode_key)
                summary_word_count = len(hinglish_summary.split())

                # Rough estimate: Average student reads 200 words/min
                minutes_saved = max(1, round((original_word_count - summary_word_count) / 200))

                # 4. Display Quick Revision Metrics
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric(label="Original Words", value=f"~{original_word_count}")
                with m_col2:
                    st.metric(label="Summary Words", value=f"~{summary_word_count}")
                with m_col3:
                    st.metric(label="Time Saved", value=f"~{minutes_saved} min")

                st.success("🎉 Aapki Hinglish Summary Tayyar Hai!")

                # 5. Optional Extracted Text Preview
                with st.expander("🔍 Extracted Raw Text Ka Preview Dekhein", expanded=False):
                    preview_length = min(1500, len(extracted_text))
                    st.text(extracted_text[:preview_length] + ("..." if len(extracted_text) > 1500 else ""))
                    st.caption(f"Showing first {preview_length} characters of {len(extracted_text)} total.")

                st.markdown("---")
                st.markdown(hinglish_summary)

                # 6. Action buttons (Download Summary in multiple formats)
                st.markdown("---")
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.download_button(
                        label="📥 Download Text (.txt)",
                        data=hinglish_summary,
                        file_name="hinglish_summary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with d_col2:
                    st.download_button(
                        label="📥 Download Markdown (.md)",
                        data=hinglish_summary,
                        file_name="hinglish_summary.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

            except PDFExtractionError as pe:
                st.warning(f"⚠️ **PDF Issue:** {str(pe)}")
            except SummarizerError as se:
                st.error(f"❌ **Summarizer Error:** {str(se)}")
            except Exception as e:
                st.error(f"❌ **Unexpected Error:** {str(e)}")


if __name__ == "__main__":
    main()
