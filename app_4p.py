import os
import json
import openai
import streamlit as st
from jinja2 import Template
from weasyprint import HTML

# OpenAI API key configuration (using Streamlit secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key is not configured.\n\nPlease check your .streamlit/secrets.toml file.")
    st.stop()

def generate_strategic_summary(company: str, analysis_data: dict):
    """
    Generate strategic summary comment based on 4P analysis results
    """
    # Convert analysis data to text for prompt
    product_text = " / ".join(analysis_data.get("product", []))
    price_text = " / ".join(analysis_data.get("price", []))
    place_text = " / ".join(analysis_data.get("place", []))
    promotion_text = " / ".join(analysis_data.get("promotion", []))
    
    prompt = f"""
Based on the following 4P analysis results for {company}, please write a concise strategic summary comment (within 150 characters) that captures the key business strategy and competitive positioning.

Product: {product_text}
Price: {price_text}
Place: {place_text}
Promotion: {promotion_text}

Please provide a professional business summary that highlights the company's strategic focus and market positioning. The comment should be suitable for a business presentation slide header.

Return only the summary comment, no additional explanations.
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business strategy consultant. Create concise, professional strategic summaries."},
                {"role": "user", "content": prompt},
            ],
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        st.error(f"Strategic summary generation error: {e}")
        return f"{company}'s 4P Analysis (Product, Price, Place, Promotion) - Strategic business framework for market positioning and competitive advantage"

def generate_4p_analysis(company: str):
    """
    Generate 4P analysis for a company using OpenAI API
    """
    prompt = f"""
You are a marketing analysis expert.
Company: {company}

Please conduct a 4P analysis (Product, Price, Place, Promotion) for this company and
return 3-4 detailed points for each element (within 125 characters per point) in a list format.

Include specific, practical, and detailed content with concrete examples and strategic insights. 
Make each point informative for business decision-making while keeping content concise.

Return only in the following JSON format (no additional explanations needed):
{{
  "product": ["Detailed product/service analysis 1", "Detailed product/service analysis 2", "Detailed product/service analysis 3"],
  "price": ["Detailed pricing strategy analysis 1", "Detailed pricing strategy analysis 2", "Detailed pricing strategy analysis 3"],
  "place": ["Detailed distribution/channel analysis 1", "Detailed distribution/channel analysis 2", "Detailed distribution/channel analysis 3"],
  "promotion": ["Detailed promotion strategy analysis 1", "Detailed promotion strategy analysis 2", "Detailed promotion strategy analysis 3"]
}}

Example format (aim for 100-125 characters per point):
- Product: "High-reliability MLCCs for EV/ADAS applications, achieving 47µF in ultra-small 1005 size with superior temperature stability"
- Price: "Premium pricing strategy leveraging technology differentiation, maintaining 15-20% price premium over competitors"
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a marketing analysis expert. Respond only in JSON format. Each point should be detailed and specific within 125 characters, including concrete examples."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content.strip()
        
        # Check JSON start and end, fix if necessary
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Check for empty response
        if not content:
            st.error("Empty response returned from API.")
            return None
            
        # JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {e}")
            with st.expander("Show debug information"):
                st.code(content)
            return None
            
    except Exception as e:
        st.error(f"API call error: {e}")
        return None

