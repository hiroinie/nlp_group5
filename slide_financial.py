import json
import re
import openai
import streamlit as st
from weasyprint import HTML

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
Based on the following financial overview for {company}, provide a concise summary within 100 characters highlighting the key trend.

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
Please provide the company's revenue and EBIT for the past eight fiscal years and, if available, the current and next fiscal year forecasts. We will use these figures to create bar charts of performance trends.

Return ONLY JSON in the following exact structure (do not include any commentary):
{{
  "revenue": ["YYYY: value", ...],
  "ebit": ["YYYY: value", ...]
}}

Requirements:
• List each fiscal year separately (e.g., 2018/3, 2019/3 ...). If a value is a forecast, add suffix "E" (e.g., 2025E).
• Use the same currency unit throughout (indicate unit inside the value, e.g., "$79 billion" or "¥2.3 trillion").
• Provide up to 10 entries (max). If forecast data is unavailable, omit.
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


def _prepare_chart_data_for_llm(data_items: list) -> list:
    """Parses data strings and calculates relative bar heights for the LLM."""
    structured_data = []
    numeric_values = []

    # First pass: extract labels and numeric values.
    for item in data_items:
        label, value_text, numeric_val = "N/A", "0", 0.0
        if isinstance(item, str) and ":" in item:
            parts = item.split(":", 1)
            label = parts[0].strip()
            value_text = parts[1].strip()
            numeric_match = re.search(r"[-+]?(\d*\.?\d+)", value_text)
            if numeric_match:
                numeric_val = float(numeric_match.group(1))
        
        structured_data.append({"label": label, "value_text": value_text})
        numeric_values.append(numeric_val)

    if not numeric_values:
        return []

    # Second pass: calculate percentage height.
    max_val = max(numeric_values) if numeric_values else 1
    if max_val == 0: max_val = 1

    for i, item in enumerate(structured_data):
        item["height_pct"] = round((numeric_values[i] / max_val) * 100)

    return structured_data


def _build_bars_html(items: list, color: str) -> str:
    """Return SVG-based bar chart so WeasyPrint renders it in PDF."""
    labels, values, texts = [], [], []
    for itm in items:
        if isinstance(itm, str) and ":" in itm:
            label, txt = itm.split(":", 1)
            labels.append(label.strip())
            texts.append(txt.strip())
            m = re.search(r"[-+]?[0-9]*\.?[0-9]+", txt)
            values.append(float(m.group()) if m else 0)
    if not values:
        return ""
    # chart geometry
    w, h = 600, 150
    slot = w / len(values)
    bar_w = slot * 0.6
    mx = max(values) or 1
    svg_parts = [f'<svg width="{w}" height="{h}" style="display:block;margin:0 auto;" xmlns="http://www.w3.org/2000/svg">']
    for i, (lbl, val, txt) in enumerate(zip(labels, values, texts)):
        bh = round((val / mx) * (h - 20))  # leave space for value text
        x = i * slot + (slot - bar_w) / 2
        y = h - bh
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bh}" fill="{color}"/>')
        svg_parts.append(f'<text x="{x + bar_w/2}" y="{y - 2}" font-size="10" text-anchor="middle">{txt}</text>')
        svg_parts.append(f'<text x="{x + bar_w/2}" y="{h}" font-size="10" text-anchor="middle">{lbl}</text>')
    svg_parts.append('</svg>')
    return "<div style='width:100%;text-align:center'>" + "".join(svg_parts) + "</div>"


def generate_financial_slide_html(company: str, analysis_data: dict, summary: str) -> str:
    """Generates final HTML by inserting data into the predefined template with markers."""
    try:
        with open("Financial performance.html", "r", encoding="utf-8") as f:
            tpl = f.read()

        revenue_html = _build_bars_html(analysis_data.get("revenue", []), "#4A90E2")
        ebit_html = _build_bars_html(analysis_data.get("ebit", []), "#F5A623")

        # Replace placeholders (allow for either single or START/END markers)
        out = tpl.replace("<!--COMPANY_NAME-->", company)
        out = out.replace("<!--SUMMARY_LIST-->", f"<li>{summary}</li><li>Key financial indicators</li>")
        # comment markers replacement
        out = re.sub(r"<!--REVENUE_CHART.*?-->([\s\S]*?)<!--REVENUE_CHART.*?-->", revenue_html, out, flags=re.IGNORECASE)
        out = re.sub(r"<!--EBIT_CHART.*?-->([\s\S]*?)<!--EBIT_CHART.*?-->", ebit_html, out, flags=re.IGNORECASE)
        # canvas replacement fallback
        out = re.sub(r"<canvas[^>]*id=\"revenueChart\"[^>]*>[\s\S]*?</canvas>", revenue_html, out, flags=re.IGNORECASE)
        out = re.sub(r"<canvas[^>]*id=\"ebitChart\"[^>]*>[\s\S]*?</canvas>", ebit_html, out, flags=re.IGNORECASE)

        # Inject mandatory CSS (size, margin-0, chart styles) ifまだ無い
        css_block = (
            "<style>@page { size:1280px 720px; margin:0 } "
            "html,body{width:1280px;height:720px;margin:0;padding:0;} "
            ".chart-container{position:relative;height:150px;text-align:center;white-space:nowrap;} "
            "" 
        )
        if "@page" not in out:
            out = out.replace("<head>", "<head>"+css_block, 1)

        return out
    except Exception as e:
        st.error(f"Slide template processing error: {e}")
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
