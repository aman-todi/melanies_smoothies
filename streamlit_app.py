# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_df = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_df.to_pandas()
st.dataframe(pd_df)
st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruits_table,
    max_selections=5)
if name_on_order and ingredients_list:
    ingredients_string = ""
    for fruit in ingredients_list:
        ingredients_string += fruit + ' '
        # Display smoothiefruit nutrition information
        fruit_api_name = session.table("smoothies.public.fruit_options").select(col('search_on')).where(col('fruit_name')==fruit).collect()[0][0]
        api_req_string = "https://my.smoothiefroot.com/api/fruit/" + fruit_api_name
        smoothiefroot_response = requests.get(api_req_string)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        
    #st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '"""+ name_on_order +"""')"""
    
    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+'!', icon="✅")

