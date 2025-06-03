import os
import json
import openai
import streamlit as st
from jinja2 import Template
from weasyprint import HTML

openai.api_key = os.getenv("OPENAI_API_KEY")

context = ""  # placeholder for future RAG


def generate_slide(company: str):
    prompt = f"""
You are GPT-4o helping to create a Porter 5 Forces slide.
Company: {company}
Context: {context}
Return only JSON with the following keys:
- Threat of new entrants
- Bargaining power of suppliers
- Bargaining power of buyers
- Threat of substitutes
- Industry rivalry
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def generate_slide_html(company: str, model_slide_html: str):
    prompt = f"""
You are GPT-4o helping to create a Porter 5 Forces slide.
Company: {company}
Below is a sample slide design in HTML. Please use this as a reference and generate a new slide for the company above. Return only the HTML code.

---
{model_slide_html}
---
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst and HTML designer."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content.strip()
    return content


st.title("AI Junior Banker")
company = st.text_input("Company Name")

if st.button("Generate Slide") and company:
    with open("template.html") as f:
        model_slide_html = f.read()
    html_content = generate_slide_html(company, model_slide_html)
    pdf = HTML(string=html_content).write_pdf()
    st.download_button("Download PDF", pdf, file_name="slide.pdf")
    st.components.v1.html(html_content, height=600, scrolling=True)
