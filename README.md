# AI Junior Banker

This repository contains a Streamlit proof of concept that can generate multiple types of business slides using GPT-4o.
Currently two slide types are available:

- **4P Analysis** – marketing mix analysis with strategic summary
- **Company Financial** – simple financial highlights overview

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key
```

## Run

Start the app with Streamlit:

```bash
streamlit run app.py
```

Choose a slide type in the sidebar, enter a company name and generate the slide. A PDF download will also be available.
