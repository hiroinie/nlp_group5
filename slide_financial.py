import json
import openai
import streamlit as st
from jinja2 import Template
from weasyprint import HTML

# Configure OpenAI API key
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key is not configured.\n\nPlease check your .streamlit/secrets.toml file.")
    st.stop()

def generate_financial_summary(company: str, analysis_data: dict) -> str:
    """Generate a short financial summary sentence."""
    revenue_text = " / ".join(analysis_data.get("revenue", []))
    profit_text = " / ".join(analysis_data.get("profit", []))
    expenses_text = " / ".join(analysis_data.get("expenses", []))
    outlook_text = " / ".join(analysis_data.get("outlook", []))

    prompt = f"""
Based on the following financial overview for {company}, provide a concise summary within 150 characters highlighting the key trend.

Revenue: {revenue_text}
Profit: {profit_text}
Expenses: {expenses_text}
Outlook: {outlook_text}
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
You are a financial analyst. Provide recent financial highlights for {company}.
Return 3 short bullet points (within 125 characters) each for Revenue, Profit, Expenses and Outlook in JSON format like:
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
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        st.error(f"Financial analysis API error: {e}")
        return None


def generate_financial_slide_html(company: str, analysis_data: dict, summary: str) -> str:
    """Generate financial slide HTML using financial_template.html."""
    try:
        with open("financial_template.html", "r", encoding="utf-8") as f:
            template_content = f.read()

        html_content = template_content
        html_content = html_content.replace("Company Financial", "Company Financial")
        html_content = html_content.replace(
            "        • Financial highlights overview<br>\n        • Key figures in recent years",
            f"        • {summary}<br>        • Key financial indicators"
        )
        revenue_html = "\n".join([f'            <li>{item}</li>' for item in analysis_data.get("revenue", [])])
        profit_html = "\n".join([f'            <li>{item}</li>' for item in analysis_data.get("profit", [])])
        expenses_html = "\n".join([f'            <li>{item}</li>' for item in analysis_data.get("expenses", [])])
        outlook_html = "\n".join([f'            <li>{item}</li>' for item in analysis_data.get("outlook", [])])

        html_content = html_content.replace(
            "            <li>Revenue item 1</li>\n            <li>Revenue item 2</li>\n            <li>Revenue item 3</li>",
            revenue_html
        )
        html_content = html_content.replace(
            "            <li>Profit item 1</li>\n            <li>Profit item 2</li>\n            <li>Profit item 3</li>",
            profit_html
        )
        html_content = html_content.replace(
            "            <li>Expenses item 1</li>\n            <li>Expenses item 2</li>\n            <li>Expenses item 3</li>",
            expenses_html
        )
        html_content = html_content.replace(
            "            <li>Outlook item 1</li>\n            <li>Outlook item 2</li>\n            <li>Outlook item 3</li>",
            outlook_html
        )
        return html_content
    except Exception as e:
        st.error(f"Template processing error occurred: {e}")
        return None


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