def generate_4p_slide_html(company: str, analysis_data: dict, strategic_summary: str):
    """
    Generate 4P analysis slide using template.html with strategic summary
    """
    try:
        # Load template file
        with open("template.html", "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # Create Jinja2 template object
        template = Template(template_content)
        
        # Generate HTML by replacing placeholders
        html_content = template_content
        
        # Replace title and subtitle
        html_content = html_content.replace("4P Analysis", f"4P Analysis")
        html_content = html_content.replace(
            '''        • Toyota's 4P Analysis (Product, Price, Place, Promotion) to organize business strategy<br>
        • Focus on differentiation in specialized applications and global market recognition improvement''',
            f"        • {strategic_summary}<br>\n        • Strategic business framework for market positioning and competitive advantage"
        )
        
        # Replace product content
        product_html = "\n".join([f'                <li>{item}</li>' for item in analysis_data.get("product", [])])
        html_content = html_content.replace(
            '''                <li>Hybrid technology providing efficient and environmentally friendly lineup, emphasizing technological innovation</li>
                <li>Diverse vehicle range including SUVs, sedans, and trucks to serve broad customer segments</li>
                <li>Market expansion through not only new vehicles but also used car sales and certified pre-owned programs</li>''',
            product_html
        )
        
        # Replace place content
        place_html = "\n".join([f'                <li>{item}</li>' for item in analysis_data.get("place", [])])
        html_content = html_content.replace(
            '''                <li>Strengthen global dealer network covering urban to rural areas</li>
                <li>Enhance customer convenience by combining online sales with click & collect models</li>
                <li>Improve post-purchase customer satisfaction through comprehensive service centers and customer support</li>''',
            place_html
        )
        
        # Replace price content
        price_html = "\n".join([f'                <li>{item}</li>' for item in analysis_data.get("price", [])])
        html_content = html_content.replace(
            '''                <li>Competitive pricing to secure market share while adding premium through technological differentiation</li>
                <li>Regional price adjustments based on local purchasing power for effective market adaptation</li>
                <li>Expand customer base by reducing purchase barriers through lease contracts and installment plans</li>''',
            price_html
        )
        
        # Replace promotion content
        promotion_html = "\n".join([f'                <li>{item}</li>' for item in analysis_data.get("promotion", [])])
        html_content = html_content.replace(
            '''                <li>Enhance brand image through sponsorships of sports events and cultural programs</li>
                <li>Emphasize reliability and sustainability through advertising campaigns linked to environmental responsibility</li>
                <li>Improve recognition among younger demographics using targeted social media campaigns</li>''',
            promotion_html
        )
        
        return html_content
    except Exception as e:
        st.error(f"Template processing error occurred: {e}")
        return None

# Streamlit UI
st.title("🚀 4P Analysis Slide Generator")
st.markdown("**Enter a company name and AI will automatically generate detailed and beautiful 4P analysis slides.**")

# Company name input
company = st.text_input("🏢 Enter company name", placeholder="Example: Apple, Toyota, Sony, Amazon")

# Generate button
if st.button("✨ Generate Detailed 4P Analysis Slide", type="primary") and company:
    with st.spinner("🤖 AI is executing detailed 4P analysis..."):
        # 1. Get 4P analysis data from OpenAI API
        analysis_data = generate_4p_analysis(company)
        
        if analysis_data:
            # 2. Generate strategic summary based on analysis results
            with st.spinner("📝 AI is generating strategic summary..."):
                strategic_summary = generate_strategic_summary(company, analysis_data)
            
            st.success("🎉 Detailed 4P analysis completed!")
            
            # 3. Display analysis results
            st.subheader("📊 Detailed Analysis Results")
            
            # Display strategic summary
            st.info(f"**Strategic Summary:** {strategic_summary}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📱 Product (Products & Services)**")
                for item in analysis_data.get("product", []):
                    st.markdown(f"• {item}")
                
                st.markdown("**💰 Price (Pricing)**")
                for item in analysis_data.get("price", []):
                    st.markdown(f"• {item}")
            
            with col2:
                st.markdown("**🌍 Place (Distribution & Channels)**")
                for item in analysis_data.get("place", []):
                    st.markdown(f"• {item}")
                
                st.markdown("**📢 Promotion (Marketing & Promotion)**")
                for item in analysis_data.get("promotion", []):
                    st.markdown(f"• {item}")
            
            # 4. Generate HTML slide with strategic summary
            html_content = generate_4p_slide_html(company, analysis_data, strategic_summary)
            
            if html_content:
                # 5. PDF download feature
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    try:
                        pdf = HTML(string=html_content).write_pdf()
                        st.download_button(
                            "📄 Download High-Quality PDF", 
                            pdf, 
                            file_name=f"{company}_4P_analysis_detailed.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.warning(f"PDF generation error occurred: {e}")
                
                # 6. HTML preview
                st.subheader("🎨 Professional Slide Preview")
                st.components.v1.html(html_content, height=600, scrolling=True)
        else:
            st.error("❌ Detailed 4P analysis generation failed.")

# Display usage instructions in sidebar
with st.sidebar:
    st.markdown("## 🔑 API Key Configuration")
    st.markdown("""
    Please configure your OpenAI API key in  
    `.streamlit/secrets.toml` file.
    """)
    
    st.markdown("## 📖 How to Use")
    st.markdown("""
    1. 🏢 Enter company name
    2. ✨ Click "Generate Detailed 4P Analysis Slide" button
    3. 🤖 AI automatically executes detailed 4P analysis
    4. 📝 AI generates strategic summary comment
    5. 📊 Review detailed results and summary
    6. 📄 Download high-quality PDF
    """)
    
    st.markdown("## 🎯 What is 4P Analysis")
    st.markdown("""
    - **📱 Product**: Product & service features
    - **💰 Price**: Pricing strategy & competitiveness
    - **🌍 Place**: Distribution, channels & placement
    - **📢 Promotion**: Promotion & marketing activities
    """)
    
    st.markdown("## ✨ Improvement Points")
    st.markdown("""
    - 🎨 Faithful to original model design
    - 📐 Presentation-oriented layout
    - 📝 Detailed analysis content (within 125 characters)
    - 🖨️ PDF output optimization
    - 📊 Professional quality
    - 🧠 AI-generated strategic summary
    """) 