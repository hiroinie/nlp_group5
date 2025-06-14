import json
import re
import openai
import streamlit as st
from weasyprint import HTML
from base64 import b64encode

# Configure OpenAI API key
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key is not configured.\n\nPlease check your .streamlit/secrets.toml file.")
    st.stop()

def generate_financial_summary(company: str, analysis_data: dict) -> str:
    """Generate a short financial summary sentence."""
    revenue_text = " / ".join(_stringify(i) for i in analysis_data.get("revenue", []))
    profit_text = " / ".join(_stringify(i) for i in analysis_data.get("profit", []))

    prompt = f"""
Based on the following financial overview for {company}, provide a concise summary within 150 characters highlighting the key trend.

Revenue: {revenue_text}
Profit: {profit_text}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst generating short, professional summaries."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Financial summary generation error: {e}")
        return f"{company} financial highlights"


def generate_financial_analysis(company: str):
    """Ask OpenAI for key financial metrics."""
    prompt = f"""
You are a financial analyst.
Please provide the revenue and profit trends for {company} over the past few years. We will use these figures to create a bar chart of the company's performance trends.
Return the information in JSON format like:
{{
  "revenue": ["..."],
  "profit": ["..."],
  "expenses": ["..."],
  "outlook": ["..."]
}}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Respond in JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        content = _strip_code_fences(response.choices[0].message.content)
        try:
            return json.loads(content)
        except json.JSONDecodeError as je:
            st.error(f"JSON parsing error: {je}\nRaw response:\n{content[:500]}")
            return None
    except Exception as e:
        st.error(f"Financial analysis API error: {e}")
        return None


def generate_financial_slide_html(company: str, analysis_data: dict, summary: str) -> str:
    """Use ChatGPT (gpt-4o) to generate the final HTML slide by providing the original template and the data to fill in."""
    try:
        # Read the SVG template. If it lacks an HTML wrapper, add a minimal one so the model clearly receives a valid HTML document.
        with open("financial_template.svg", "r", encoding="utf-8") as f:
            svg_content = f.read()

        if "<html" not in svg_content.lower():
            template_content = f"<html><body>{svg_content}</body></html>"
        else:
            template_content = svg_content

        # Construct the prompt for ChatGPT.
        prompt = (
            "You are a professional presentation designer. "
            "I will give you an HTML template for a financial overview slide together with specific data. "
            "Please output a *single* completed HTML document (including <html> and <body> tags) that looks the same as the template but with the data filled in. "
            "Return only HTML – no Markdown code fences or additional commentary. Ensure the slide keeps 16:9 horizontal orientation. For the bar charts, adjust bar heights proportionally to the numeric values provided.\n\n"
            "----- TEMPLATE START -----\n"
            f"{template_content}\n"
            "----- TEMPLATE END -----\n\n"
            f"Company name: {company}\n"
            f"Introductory bullets (replace the existing intro bullets): • {summary} <br> • Key financial indicators\n\n"
            "Replace each section's list items using the following JSON. Each list must contain exactly the items given, one <li> element per item.\n"
            f"{json.dumps(analysis_data, ensure_ascii=False)}"
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You output only valid, minified HTML with no explanations."},
                {"role": "user", "content": prompt},
            ],
            # Let the model decide length; template is large so we omit max_tokens here.
        )

        html_output = _strip_code_fences(response.choices[0].message.content)

        # Ensure landscape orientation CSS is present.
        html_output = _ensure_landscape_css(html_output)

        return html_output
    except Exception as e:
        st.error(f"Financial slide generation error: {e}")
        return None


def _strip_code_fences(text: str) -> str:
    """Remove triple-backtick Markdown fences (with or without language tags) from given text."""
    # Remove starting and ending fences, and any inner fenced blocks.
    # Pattern: optional ```lang\n at beginning, optional ``` at end, global.
    # Use non-greedy match for content between fences.
    return re.sub(r"```[a-zA-Z]*\s*|```", "", text).strip()


def _stringify(item) -> str:
    """Convert list element (str, dict, etc.) to a readable string."""
    if isinstance(item, dict):
        # Concatenate key-value pairs like "year: 2023, value: $10B"
        return ", ".join(f"{k}: {v}" for k, v in item.items())
    return str(item)


def _ensure_landscape_css(html: str) -> str:
    """Inject @page landscape CSS into <head> if not already present."""
    if "@page" in html and "landscape" in html:
        return html  # Already has orientation info
    css_block = (
        "<style>@page { size: 1280px 720px landscape; margin: 0;} "
        "body {width: 1280px; height: 720px; margin:0 auto;} </style>"
    )
    if "<head>" in html:
        return html.replace("<head>", f"<head>{css_block}")
    # Fallback: prepend
    return css_block + html


def run() -> None:
    """Run the Company Financial Streamlit page."""
    st.title("🏦 Company Financial Slide Generator")
    st.markdown("**Enter a company name to generate a financial overview slide.**")
    company = st.text_input("🏢 Enter company name", key="fin_company", placeholder="Example: Apple, Toyota, Sony, Amazon")

    if st.button("✨ Generate Company Financial Slide", key="fin_button", type="primary") and company:
        with st.spinner("🤖 AI is gathering financial data..."):
            analysis_data = generate_financial_analysis(company)
            if analysis_data:
                with st.spinner("📝 AI is summarizing..."):
                    summary = generate_financial_summary(company, analysis_data)
                st.success("🎉 Financial analysis completed!")
                st.subheader("📊 Financial Highlights")
                for section, items in analysis_data.items():
                    st.markdown(f"**{section.capitalize()}**")
                    for item in items:
                        st.markdown(f"• {item}")
                html_content = generate_financial_slide_html(company, analysis_data, summary)
                if html_content:
                    col_a, col_b = st.columns([1,3])
                    with col_a:
                        try:
                            pdf = HTML(string=html_content).write_pdf()
                            st.download_button(
                                "📄 Download High-Quality PDF",
                                pdf,
                                file_name=f"{company}_financial_overview.pdf",
                                mime="application/pdf",
                                key="fin_pdf"
                            )
                        except Exception as e:
                            st.warning(f"PDF generation error occurred: {e}")
                    st.subheader("🎨 Slide Preview")
                    st.components.v1.html(html_content, height=600, scrolling=True)
            else:
                st.error("❌ Financial analysis generation failed.")

    with st.sidebar:
        st.markdown("## 🔑 API Key Configuration")
        st.markdown(
            """
            Please configure your OpenAI API key in
            `.streamlit/secrets.toml` file.
            """
        )

if __name__ == "__main__":
    run()
