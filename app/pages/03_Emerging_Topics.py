import streamlit as st

from components.views import rows, show_table

st.title("Emerging topics")
year = st.number_input("Publication year", min_value=1800, max_value=2100, value=2025)
field = st.text_input("Field ID").strip()
indicator = st.selectbox("Ranking indicator", ["composite", "relative_growth", "acceleration", "share_change", "field_adjusted_growth"])
records = rows("emerging_topics", """
    SELECT topic_id, field_id, rank, score FROM {table}
    WHERE publication_year = :year AND indicator = :indicator AND (:field = '' OR field_id = :field)
    ORDER BY rank, topic_id LIMIT 100
""", {"year": year, "field": field, "indicator": indicator})
show_table(records, "Rankings are unavailable for this selection.")
if records:
    topic = st.selectbox("Explain a topic ranking", [row["topic_id"] for row in records])
    explanations = rows("indicator_explanations", """
        SELECT component, contribution FROM {table}
        WHERE topic_id = :topic AND publication_year = :year AND indicator = :indicator
        ORDER BY component LIMIT 100
    """, {"topic": topic, "year": year, "indicator": indicator})
    show_table(explanations, "No score contributions are available for this topic.")
