# Running the Streamlit Dashboard

## Quick Start

### 1. Install Streamlit
```bash
pip install streamlit==1.28.0
```

Or update your requirements:
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run streamlit_app.py
```

This will:
- Start a local web server (usually at `http://localhost:8501`)
- Open your browser automatically
- Show the audit tool interface

### 3. Using the Dashboard

**Left Column - Upload & Configure:**
1. Enter client name in the sidebar
2. Adjust research window (years) and depth
3. Upload your CSV file
4. Preview the data
5. Click "🚀 Run Audit"

**Right Column - Report:**
1. View report preview after audit completes
2. Download the markdown report
3. Start a new audit if needed

## Features

✅ **Drag & Drop CSV Upload** - Easy file handling
✅ **Live Preview** - See your data before running
✅ **Progress Tracking** - Watch the audit in real-time
✅ **Report Preview** - Review before downloading
✅ **One-Click Download** - Get your markdown report
✅ **Session Management** - Keep reports until you start new audit

## Troubleshooting

**Dashboard won't start:**
```bash
# Make sure you're in the right directory
cd ~/Desktop/AI_Consultancy_Project/2-Personal_Projects/simplified_TSAT

# Verify streamlit is installed
pip list | grep streamlit
```

**Port already in use:**
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

**Report not showing:**
- Check that the audit completed successfully
- Look for error messages in the dashboard
- Verify your .env file has OPENAI_API_KEY

## Tips

💡 **Research Depth:**
- **Quick**: ~5-10 min, basic research
- **Medium**: ~15-20 min, balanced (recommended)
- **Deep**: ~25-30 min, comprehensive

💡 **Multiple Audits:**
- Reports are saved with timestamps
- Check `output/` folder for all past reports
- Dashboard keeps current report until you click "Start New Audit"

💡 **CSV Format:**
Must have these columns:
- Tool Name
- Category
- Used By
- Criticality

See `data/cga_real_tools.csv` for an example.
