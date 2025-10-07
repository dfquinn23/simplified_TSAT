#!/usr/bin/env python3
"""
Tech Stack Audit Tool - Streamlit Dashboard
Simple web interface for uploading CSVs and running audits
"""

from simple_audit import TechStackAudit
import streamlit as st
import pandas as pd
import asyncio
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Page config
st.set_page_config(
    page_title="Tech Stack Audit Tool",
    page_icon="🔧",
    layout="wide"
)

# Initialize session state
if 'audit_complete' not in st.session_state:
    st.session_state.audit_complete = False
if 'report_path' not in st.session_state:
    st.session_state.report_path = None
if 'report_content' not in st.session_state:
    st.session_state.report_content = None

# Header
st.title("🔧 Tech Stack Audit Tool")
st.markdown("**Automated software update research and integration analysis**")
st.divider()

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    client_name = st.text_input(
        "Client Name",
        placeholder="e.g., Acme Financial",
        help="Name of the client for the report"
    )

    years = st.slider(
        "Research Window (Years)",
        min_value=1,
        max_value=5,
        value=2,
        help="How many years back to research updates"
    )

    depth = st.selectbox(
        "Research Depth",
        options=["quick", "medium", "deep"],
        index=1,
        help="Quick: Basic research | Medium: Balanced | Deep: Comprehensive"
    )

    st.divider()

    st.markdown("### 📋 Requirements")
    st.markdown("""
    Your CSV must have:
    - Tool Name
    - Category
    - Used By
    - Criticality
    """)

    st.markdown("### 🎯 What This Does")
    st.markdown("""
    1. Research tool updates
    2. Identify automation opportunities
    3. Generate n8n workflow specs
    4. Create client-ready report
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload CSV")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your tech stack inventory CSV"
    )

    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_csv_path = temp_dir / f"upload_{timestamp}.csv"

        with open(temp_csv_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Preview the CSV
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        try:
            df = pd.read_csv(temp_csv_path)

            st.subheader("📊 CSV Preview")
            st.dataframe(df, use_container_width=True)

            st.metric("Total Tools", len(df))

            # Validate required columns
            required_cols = {"Tool Name", "Category", "Used By", "Criticality"}
            missing_cols = required_cols - set(df.columns)

            if missing_cols:
                st.error(f"❌ Missing required columns: {missing_cols}")
            else:
                st.success("✅ All required columns present")

                # Run audit button
                if st.button("🚀 Run Audit", type="primary", disabled=not client_name):
                    if not client_name:
                        st.warning(
                            "⚠️ Please enter a client name in the sidebar")
                    else:
                        with st.spinner("Running audit... This may take a few minutes..."):
                            # Progress indicators
                            progress_text = st.empty()
                            progress_bar = st.progress(0)

                            try:
                                # Create audit instance
                                audit = TechStackAudit(
                                    research_window_years=years)

                                # Run audit
                                progress_text.text(
                                    "Phase 1: Researching tools...")
                                progress_bar.progress(33)

                                # Run async audit
                                report_path = asyncio.run(
                                    audit.run_audit(
                                        csv_path=str(temp_csv_path),
                                        client_name=client_name,
                                        research_depth=depth
                                    )
                                )

                                progress_bar.progress(100)
                                progress_text.text("✅ Audit complete!")

                                # Read report content
                                with open(report_path, 'r', encoding='utf-8') as f:
                                    report_content = f.read()

                                # Store in session state
                                st.session_state.audit_complete = True
                                st.session_state.report_path = report_path
                                st.session_state.report_content = report_content

                                st.success(
                                    f"🎉 Audit complete! Report saved to: {report_path}")
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error during audit: {str(e)}")
                                st.exception(e)

        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")

with col2:
    st.header("📄 Report")

    if st.session_state.audit_complete and st.session_state.report_content:
        # Show report preview
        st.subheader("Preview")

        # Display report in a scrollable container
        st.markdown(st.session_state.report_content, unsafe_allow_html=False)

        st.divider()

        # Download button
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=st.session_state.report_content,
            file_name=f"audit_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            type="primary"
        )

        # Option to start new audit
        if st.button("🔄 Start New Audit"):
            st.session_state.audit_complete = False
            st.session_state.report_path = None
            st.session_state.report_content = None
            st.rerun()

    else:
        st.info("👈 Upload a CSV and click 'Run Audit' to generate a report")

        # Show example of what report looks like
        st.subheader("What You'll Get")
        st.markdown("""
        Your report will include:
        
        **📊 Executive Summary**
        - Total tools analyzed
        - Key findings
        - Estimated time savings & ROI
        
        **🔧 Tools Analyzed**
        - Recent updates discovered
        - Automation features
        - Current utilization
        
        **🔗 Integration Opportunities**
        - Specific n8n workflows
        - Time savings estimates
        - Implementation complexity
        - Prerequisites
        
        **⚡ Quick Wins**
        - Low-hanging fruit (< 1 week)
        - Immediate ROI opportunities
        
        **🗺️ Implementation Roadmap**
        - Phased approach
        - Timeline and owners
        - Success metrics
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Tech Stack Audit Tool | Powered by CrewAI & OpenAI | Open Source (n8n) Focus</small>
</div>
""", unsafe_allow_html=True)
