# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

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

    # Create the SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients) 
        VALUES ('{name_on_order}', '{ingredients_string}')
    """
    
    st.write(my_insert_stmt)  # Show the generated SQL statement

    # Submit order button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is Ordered!', icon="✅")
