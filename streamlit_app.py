#toDO:: Bring in mapping API
#toDO:: calculate A1A3 emissions
#toDO:: plot emissions and beautify dashboard

import pandas as pd
import streamlit as st
import altair as alt


def preprocess_data(df):
    """
    Preprocess the DataFrame: Combine 'Type Name' and 'Family Name', and convert 'Volume' to float.
    """
    df['Family Name: Type Name'] = df['Family Name'] + ': ' + df['Type Name']
    df['Volume'] = df['Volume'].str.extract(r'(\d+\.?\d*)')[0].astype(float)
    return df

def summarize_data(df, parameter_1='Family Name: Type Name', parameter_2='Volume'):
    """
    Summarize the data: Provide summed up volumes and counts.
    """
    summed_volumes = df.groupby(parameter_1)[parameter_2].sum().sort_values(ascending=False)
    count_items = df.groupby(parameter_1)[parameter_2].count()
    total_volume = summed_volumes.sum()
    total_count = count_items.sum()
    return summed_volumes, count_items, total_volume, total_count

def top_10_with_other(summed_volumes):
    """
    Create a new series with the top 10 items and an "Other" category for the rest.
    """
    top_10 = summed_volumes.head(20)
    others = pd.Series([summed_volumes.iloc[10:].sum()], index=['Other'])
    top_10_with_others = pd.concat([top_10, others])
    # Set the index name and column name
    top_10_with_others.index.name = 'Category'
    top_10_with_others.name = 'Volume'
    return top_10_with_others

def plot_bar_chart(summed_volumes):
    """
    Plot a horizontal bar chart for the summed up volumes.
    """
    st.bar_chart(top_10_with_other(summed_volumes), horizontal=True)


@st.cache_data
def donut_chart_families(df, use_container_width: bool):
    # Summing up the "Volume" column by grouping "Family Names"
    grouped_df = df.groupby("Family Name")["Volume"].sum().sort_values(ascending=False).reset_index()
    grouped_df.columns = ["Family Name", "Volume"]

    # Creating the donut chart
    chart = alt.Chart(grouped_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Volume", type="quantitative"),
        color=alt.Color(field="Family Name", type="nominal"),
    )

    st.altair_chart(chart, theme="streamlit", use_container_width=True)

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Revit Project Data Analysis")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, low_memory=False)
        df = preprocess_data(df)

        summed_volumes, count_items, total_volume, total_count = summarize_data(df)

        st.header("Volume by Family Names and Type Names")
        donut_chart_families(df, use_container_width=True)
        plot_bar_chart(summed_volumes)

        st.header("Project Volume")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=f'Total Volume (m3)', value=f'{round(total_volume, 2)}')
        with col2:
            st.metric(label=f'Total Count of Items', value=f'{round(total_count)}')
        st.header("Summed Volumes by Family Name: Type Name")
        st.table(top_10_with_other(summed_volumes))


if __name__ == "__main__":
    main()
