# 🚀 4P Analysis Slide Generator

AI-powered Streamlit app that generates detailed 4P analysis slides for any company using OpenAI GPT-4o.

## ✨ Features

- **AI-Generated 4P Analysis**: Product, Price, Place, Promotion analysis for any company
- **Strategic Summary**: AI-generated business strategy summary
- **Professional Slides**: Beautiful HTML presentation slides
- **PDF Export**: Download slides as PDF using WeasyPrint
- **Responsive Design**: Works on desktop and mobile

## 🛠️ Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API Key**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```

3. **Run the app**
   ```bash
   streamlit run app_4p.py
   ```

## 📁 Project Structure

```
├── app_4p.py          # Main Streamlit application
├── template.html      # HTML slide template
├── requirements.txt   # Python dependencies
├── .gitignore        # Git ignore rules
└── .streamlit/       # Streamlit configuration
    └── secrets.toml  # API keys (not in git)
```

## 🎯 Usage

1. Enter any company name (e.g., "Apple", "Toyota", "Amazon")
2. Click "Generate Detailed 4P Analysis Slide"
3. View AI-generated analysis results
4. Download as PDF or view HTML preview

## 🔧 Dependencies

- `streamlit` - Web app framework
- `openai` - OpenAI API client
- `Jinja2` - HTML template processing
- `WeasyPrint` - PDF generation

## 📝 Note

Requires OpenAI API key for GPT-4o access. Each analysis costs approximately $0.01-0.02. 