
import streamlit as st
import pandas as pd
import requests

# -----------------------------
# 🔐 SerpAPI Key (Hardcoded)
# -----------------------------
api_key = "e59d3441aefda6456b467ba272417d89ab5b5a7accc9f668f523321e5d8bc057"

# -----------------------------
# 🔍 Scraping Function
# -----------------------------
def scrape_leads_with_serpapi(api_key, keyword, location, company=None, num_results=30):
    query = f'site:linkedin.com/in/ "{keyword}" "{location}"'
    if company:
        query += f' "{company}"'

    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": api_key
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    leads = []
    for result in data.get("organic_results", []):
        leads.append({
            "Name/Title": result.get("title"),
            "LinkedIn URL": result.get("link"),
            "Snippet": result.get("snippet")
        })

    return pd.DataFrame(leads)

# -----------------------------
# 🧠 Lead Scoring Function
# -----------------------------
def score_lead(row):
    score = 0
    keywords = ['AI', 'ML', 'Data', 'Senior', 'Principal', 'Lead', 'Manager', 'Director',
                'Talent Acquisition', 'Recruiter', 'HR', 'Hiring Manager',
                'Software Engineer', 'Data Scientist', 'Data Analyst', 'Business Analyst']
    for kw in keywords:
        if kw.lower() in str(row['Name/Title']).lower() or kw.lower() in str(row['Snippet']).lower():
            score += 2
    return score

# -----------------------------
# 🚀 Streamlit App UI
# -----------------------------
st.set_page_config(page_title="Lead Scraper", layout="wide")
st.title("🔗 Lead Scraper")
st.markdown("Enter the details below to scrape Leads")

# 📌 Input Fields
keyword = st.text_input("🧠 Keyword (e.g., Data Scientist)")
location = st.text_input("📍 Location (e.g., India)")
company = st.text_input("🏢 Company (optional)")

# 🔢 Number of Results Slider
num_results = st.slider(
    label="Number of Results",
    min_value=10,
    max_value=100,
    value=30,
    help="Select how many leads to fetch (max 100)"
)

# 🔍 Scraping and Scoring
if st.button("🚀 Scrape Leads"):
    if not keyword or not location:
        st.warning("Please enter both keyword and location.")
    else:
        with st.spinner("🔍 Scraping data from LinkedIn..."):
            df = scrape_leads_with_serpapi(api_key, keyword, location, company, num_results=num_results)

            if df.empty:
                st.error("❌ No leads found. Try different inputs.")
            else:
                df['Lead Score'] = df.apply(score_lead, axis=1)
                df = df.sort_values(by='Lead Score', ascending=False)

                # Add clickable LinkedIn profile links
                df['LinkedIn Profile (Link)'] = df['LinkedIn URL'].apply(
                    lambda x: f"<a href='{x}' target='_blank'>🔗 Profile</a>" if pd.notnull(x) else ''
                )

                # Show in Streamlit with HTML
                st.markdown("### 🧾 Scored Leads")
                st.write(df[['Name/Title', 'LinkedIn Profile (Link)', 'Snippet', 'Lead Score']].to_html(escape=False, index=False), unsafe_allow_html=True)

                # Download scored leads CSV
                csv = df[['Name/Title', 'LinkedIn URL', 'Snippet', 'Lead Score']].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Scored Leads CSV",
                    data=csv,
                    file_name='scored_leads.csv',
                    mime='text/csv'
                )
