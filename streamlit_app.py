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
my_data_frame = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()
fruit_options = [row["FRUIT_NAME"] for row in my_data_frame]  # Extract fruit names

st.dataframe(data=my_data_frame, use_container_width=True)
st.stop()

# Convert the snowpark dataframe to Pandas DataFrame so we can use the loc function
pd_df = my_data_frame.to_pandas()
st.dataframe(pd_df)
st.stop()

# User selects ingredients
ingredients_list = st.multiselect('Select up to 5 ingredients:', fruit_options, max_selections=5)

if ingredients_list and name_on_order.strip():
    # Format ingredients as a comma-separated string
    ingredients_string = ', '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is: {search_on}.')
        
        st.subheader(f'{fruit_chosen} Nutrition Information')
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    
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
