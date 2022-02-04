import streamlit as st
import pandas as pd
import plotly
import plotly.express as px

def return_luna_settlement(x):
    parse_list = []
    for value in list(x.values()):
        if 'denom' in value[0]:
                parse_list.append(value[0].get('amount'))

    return (max(parse_list) / 10**6)

def app():

    st.sidebar.header("Choose Grouping:")
    grouping_check = st.sidebar.checkbox('Group Without Rarirty'
    )

    if grouping_check:
        group_master = ['BLOCK_TIMESTAMP']
        merge_cols = ['BLOCK_TIMESTAMP', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    else:
        group_master = ['BLOCK_TIMESTAMP', 'RARITY']
        merge_cols = ['BLOCK_TIMESTAMP', 'RARITY', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    eggs = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/1d2218a1-e613-4585-a168-c562a8671cde/data/latest')
    eggs['NFT_LUNA_PRICE'] = eggs['EVENT_ATTRIBUTES'].apply(lambda x: return_luna_settlement(x))
    eggs.pop('EVENT_ATTRIBUTES')
    eggs['NFT_UST_PRICE_AT_PURCHASE'] = eggs['NFT_LUNA_PRICE'] * eggs['LUNA_UST_PRICE']


    eggs_rarity = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/284600cc-7b4c-4d47-ab50-dbdd528daf93/data/latest')
    eggs_rarity_merge = pd.merge(eggs, eggs_rarity[['TOKEN_ID', 'RARITY']], on='TOKEN_ID')

    eggs_rarity_merge = eggs_rarity_merge[merge_cols]
    eggs_rarity_merge['BLOCK_TIMESTAMP'] = pd.to_datetime(eggs_rarity_merge['BLOCK_TIMESTAMP'])
    eggs_rarity_merge.set_index('BLOCK_TIMESTAMP', inplace = True)
    eggs_rarity_merge.index = eggs_rarity_merge.index.round('D')

    total_df = eggs_rarity_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
    average_df = eggs_rarity_merge.groupby(group_master).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
    tx_count_df = eggs_rarity_merge.groupby(group_master).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
    tx_count_df = tx_count_df['TRANSACTION_COUNT']
    min_df = eggs_rarity_merge.groupby(group_master).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
    max_df = eggs_rarity_merge.groupby(group_master).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
    median_df = eggs_rarity_merge.groupby(group_master).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
    cum_sum = eggs_rarity_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

    eggs_master = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=group_master, ascending=False)

    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = eggs_master.columns,
        default = eggs_master.columns.min()
    )

    st.sidebar.header("Logarithmic / Linear:")
    log_lin = st.sidebar.checkbox('Enable Log'
    )

    if log_lin:
        t_f = True
    else:
        t_f = False

    if grouping_check:
        line = px.line(eggs_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(eggs_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)
    else:
        line = px.line(eggs_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RARITY", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(eggs_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RARITY", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        
        ust_pie_df = eggs_master[['RARITY', 'TOTAL_UST']].groupby(['RARITY']).sum()
        ust_pie = px.pie(ust_pie_df, values = 'TOTAL_UST', names = ust_pie_df.index, width = 1000)
        counts_pie_df = eggs_master[['RARITY', 'TRANSACTION_COUNT']].groupby(['RARITY']).sum()
        counts_pie = px.pie(counts_pie_df, values = 'TRANSACTION_COUNT', names = counts_pie_df.index, width = 1000)


        


    st.title('Eggs')
    st.text("""
    Egg Stats by Rarity
    """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(eggs_master)

    st.download_button(
    "Press to Download",
    eggs_master.to_csv().encode('utf-8'),
    "master_dataframe_eggs.csv",
    "text/csv",
    key='download-csv'
    )

    st.markdown("""
    # Line Chart Builder
    """)
    st.plotly_chart(line)

    st.markdown("""
    # Bar Chart Builder
    """)
    st.plotly_chart(bar)

    if not grouping_check:

        st.markdown("""
        ### UST Exchanged to Date by Rarity
        """)
        st.plotly_chart(ust_pie, use_column_width=True)

        st.markdown("""
        ### Transaction Count to Date by Rarity
        """)
        st.plotly_chart(counts_pie, use_column_width=True)