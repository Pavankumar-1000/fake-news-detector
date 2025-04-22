import streamlit as st
from utils.preprocess import clean_text
from utils.ml_model import predict_news
from utils.fact_check import verify_facts
from utils.kaggle_checker import check_against_kaggle
from utils.kaggle_updater import download_latest_dataset
from utils.newsapi_verifier import verify_with_newsapi
from utils.gemini_fact_check import fact_check_with_gemini
from dotenv import load_dotenv

load_dotenv()
download_latest_dataset()

st.set_page_config(page_title="Fake News Detector", layout="centered")

st.title("📰 Fake News Detection & Verification")
st.markdown("""
This app predicts whether a news article is **True or Fake**, using:
- ✅ Gemini AI (internet + intelligent reasoning)  
- ✅ NewsAPI (real-time news)  
- ✅ Kaggle Dataset  
- ✅ Trusted Source Search  
- ✅ ML model (fallback only)

Supports **English and Tamil** 🗞️  
""")

language = st.radio("🌐 Language Preference", ["English", "Tamil"], horizontal=True)
use_gemini = st.checkbox("🧠 Use Gemini AI for Internet-based Verification", value=True)

news_input = st.text_area("🖊️ Paste or type the news you want to verify:", height=200)

if st.button("🔍 Verify News"):
    if not news_input.strip():
        st.warning("⚠️ Please enter some news content.")
    else:
        with st.spinner("Cleaning and analyzing the input..."):
            cleaned = clean_text(news_input)

        final_verdict = None
        confidence = 0
        source_links = []
        method_used = ""
        gemini_explanation = ""

        # ✅ Step 1: Gemini AI
        if use_gemini:
            with st.spinner("Checking with Gemini AI..."):
                gemini_result = fact_check_with_gemini(news_input)

            print("Gemini Response:", gemini_result)

            if gemini_result.get("verdict") in ["Real", "Fake"]:
                final_verdict = "True" if gemini_result["verdict"] == "Real" else "Fake"
                confidence = gemini_result.get("confidence", 0)
                method_used = "Gemini AI"
                source_links = gemini_result.get("sources", [])
                gemini_explanation = gemini_result.get("explanation", "")
            elif gemini_result.get("verdict") == "limit_exceeded":
                st.error("❌ Gemini API usage limit exceeded. Try again later or use another method.")
            else:
                st.warning("⚠️ Gemini API failed or gave an invalid result. Proceeding with fallback options.")

        # ✅ Step 2: NewsAPI
        if final_verdict is None:
            with st.spinner("Checking with NewsAPI..."):
                newsapi_result = verify_with_newsapi(news_input)
            if newsapi_result.get("status") == "success" and newsapi_result["sources"]:
                final_verdict = "True"
                confidence = 90
                method_used = "NewsAPI"
                source_links = newsapi_result["urls"]

        # ✅ Step 3: Kaggle Dataset
        if final_verdict is None:
            with st.spinner("Checking Kaggle dataset..."):
                kaggle_result = check_against_kaggle(cleaned)
            if kaggle_result["match_found"]:
                final_verdict = kaggle_result["verdict"]
                confidence = 85
                method_used = "Kaggle Dataset"
                source_links = [match["text"] for match in kaggle_result["matches"][:1]]

        # ✅ Step 4: Trusted Internet Sources
        if final_verdict is None:
            with st.spinner("Checking official and trusted sources..."):
                verification_results = verify_facts(cleaned)
            total_sources = sum(len(urls) for urls in verification_results.values())
            if total_sources > 0:
                final_verdict = "True" if total_sources >= 4 else "Fake"
                confidence = 75 if total_sources >= 4 else 50
                method_used = "Trusted Internet Sources"
                for urls in verification_results.values():
                    source_links.extend(urls)

        # ✅ Step 5: ML Model
        if final_verdict is None:
            with st.spinner("Using Machine Learning model as final step..."):
                ml_prediction = predict_news(cleaned)
                final_verdict = ml_prediction
                confidence = 60
                method_used = "Machine Learning"

        # ✅ Final Output
        st.header("🧾 Final Verdict")
        if final_verdict == "True":
            st.success("✅ This news is predicted to be **TRUE**.")
        elif final_verdict == "Fake":
            st.error("🚫 This news is predicted to be **FAKE**.")
        else:
            st.warning("⚠️ Unable to determine the verdict.")

        st.progress(confidence / 100)
        st.markdown(f"**🎯 Confidence Level:** {confidence}%")
        st.markdown(f"**🔍 Source of Verdict:** {method_used}")

        if gemini_explanation:
            with st.expander("💬 Gemini's Explanation"):
                st.write(gemini_explanation)

        if source_links:
            st.markdown("**🔗 Verified Sources:**")
            for link in source_links:
                if link.startswith("http"):
                    st.markdown(f"- [Link]({link})")
                else:
                    st.markdown(f"- {link}")

