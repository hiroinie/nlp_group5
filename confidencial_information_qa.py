import streamlit as st
import pandas as pd
import openai

@st.cache_data
def load_confidential_data():
    return pd.read_csv("Investment_Banking_Confidential_Data__sample_.csv", sep=';')

def get_sector_options(df):
    return sorted(df['Sector'].unique())

def summarize_experience(sector, df):
    if sector:
        sector_rows = df[df['Sector'] == sector]
    else:
        sector_rows = df
    experience = sector_rows[['Company', 'DealType', 'DealValueUSD_M', 'RevenueMultiple', 'EBITDAMultiple', 'FundingSource', 'PostDealROIC_3Y_pct', 'MarketReaction_1D_pct', 'Recommendation']].to_dict(orient='records')
    return experience

def ask_openai(question, experience, company, sector):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    prompt = f"""
You are an expert M&A advisor. Use the following confidential deal data as your experience base. Answer the user's question about {company} in the {sector if sector else 'all'} sector, using only the data below as your knowledge. If the answer is not directly in the data, use your best judgment based on the patterns and numbers provided.

Experience data:
{experience}

Question: {question}
Answer as a concise, professional M&A advisor:
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert M&A advisor. Use only the provided experience data."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"

def answer_questions(company, sector, df):
    experience = summarize_experience(sector, df)
    questions = [
        f"If {company} were to pursue an acquisition, how much do companies in the same sector usually pay?",
        f"For a deal by {company}, what three-year ROIC could be expected based on sector experience?",
        f"If {company} does a large deal, is it more likely to be financed with debt or equity in this sector?",
        f"After similar deals, do analysts mostly rate companies like {company} a buy or a sell?",
        f"How does the market typically react right after a big deal is announced by a company like {company}?"
    ]
    answers = []
    for q in questions:
        answer = ask_openai(q, experience, company, sector)
        answers.append(answer)
    return answers

def run():
    st.title("Confidential Information Decision")
    st.write("Answer key M&A questions using confidential deal data and AI expertise.")
    df = load_confidential_data()
    company = st.text_input("Enter company name:")
    sector_options = get_sector_options(df)
    sector = st.selectbox("Select sector for experience base:", ["All sectors"] + sector_options)
    sector_value = None if sector == "All sectors" else sector
    if company:
        answers = answer_questions(company, sector_value, df)
        questions = [
            f"If {company} were to pursue an acquisition, how much do companies in the same sector usually pay?",
            f"For a deal by {company}, what three-year ROIC could be expected based on sector experience?",
            f"If {company} does a large deal, is it more likely to be financed with debt or equity in this sector?",
            f"After similar deals, do analysts mostly rate companies like {company} a buy or a sell?",
            f"How does the market typically react right after a big deal is announced by a company like {company}?"
        ]
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            st.markdown(f"**{i}. {q}**")
            st.write(a)
