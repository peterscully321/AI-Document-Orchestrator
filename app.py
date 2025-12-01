"""Interactive Streamlit UI for AI Document Orchestrator."""

import asyncio
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_doc_orchestrator.models import OutputFormat, UserInput
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Document Orchestrator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_keys():
    """Check if required API keys are set."""
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not gemini_key:
        st.error("❌ GOOGLE_GEMINI_API_KEY not found in .env file")
        return False
    if not tavily_key:
        st.error("❌ TAVILY_API_KEY not found in .env file")
        return False
    return True


@st.cache_resource
def get_orchestrator():
    """Get cached orchestrator instance."""
    return DocumentOrchestrator()


def run_async(coro):
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def main():
    """Main application."""
    # Header
    st.markdown('<h1 class="main-header">📚 AI Document Orchestrator</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Choose a feature:",
        ["🏠 Home", "📝 Document Generator", "📄 Summarizer", "✍️ Blog Writer", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    # Check API keys
    if not check_api_keys():
        st.sidebar.warning("⚠️ Please configure API keys in .env file")
        return
    
    # Route to different pages
    if page == "🏠 Home":
        show_home()
    elif page == "📝 Document Generator":
        show_document_generator()
    elif page == "📄 Summarizer":
        show_summarizer()
    elif page == "✍️ Blog Writer":
        show_blog_writer()
    elif page == "⚙️ Settings":
        show_settings()


def show_home():
    """Home page."""
    st.markdown("""
    <div class="feature-card">
        <h2>Welcome to AI Document Orchestrator</h2>
        <p>Your intelligent document generation assistant powered by Google Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 Document Generator</h3>
            <p>Generate comprehensive documents on any topic with research, summarization, and quality checks.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Summarizer</h3>
            <p>Quickly summarize research content and create structured notes from raw data.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>✍️ Blog Writer</h3>
            <p>Create engaging blog posts with research-backed content and quality assurance.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Tip:** Use the sidebar to navigate to different features!")


def show_document_generator():
    """Document Generator page."""
    st.header("📝 Document Generator")
    st.markdown("Generate comprehensive documents with research, summarization, and quality checks.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "📌 Enter Topic",
            placeholder="e.g., Machine Learning Basics, Python Programming, Climate Change",
            help="The topic you want to research and write about"
        )
    
    with col2:
        output_format = st.selectbox(
            "📄 Output Format",
            ["text", "pdf", "google_docs"],
            help="Choose the output format for your document"
        )
    
    # Local files option
    with st.expander("📎 Add Local Files (Optional)"):
        uploaded_files = st.file_uploader(
            "Upload files to include in research",
            type=["txt", "md", "pdf"],
            accept_multiple_files=True,
            help="Upload local files to be included in the research phase"
        )
        local_files = []
        if uploaded_files:
            for file in uploaded_files:
                # Save uploaded file temporarily
                temp_path = f"temp_{file.name}"
                with open(temp_path, "wb") as f:
                    f.write(file.getbuffer())
                local_files.append(temp_path)
    
    if st.button("🚀 Generate Document", type="primary", use_container_width=True):
        if not topic:
            st.error("Please enter a topic!")
            return
        
        try:
            orchestrator = get_orchestrator()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Phase 1
            status_text.text("Phase 1: Gathering information...")
            progress_bar.progress(10)
            
            # Run the orchestrator
            user_input = UserInput(topic=topic, format=OutputFormat(output_format))
            
            status_text.text("Phase 2: Processing and summarizing...")
            progress_bar.progress(30)
            
            status_text.text("Phase 3: Writing and quality checking...")
            progress_bar.progress(60)
            
            result = run_async(orchestrator.process(user_input, local_files=local_files))
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Display results
            st.success("Document generated successfully!")
            
            if result.format == OutputFormat.TEXT:
                st.subheader("📄 Generated Document")
                st.text_area("Content", result.content, height=400)
                st.download_button(
                    "💾 Download as Text",
                    result.content,
                    file_name=f"{topic.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            
            elif result.format == OutputFormat.PDF:
                if result.file_path and Path(result.file_path).exists():
                    st.subheader("📄 Generated PDF")
                    with open(result.file_path, "rb") as f:
                        st.download_button(
                            "💾 Download PDF",
                            f.read(),
                            file_name=Path(result.file_path).name,
                            mime="application/pdf"
                        )
                    st.info(f"PDF saved at: {result.file_path}")
                else:
                    st.error("PDF file not found")
            
            elif result.format == OutputFormat.GOOGLE_DOCS:
                st.subheader("📄 Google Doc Created")
                st.success(f"Document created successfully!")
                if result.url:
                    st.markdown(f"🔗 [Open Document]({result.url})")
            
            # Clean up temp files
            for file_path in local_files:
                if Path(file_path).exists():
                    Path(file_path).unlink()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


def show_summarizer():
    """Summarizer page."""
    st.header("📄 Summarizer")
    st.markdown("Quickly summarize research content and create structured notes.")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["🔍 Research Topic", "📝 Paste Content"],
        horizontal=True
    )
    
    if input_method == "🔍 Research Topic":
        topic = st.text_input(
            "📌 Enter Topic to Research",
            placeholder="e.g., Artificial Intelligence, Quantum Computing",
            help="The topic you want to research and summarize"
        )
        
        if st.button("🔍 Research & Summarize", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a topic!")
                return
            
            try:
                orchestrator = get_orchestrator()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Phase 1: Research
                status_text.text("🔍 Researching topic...")
                progress_bar.progress(20)
                
                from ai_doc_orchestrator.models import AgentMessage
                research_message = AgentMessage(
                    from_agent="User",
                    to_agent="ResearchAgent",
                    phase="research",
                    data={"topic": topic, "format": "text"}
                )
                research_result = run_async(orchestrator.research_agent.process(research_message))
                
                # Phase 2: Summarize
                status_text.text("📄 Summarizing content...")
                progress_bar.progress(60)
                
                summary_message = AgentMessage(
                    from_agent="ResearchAgent",
                    to_agent="SummaryAgent",
                    phase="summary",
                    data={
                        "raw_data": research_result["raw_data"],
                        "local_files": []
                    }
                )
                summary_result = run_async(orchestrator.summary_agent.process(summary_message))
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                structured_notes = summary_result["structured_notes"]
                
                # Display results
                st.success("Summary generated successfully!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Summary")
                    st.write(structured_notes["summary"])
                
                with col2:
                    st.subheader("🔑 Key Points")
                    for point in structured_notes["key_points"]:
                        st.markdown(f"- {point}")
                
                st.subheader("📚 Sources")
                for i, source in enumerate(structured_notes["sources"][:5], 1):
                    st.markdown(f"{i}. {source}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:  # Paste Content
        content = st.text_area(
            "📝 Paste Content to Summarize",
            height=200,
            placeholder="Paste your content here...",
            help="Paste the content you want to summarize"
        )
        
        if st.button("📄 Summarize Content", type="primary", use_container_width=True):
            if not content:
                st.error("Please paste some content!")
                return
            
            try:
                orchestrator = get_orchestrator()
                
                # Create mock raw data from pasted content
                raw_data = {
                    "sources": [{"title": "Pasted Content", "url": "", "content": content}],
                    "search_queries": []
                }
                
                from ai_doc_orchestrator.models import AgentMessage
                summary_message = AgentMessage(
                    from_agent="User",
                    to_agent="SummaryAgent",
                    phase="summary",
                    data={"raw_data": raw_data, "local_files": []}
                )
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("📄 Summarizing content...")
                progress_bar.progress(50)
                
                summary_result = run_async(orchestrator.summary_agent.process(summary_message))
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                structured_notes = summary_result["structured_notes"]
                
                st.success("Summary generated successfully!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Summary")
                    st.write(structured_notes["summary"])
                
                with col2:
                    st.subheader("🔑 Key Points")
                    for point in structured_notes["key_points"]:
                        st.markdown(f"- {point}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def show_blog_writer():
    """Blog Writer page."""
    st.header("✍️ Blog Writer")
    st.markdown("Create engaging blog posts with research-backed content.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        blog_topic = st.text_input(
            "📌 Blog Topic",
            placeholder="e.g., 10 Tips for Better Python Code, Introduction to Machine Learning",
            help="The topic for your blog post"
        )
    
    with col2:
        blog_tone = st.selectbox(
            "🎨 Writing Tone",
            ["Professional", "Casual", "Friendly", "Technical", "Conversational"],
            help="The tone of voice for your blog post"
        )
    
    # Additional options
    with st.expander("⚙️ Advanced Options"):
        target_length = st.slider("Target Length (words)", 500, 3000, 1000, 100)
        include_intro = st.checkbox("Include Introduction", value=True)
        include_conclusion = st.checkbox("Include Conclusion", value=True)
    
    if st.button("✍️ Write Blog Post", type="primary", use_container_width=True):
        if not blog_topic:
            st.error("Please enter a blog topic!")
            return
        
        try:
            orchestrator = get_orchestrator()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Enhanced topic with tone
            enhanced_topic = f"{blog_topic} (Tone: {blog_tone}, Length: {target_length} words)"
            
            status_text.text("🔍 Researching topic...")
            progress_bar.progress(15)
            
            # Research phase
            from ai_doc_orchestrator.models import AgentMessage
            research_message = AgentMessage(
                from_agent="User",
                to_agent="ResearchAgent",
                phase="research",
                data={"topic": enhanced_topic, "format": "text"}
            )
            research_result = run_async(orchestrator.research_agent.process(research_message))
            
            status_text.text("📄 Summarizing research...")
            progress_bar.progress(35)
            
            # Summary phase
            summary_message = AgentMessage(
                from_agent="ResearchAgent",
                to_agent="SummaryAgent",
                phase="summary",
                data={"raw_data": research_result["raw_data"], "local_files": []}
            )
            summary_result = run_async(orchestrator.summary_agent.process(summary_message))
            
            status_text.text("✍️ Writing blog post...")
            progress_bar.progress(55)
            
            # Writer phase with blog-specific instructions
            structured_notes = summary_result["structured_notes"]
            blog_instructions = f"""
            Write a blog post about: {blog_topic}
            Tone: {blog_tone}
            Target length: {target_length} words
            Include introduction: {include_intro}
            Include conclusion: {include_conclusion}
            Make it engaging, well-structured, and suitable for a blog audience.
            """
            
            writer_message = AgentMessage(
                from_agent="SummaryAgent",
                to_agent="WriterAgent",
                phase="writing",
                data={
                    "structured_notes": structured_notes,
                    "topic": blog_topic,
                    "format": "text",
                    "version": 1,
                    "blog_instructions": blog_instructions
                }
            )
            writer_result = run_async(orchestrator.writer_agent.process(writer_message))
            
            status_text.text("✅ Quality checking...")
            progress_bar.progress(80)
            
            # QC phase
            qc_message = AgentMessage(
                from_agent="WriterAgent",
                to_agent="QCAgent",
                phase="qc",
                data={
                    "draft": writer_result["draft"],
                    "topic": blog_topic,
                    "format": "text"
                }
            )
            qc_result = run_async(orchestrator.qc_agent.process(qc_message))
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            draft = writer_result["draft"]
            
            st.success("Blog post generated successfully!")
            
            st.subheader("📝 Your Blog Post")
            st.markdown(draft["content"])
            
            st.download_button(
                "💾 Download Blog Post",
                draft["content"],
                file_name=f"{blog_topic.replace(' ', '_')}_blog.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


def show_settings():
    """Settings page."""
    st.header("⚙️ Settings")
    
    st.subheader("🔑 API Configuration")
    
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY", "")
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Google Gemini API:** {'✅ Configured' if gemini_key else '❌ Not configured'}")
        if gemini_key:
            st.success(f"Key: {gemini_key[:20]}...")
    
    with col2:
        st.info(f"**Tavily API:** {'✅ Configured' if tavily_key else '❌ Not configured'}")
        if tavily_key:
            st.success(f"Key: {tavily_key[:20]}...")
    
    st.markdown("---")
    st.subheader("📚 Model Information")
    
    orchestrator = get_orchestrator()
    st.info(f"**Current Model:** {orchestrator.model}")
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.markdown("""
    **AI Document Orchestrator** v0.1.0
    
    A multi-agent system for intelligent document generation powered by:
    - Google Gemini AI
    - Tavily Search API
    
    Features:
    - 📝 Document Generation
    - 📄 Content Summarization
    - ✍️ Blog Writing
    - 🔍 Web Research
    - ✅ Quality Assurance
    """)


if __name__ == "__main__":
    main()


