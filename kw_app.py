import streamlit as st
from PIL import Image

import pandas as pd
import json



from multiapp import MultiApp
#from apps import home, not_nested, nested, loot, meteor, meteor_dust # import your app modules here
from apps import home, meteors, dust, eggs, loot, nested, main, loot_role, CSV

app = MultiApp()

st.set_page_config(layout="wide")
#levana = Image.open("levana.png")
#st.image(levana)

st.markdown("""
# Levana RandomEarth Sales Tracking
""")



# Add all your application here
app.add_app("Home", home.app)
app.add_app("Stats for all NFTs", main.app)
app.add_app("CSV files for all transactions", CSV.app)
app.add_app("Meteors", meteors.app)
app.add_app("Meteor Dust", dust.app)
app.add_app("Dragon Eggs (Not Nested)", eggs.app)
app.add_app("Nested Eggs", nested.app)
app.add_app("Loot", loot.app)
app.add_app("Loot (Role)", loot_role.app)




# The main app
app.run()