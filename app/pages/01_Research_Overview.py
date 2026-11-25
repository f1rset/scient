import streamlit as st

from components.views import rows, show_table

st.title("Research overview")
field = st.text_input("Field ID").strip()
records = rows("topic_overview", """
    SELECT topic_id, topic_name, field_name, publication_count FROM {table}
    WHERE (:field = '' OR field_id = :field)
    ORDER BY publication_count DESC, topic_id LIMIT 100
""", {"field": field})
show_table(records, "No topics are available for the selected field.")
