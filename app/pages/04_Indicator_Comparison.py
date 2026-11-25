import streamlit as st

from components.views import rows, show_table

st.title("Indicator comparison")
topic = st.text_input("OpenAlex topic ID").strip().upper()
year = st.number_input("Publication year", min_value=1800, max_value=2100, value=2025)
if not topic:
    st.info("Enter a topic ID to compare its rankings.")
    st.stop()
show_table(rows("emerging_topics", """
    SELECT indicator, rank, score FROM {table}
    WHERE topic_id = :topic AND publication_year = :year ORDER BY indicator LIMIT 100
""", {"topic": topic, "year": year}), "Indicator rankings are unavailable for this topic and year.")
