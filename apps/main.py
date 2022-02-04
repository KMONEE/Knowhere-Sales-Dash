import streamlit as st
import streamlit.components.v1 as components
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
    grouping_check = st.sidebar.checkbox('Group Without NFT Type'
    )

    if grouping_check:
        group_master = ['BLOCK_TIMESTAMP']
        merge_cols = ['BLOCK_TIMESTAMP', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    else:
        group_master = ['BLOCK_TIMESTAMP', 'NFT_TYPE']
        merge_cols = ['BLOCK_TIMESTAMP', 'NFT_TYPE', 'NFT_LUNA_PRICE', 'NFT_UST_PRICE_AT_PURCHASE']

    meteors = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/cd4f0436-4d17-4017-bfa2-8cf1b902a94e/data/latest')
    meteor_dust = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/6c05308b-2560-47f5-8284-8b8dc8566506/data/latest')
    eggs = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/1d2218a1-e613-4585-a168-c562a8671cde/data/latest')
    loot = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/07ffb915-df99-46a2-a3b4-f1883d9fffce/data/latest')
    nested_egg = pd.read_json('https://api.flipsidecrypto.com/api/v2/queries/1e0c6650-5f1c-4281-98ed-de7d3e591d7d/data/latest')
    #IT IS ABSOLUTELY CRUCIAL THAT YOU DO NOT CHANGE THE ORIGINAL NAMES OF THE DATAFRAME COLUMNS ON VELOCITY

    #MUST STORE IN A DICTIONARY 
    current_nft_dict = {'nested_egg':nested_egg, 'loot':loot, 'eggs':eggs, 'meteor_dust':meteor_dust, 'meteors':meteors}

    for nft in current_nft_dict:
        current_nft_dict[nft]['NFT_LUNA_PRICE'] = current_nft_dict[nft]['EVENT_ATTRIBUTES'].apply(lambda x: return_luna_settlement(x))
        current_nft_dict[nft].pop('EVENT_ATTRIBUTES')
        current_nft_dict[nft]['NFT_UST_PRICE_AT_PURCHASE'] = current_nft_dict[nft]['NFT_LUNA_PRICE'] * current_nft_dict[nft]['LUNA_UST_PRICE']

    nft_luna_price_df = []
    for nft in current_nft_dict:
        #renames columns from Flipside dataframes according to NFT
        nft_luna_price_df.append(current_nft_dict[nft][merge_cols])

    nft_luna_price_df = pd.concat(nft_luna_price_df)
    nft_luna_price_df['BLOCK_TIMESTAMP'] = pd.to_datetime(nft_luna_price_df['BLOCK_TIMESTAMP'])
    nft_luna_price_df.set_index('BLOCK_TIMESTAMP', inplace = True)
    nft_luna_price_df.index = nft_luna_price_df.index.round('D')
    #nft_luna_price_df


    total_df = nft_luna_price_df.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST'})
    average_df = nft_luna_price_df.groupby(group_master).mean().rename(columns={'NFT_LUNA_PRICE':'AVERAGE_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'AVERAGE_UST'})
    tx_count_df = nft_luna_price_df.groupby(group_master).count().rename(columns={'NFT_LUNA_PRICE':'TRANSACTION_COUNT'})
    tx_count_df = tx_count_df['TRANSACTION_COUNT']
    min_df = nft_luna_price_df.groupby(group_master).min().rename(columns={'NFT_LUNA_PRICE':'MIN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MIN_UST'})
    max_df = nft_luna_price_df.groupby(group_master).max().rename(columns={'NFT_LUNA_PRICE':'MAX_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MAX_UST'})
    median_df = nft_luna_price_df.groupby(group_master).median().rename(columns={'NFT_LUNA_PRICE':'MEDIAN_LUNA', 'NFT_UST_PRICE_AT_PURCHASE':'MEDIAN_UST'})
    cum_sum = nft_luna_price_df.groupby(group_master).sum().rename(columns={'NFT_LUNA_PRICE':'TOTAL_LUNA_CUMULATIVE', 'NFT_UST_PRICE_AT_PURCHASE':'TOTAL_UST_CUMULATIVE'}).cumsum(axis=0)

    master_df = pd.concat([total_df, tx_count_df, average_df, min_df, max_df, median_df, cum_sum], axis = 1).reset_index().sort_values(by=group_master, ascending=False)

    st.sidebar.header("Choose Columns:")
    columns = st.sidebar.multiselect(
        "Select the columns to plot",
        options = master_df.columns,
        default = master_df.columns.min()
    )

    st.sidebar.header("Logarithmic / Linear:")
    log_lin = st.sidebar.checkbox('Enable Log'
    )

    if log_lin:
        t_f = True
    else:
        t_f = False

    if grouping_check:
        line = px.line(master_df, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(master_df, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, orientation = "v", template = "plotly_white", height = 600, width = 1000)

    else:
        line = px.line(master_df, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "NFT_TYPE", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        bar = px.bar(master_df, x = "BLOCK_TIMESTAMP", log_y = t_f, y = columns, color = "NFT_TYPE", orientation = "v", template = "plotly_white", height = 600, width = 1000)
        ust_pie_df = master_df[['NFT_TYPE', 'TOTAL_UST']].groupby(['NFT_TYPE']).sum()
        ust_pie = px.pie(ust_pie_df, values = 'TOTAL_UST', names = ust_pie_df.index, width = 1000)
        counts_pie_df = master_df[['NFT_TYPE', 'TRANSACTION_COUNT']].groupby(['NFT_TYPE']).sum()
        counts_pie = px.pie(counts_pie_df, values = 'TRANSACTION_COUNT', names = counts_pie_df.index, width = 1000)


    st.title('Tracking for all NFTS (not counting rarity)')
    # st.text("""
    # V1 of the sales tracking dash for RE sales only; rarity stats next followed by 
    # Knowhere
    # """)
    st.markdown("""
    ---
    """)

    st.markdown("""
    ### Master Dataframe
    """)
    st.dataframe(master_df)

    st.download_button(
    "Press to Download",
    master_df.to_csv().encode('utf-8'),
    "master_dataframe_all_nft.csv",
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