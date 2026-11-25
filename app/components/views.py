import plotly.graph_objects as go
import streamlit as st

from services.warehouse import query


@st.cache_data(ttl=120, show_spinner=False)
def fetch(table, statement, parameters=None):
    return query(table, statement, parameters)


def rows(table, statement, parameters=None):
    try:
        return fetch(table, statement, parameters)
    except ValueError as error:
        st.info(str(error))
    except Exception:
        st.warning("The Serving data could not be read. Check the warehouse resource and app permissions.")
    st.stop()


def show_table(results, empty_message):
    if results:
        st.dataframe(results, hide_index=True)
    else:
        st.info(empty_message)


def add_series(records, indicator):
    if records:
        figure = go.Figure(go.Scatter(
            x=[row["publication_year"] for row in records],
            y=[row[indicator] for row in records],
            mode="lines+markers",
            connectgaps=False,
        ))
        figure.update_layout(xaxis_title="Publication year", yaxis_title=indicator.replace("_", " ").title())
        st.plotly_chart(figure, use_container_width=True)
    else:
        st.info("No trends are available for this topic and period.")
