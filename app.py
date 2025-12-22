import pandas as pd
import streamlit as st

from data_source.noon_scaper import scrape

search_keyword = st.text_input("Search keyword")

if search_keyword:
    products = scrape(search_keyword, 3)
    data = pd.DataFrame(map(lambda p: p.model_dump(), products))
    st.write(data)

    freq_df = (
        pd.cut(data["price"], bins=5)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    freq_df.columns = ["price_range", "count"]
    freq_df["price_range_name"] = freq_df["price_range"].astype(str)
    st.bar_chart(
        freq_df,
        x='price_range_name', y='count',
        x_label='Price Range', y_label='Count',
        sort='price_range'
    )
