import streamlit as st

from components.views import add_series, rows

st.title("Topic explorer")
topic = st.text_input("OpenAlex topic ID", placeholder="T12345").strip().upper()
first = st.number_input("First publication year", min_value=1800, max_value=2100, value=2015)
last = st.number_input("Last publication year", min_value=1800, max_value=2100, value=2025)
indicator = st.selectbox("Indicator", ["publication_count", "relative_growth", "topic_share"])
if not topic or first > last:
    st.info("Enter a topic ID and a valid publication period.")
    st.stop()
records = rows("topic_trends", """
    SELECT publication_year, publication_count, relative_growth, topic_share FROM {table}
    WHERE topic_id = :topic AND publication_year BETWEEN :first AND :last
    ORDER BY publication_year LIMIT 350
""", {"topic": topic, "first": first, "last": last})
add_series(records, indicator)
