import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly
import plotly.express as px
import ast

def return_luna_settlement(x):
    parse_list = []
    for value in list(x.values()):
        if 'denom' in value[0]:
                parse_list.append(value[0].get('amount'))

    return (max(parse_list) / 10**6)

def app():
    st.sidebar.header("Choose Grouping:")
    grouping_check = st.sidebar.checkbox('Group Without Faction'
    )

    if grouping_check:
        group_master = ['BLOCK_TIMESTAMP', 'TYPE', 'ROLE']
        merge_cols = ['BLOCK_TIMESTAMP', 'TYPE', 'ROLE', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    else:
        group_master = ['BLOCK_TIMESTAMP', 'TYPE', 'ROLE', 'FACTION']
        merge_cols = ['BLOCK_TIMESTAMP', 'TYPE', 'ROLE', 'FACTION', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']


    loot = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/07ffb915-df99-46a2-a3b4-f1883d9fffce/data/latest')
    loot['NFT_LUNA_PRICE'] = loot['EVENT_ATTRIBUTES'].apply(lambda x: return_luna_settlement(x))
    loot.pop('EVENT_ATTRIBUTES')
    loot['NFT_UST_PRICE_AT_PURCHASE'] = loot['NFT_LUNA_PRICE'] * loot['LUNA_UST_PRICE']
    
    loot_faction = pd.read_csv('http://165.22.125.123/loot_nfts.csv')
    loot_ROLE_merge = pd.merge(loot, loot_faction[['token_id', 'traits']], left_on='TOKEN_ID', right_on='token_id', how='inner')
    loot_ROLE_merge['ROLE'] = loot_ROLE_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Role'))
    loot_ROLE_merge['FACTION'] = loot_ROLE_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Faction'))
    loot_ROLE_merge['TYPE'] = loot_ROLE_merge['traits'].apply(lambda x: ast.literal_eval(x).get('Type'))
    loot_ROLE_merge.pop('traits')

    loot_ROLE_merge = loot_ROLE_merge[merge_cols]
    loot_ROLE_merge['BLOCK_TIMESTAMP'] = pd.to_datetime(loot_ROLE_merge['BLOCK_TIMESTAMP'])
    loot_ROLE_merge.set_index('BLOCK_TIMESTAMP', inplace = True)
    loot_ROLE_merge.index = loot_ROLE_merge.index.floor('D')

    total_df = loot_ROLE_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
    average_df = loot_ROLE_merge.groupby(group_master).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
    tx_count_df = loot_ROLE_merge.groupby(group_master).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
    tx_count_df = tx_count_df['TRANSACTION_COUNT']
    min_df = loot_ROLE_merge.groupby(group_master).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
    max_df = loot_ROLE_merge.groupby(group_master).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
    median_df = loot_ROLE_merge.groupby(group_master).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
    cum_sum = loot_ROLE_merge.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

    loot_master = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=group_master, ascending=False)

    if not grouping_check:
        loot_master['RF'] = loot_master['ROLE'] + (' - ') + loot_master['FACTION']

    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = loot_master.columns,
        default = loot_master.columns.min()
    )

    st.sidebar.header("Logarithmic / Linear:")
    log_lin = st.sidebar.checkbox('Enable Log'
    )

    if log_lin:
        t_f = True
    else:
        t_f = False

    if grouping_check:
        line = px.line(loot_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = 'ROLE', orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(loot_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = 'ROLE', orientation = "v", template = "plotly_white", height = 600, width = 1000)
    else:
        line = px.line(loot_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RF", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(loot_master, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "RF", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        
        ust_pie_df = loot_master[['RF', 'TOTAL_UST']].groupby(['RF']).sum()
        ust_pie = px.pie(ust_pie_df, values = 'TOTAL_UST', names = ust_pie_df.index, width = 1000)
        counts_pie_df = loot_master[['RF', 'TRANSACTION_COUNT']].groupby(['RF']).sum()
        counts_pie = px.pie(counts_pie_df, values = 'TRANSACTION_COUNT', names = counts_pie_df.index, width = 1000)


    


    st.title('Loot')
    st.text("""
    Loot stats by Role - Faction
    """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(loot_master)

    st.download_button(
    "Press to Download",
    loot_master.to_csv().encode('utf-8'),
    "master_dataframe_loot.csv",
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
        ### UST Exchanged to Date by ROLE
        """)
        st.plotly_chart(ust_pie, use_column_width=True)

        st.markdown("""
        ### Transaction Count to Date by ROLE
        """)
        st.plotly_chart(counts_pie, use_column_width=True)