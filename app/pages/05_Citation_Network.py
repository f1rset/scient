import streamlit as st

from components.views import rows, show_table

st.title("Related topics")
available = rows("related_topics", "SELECT 1 AS available FROM {table} LIMIT 1")
if not available:
    st.info("Network outputs are unavailable for this corpus.")
    st.stop()
topic = st.text_input("OpenAlex topic ID").strip().upper()
network = st.selectbox("Network", ["citation", "cooccurrence"])
if topic:
    show_table(rows("related_topics", """
        SELECT target_topic_id, weight FROM {table}
        WHERE source_topic_id = :topic AND network = :network
        ORDER BY weight DESC, target_topic_id LIMIT 50
    """, {"topic": topic, "network": network}), "No outgoing relationships were found.")
