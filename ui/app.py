"""Streamlit demo chatbot UI (Role D, FR-4.5, FR-4.6).

Run with: streamlit run ui/app.py
"""

import html
import logging

import streamlit as st

from dehallucinator import pipeline
from dehallucinator.config import MAX_INPUT_CHARS
from dehallucinator.ui_render import claim_html, claim_rows, load_samples, trust_colour

logger = logging.getLogger(__name__)
OWN_ANSWER = "Paste your own answer"

st.set_page_config(page_title="Dehallucinator", page_icon="🔎")
st.title("Dehallucinator")
st.caption("Checks an AI answer against Wikipedia and a local knowledge base, then corrects it.")

samples = load_samples()
titles = [OWN_ANSWER] + [sample["title"] for sample in samples]
choice = st.selectbox("Sample answer", titles, index=1)
default = "" if choice == OWN_ANSWER else samples[titles.index(choice) - 1]["answer"]

text = st.text_area("AI answer", value=default, height=160, max_chars=MAX_INPUT_CHARS, key=choice)

if st.button("Check", type="primary"):
    try:
        with st.spinner("Checking claims..."):
            result = pipeline.check_answer(text)
    except ValueError as exc:
        st.error(f"Invalid input: {exc}")
    except Exception:
        logger.exception("check_answer failed in the UI")
        st.error("Something went wrong while checking this answer. Please try again.")
    else:
        colour = trust_colour(result.trust_score)
        st.markdown(
            f'<h3>Trust score: <span style="color:{colour}">{result.trust_score:.1f}</span>'
            " / 100</h3>",
            unsafe_allow_html=True,
        )

        st.subheader("Claims")
        rows = claim_rows(result)
        if not rows:
            st.info("No factual claims found in this answer.")
        for row in rows:
            # claim_html escapes every piece of answer and evidence text.
            st.markdown(claim_html(row), unsafe_allow_html=True)

        st.subheader("Corrected answer")
        st.markdown(
            f'<div style="white-space:pre-wrap;">{html.escape(result.corrected)}</div>',
            unsafe_allow_html=True,
        )
