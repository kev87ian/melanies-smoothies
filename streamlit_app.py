# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write("Choose the fruits you want in your Custom Smoothie!")

# Get user input for the order name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your smoothie will be: ', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from the database
my_data_frame = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_options = [row["FRUIT_NAME"] for row in my_data_frame]  # Extract fruit names

# User selects ingredients
ingredients_list = st.multiselect('Select up to 5 ingredients:', fruit_options, max_selections=5)

if ingredients_list and name_on_order.strip():
    # Format ingredients as a comma-separated string
    ingredients_string = ', '.join(ingredients_list)

    # Fetch data for each chosen fruit
    for fruit_chosen in ingredients_list:
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}")
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    # Create the SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients) 
        VALUES ('{name_on_order}', '{ingredients_string}')
    """
    
    st.write(my_insert_stmt)  # Show the generated SQL statement

    # Submit order button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is Ordered!', icon="✅")
