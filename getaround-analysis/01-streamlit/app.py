# Import necessary libraries
import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import io
import requests

# Function to create home page
st.set_page_config(
    page_title="Getaround Project",
    page_icon="🚗",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/nizar-sayad-26b18411a/',
        'Report a bug': "https://www.linkedin.com/in/nizar-sayad-26b18411a/",
        'About': "https://www.linkedin.com/in/nizar-sayad-26b18411a/"
    }
  )

st.title('Getaround Insights Dashboard')
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Data Overview", "Data Analysis", "Solution Analysis", "Price Estimation"])
with tab1:
  st.write("""
## Home

### Context

Getaround users book cars for a range of time periods, spanning from an hour to a few days. They are expected to return the car punctually, however, occasional delays do occur.

These delays can cause significant friction for the next driver, particularly if the car was due to be rented again on the same day. Our customer service often reports instances of users expressing dissatisfaction because they had to wait for the car to be returned from the previous rental or even had to cancel their rental because the car wasn't returned on time.

To address these issues, we've decided to implement a minimum delay between two rentals. This means a car won't appear in the search results if the requested checkin or checkout times are too close to an already booked rental.

While this solution addresses the late checkout issue, it may also potentially impact Getaround/owners' revenues. Thus, we need to strike the right balance.

There are key decisions that our Product Manager needs to make:

- **Threshold**: What should be the minimum delay duration?
- **Scope**: Should we enable this feature for all cars, or only Connect cars?

To make an informed decision, we need to gather data insights, and we try to focus on some key areas such as:

- What percentage of our owner's revenue could potentially be affected by this feature?
- How many rentals would be affected by this feature, depending on the threshold and scope we choose?
- How often are drivers late for the next check-in? How does it affect the next driver?
- How many problematic cases will this resolve depending on the chosen threshold and scope?

""")

         

# Load the data
@st.cache_data
def load_delay_data():
    data = pd.read_excel('get_around_delay_analysis.xlsx')
    return data
delay = load_delay_data()

@st.cache_data
def load_price_data():
    data = pd.read_csv('get_around_pricing_project.csv')
    return data
price = load_price_data()


with tab2:
  st.write("""
    ## Data Overview
    """)
  col1, col2 = st.columns([1,1.5])
  with col1:
    st.write("""
    ### Data Description
    """)
    # Basic stats about the dataframe
    st.write(f"Number of rows : {delay.shape[0]}")
    st.write(f"Number of columns : {delay.shape[1]}")
    st.write(f"Displaying variable types and number of non-null values :")
    buffer = io.StringIO()
    delay.info(verbose=True,buf=buffer)
    s = buffer.getvalue()
    st.text(s)
    st.write("Displaying percentage of missing values :")
    # Display percentage of missing values
    @st.cache_data
    def missing_values(df):
        missing_values = pd.DataFrame(np.round(100*df.isnull().sum()/df.shape[0]), columns=['% missing values'])
        return missing_values
    missing_values = missing_values(delay)
    st.dataframe(missing_values)
  
  with col2:
    st.write(""" ### Data Preview """)
    st.write(f"Displaying first 5 rows of the dataframe :")
    st.dataframe(delay.head())
    st.write("Displaying basic statistics about the dataframe :")
    # Display basic statistics
    data_desc = delay.describe(include='all')
    st.dataframe(data_desc)

with tab3:
  st.write("""
  ## Data Analysis
  """)
  option = st.selectbox('What would you like to analyze?', ['Numerical variables', 'Categorical variables', 'In-depth analysis'])
  # In-depth analysis
  # Histograms for continuous variables
  # Creating a new column for delay category and displaying its distribution
  @st.cache_data
  def delay_category():
    delay['delay_category'] = 'no delay'
    delay.loc[delay['delay_at_checkout_in_minutes'] > 0, 'delay_category'] = 'delay < 30 minutes'
    delay.loc[delay['delay_at_checkout_in_minutes'] >= 30, 'delay_category'] = '30 minutes <= delay < 1 hour'
    delay.loc[delay['delay_at_checkout_in_minutes'] >= 60, 'delay_category'] = '1 hour <= delay < 2 hours'
    delay.loc[delay['delay_at_checkout_in_minutes'] >= 120, 'delay_category'] = '2 hours <= delay'
    return delay
  
  @st.cache_data
  def real_delay():
    # fill missing values with 720 minutes (12 hours) as per the documentation provided
    delay['time_delta_with_previous_rental_in_minutes'].fillna(720, inplace=True)
    # fill missing values with 0 minutes
    delay['delay_at_checkout_in_minutes'].fillna(0, inplace=True)
    delay_true = delay[delay['delay_at_checkout_in_minutes'] > 0]
    delay_false = delay[delay['delay_at_checkout_in_minutes'] <= 0]
    # Calculating the actual delay in minutes for each rental
    delay.loc[:,'real_time_delta'] = delay['time_delta_with_previous_rental_in_minutes'] - delay['delay_at_checkout_in_minutes']
    delay_true.loc[:,'real_time_delta'] = delay_true['time_delta_with_previous_rental_in_minutes'] - delay_true['delay_at_checkout_in_minutes']
    delay_false.loc[:,'real_time_delta'] = delay_false['time_delta_with_previous_rental_in_minutes'] - delay_false['delay_at_checkout_in_minutes']
    # Creating a new column 'waited_for_rental' to track if the user waited for the previous rental to be returned
    delay.loc[:,'waited_for_rental'] = delay['real_time_delta'].apply(lambda x: 1 if x<0 else 0 if x>=0 else np.nan)
    delay_true.loc[:,'waited_for_rental'] = delay_true['real_time_delta'].apply(lambda x: 1 if x<0 else 0 if x>=0 else np.nan)
    delay_false.loc[:,'waited_for_rental'] = delay_false['real_time_delta'].apply(lambda x: 1 if x<0 else 0 if x>=0 else np.nan)
    return delay, delay_true, delay_false

  delay = delay_category()
  delay_new, delay_true, delay_false = real_delay()
  if option == 'Numerical variables':
    for col in delay.select_dtypes('float'):
        if col=='delay_at_checkout_in_minutes':
          col1, col2 = st.columns([1,1])
          fig = px.histogram(delay, x=col, title=f'Distribution of {col.replace("_", " ")}', marginal='box')
          col1.plotly_chart(fig)
          # Calculating late check-ins percentage
          late_checkins = delay[delay['delay_at_checkout_in_minutes'] > 0].shape[0]*100/delay.shape[0]
          col1.caption(f'Percentage of late checkins: {np.round(late_checkins)}')
          # Plotting the distribution of the delay at checkout after removing outliers
          Q1 = delay['delay_at_checkout_in_minutes'].quantile(0.25)
          Q3 = delay['delay_at_checkout_in_minutes'].quantile(0.75)
          IQR = Q3 - Q1
          lower = Q1 - 1.5*IQR
          upper = Q3 + 1.5*IQR
          fig = px.histogram(delay[delay['delay_at_checkout_in_minutes'].between(Q1,Q3)], x='delay_at_checkout_in_minutes', title=f'Distribution of delay at checkout (no outliers)', marginal='box')
          col2.plotly_chart(fig)
        
        else:
          fig = px.histogram(delay, x=col, title=f'Distribution of {col.replace("_", " ")}', marginal='box')
          st.plotly_chart(fig)

  elif option == 'Categorical variables':
    col1, col2 = st.columns([1,1])
    # Pie charts for categorical variables
    for col in delay.select_dtypes('object'):
        if col=='delay_category':
          fig = px.pie(delay, names=col, title=f'Distribution of {col.replace("_", " ")}')
          col2.plotly_chart(fig)
          # Displaying the number of unique cars
          unique_cars = delay['car_id'].nunique()
          col2.write(f'**Number of unique cars: {unique_cars}**')
        else:
          fig = px.pie(delay, names=col, title=f'Distribution of {col.replace("_", " ")}')
          col1.plotly_chart(fig)


  else:
    col1, col2 = st.columns([1,1])
    delay_categories = ['no_delay', 'delay < 30 minutes', '30 minutes <= delay < 1 hour', '1 hour <= delay < 2 hours', '2 hours <= delay']

    # Bar plots for number of rentals per delay category
    grouped = delay.groupby(['checkin_type'])['delay_category'].value_counts(normalize=True).reset_index()
    grouped['count'] = delay.groupby(['checkin_type'])['delay_category'].value_counts().reset_index()['count']
    fig = px.bar(grouped, x='checkin_type',y='proportion', color='delay_category', title='Proportion of rentals per delay category')
    col1.plotly_chart(fig)
    fig = px.bar(grouped, x='checkin_type',y='count', color='delay_category', title='Number of rentals per delay category')
    col2.plotly_chart(fig)

    # Box plot for distribution of time delta with previous rental in minutes per delay category
    fig = px.box(delay, x='delay_category', y='time_delta_with_previous_rental_in_minutes', color='delay_category',category_orders={'delay_category':delay_categories}, title='Distribution of time delta with previous rental in minutes per delay category')
    col1.plotly_chart(fig)

    # Bar plots for average delay at checkout and time between two rentals per checkin type
    grouped = delay_true.groupby(['checkin_type'])['delay_at_checkout_in_minutes'].mean().reset_index()
    fig = px.bar(grouped, x='checkin_type', y='delay_at_checkout_in_minutes', color='checkin_type', title='Average delay at checkout per checkin type')
    col2.plotly_chart(fig)
    grouped = delay_true.groupby(['checkin_type'])['time_delta_with_previous_rental_in_minutes'].mean().reset_index()
    fig = px.bar(grouped, x='checkin_type', y='time_delta_with_previous_rental_in_minutes', color='checkin_type', title='Average time between two rentals per checkin type')
    col1.plotly_chart(fig)

    # Calculating the actual delay in minutes for each rental
    delay.loc[:,'real_time_delta'] = delay['time_delta_with_previous_rental_in_minutes'] - delay['delay_at_checkout_in_minutes']
    delay_true.loc[:,'real_time_delta'] = delay_true['time_delta_with_previous_rental_in_minutes'] - delay_true['delay_at_checkout_in_minutes']

    # Creating a new column 'waited_for_rental' to track if the user waited for the previous rental to be returned
    delay.loc[:,'waited_for_rental'] = delay['real_time_delta'].apply(lambda x: 1 if x<0 else 0 if x>=0 else np.nan)
    delay_true.loc[:,'waited_for_rental'] = delay_true['real_time_delta'].apply(lambda x: 1 if x<0 else 0 if x>=0 else np.nan)

    # Bar plot of average time between two rentals per checkin type
    grouped = delay_true.groupby(['checkin_type'])['real_time_delta'].mean().reset_index()
    fig = px.bar(grouped, x='checkin_type', y='real_time_delta', color='checkin_type', title='Average REAL time between two rentals per checkin type')
    col2.plotly_chart(fig)

    # Bar plot of number of drivers that waited for rentals
    grouped = delay.groupby(['checkin_type'])['waited_for_rental'].value_counts().reset_index()
    grouped['waited_for_rental'] = grouped['waited_for_rental'].apply(lambda x: 'waited for rental' if x==1 else 'did not wait for rental')
    fig = px.bar(grouped, x='checkin_type',y='count', color='waited_for_rental', title='Number of drivers that waited for rentals')
    col1.plotly_chart(fig)

    # Pie chart of distribution of drivers who waited for rentals
    fig = px.pie(delay, names='waited_for_rental', title=f'Distribution of drivers who waited for rentals')
    col2.plotly_chart(fig)

with tab4:
  delay_new, delay_true, delay_false = real_delay()
  st.write('## Solution analysis')
  # Adding a slider for the minimum delay threshold
  min_delay = st.slider('**Select a minimum delay threshold:**', min_value=0, max_value=720)
  
  # Filtering the data based on the selected minimum delay threshold
  filtered_delay = delay_new[delay_new['time_delta_with_previous_rental_in_minutes'] >= min_delay]
  filtered_delay_true = delay_true[delay_true['time_delta_with_previous_rental_in_minutes'] >= min_delay]
  filtered_delay_false = delay_false[delay_false['time_delta_with_previous_rental_in_minutes'] >= min_delay] # Consider fillna for filtered delays
  
  st.write(f'### Minimum delay threshold: {min_delay} minutes')
  impacted_rentals = delay_new[delay_new['time_delta_with_previous_rental_in_minutes'] < min_delay]
  st.write(f'### Total number of impacted rentals: {impacted_rentals["checkin_type"].count()}') 
  impacted_connect = delay_new[(delay_new["checkin_type"]=="connect") & (delay_new['time_delta_with_previous_rental_in_minutes'] < min_delay)]
  st.write(f'### Total number of impacted connect rentals: {impacted_connect["checkin_type"].count()}')

  impacted_mobile = delay_new[(delay_new["checkin_type"]=="mobile") & (delay_new['time_delta_with_previous_rental_in_minutes'] < min_delay)]
  st.write(f'### Total number of impacted mobile rentals: {impacted_mobile["checkin_type"].count()}')



  col1, col2 = st.columns(2)
  # Plotting the total count of rentals per checkin type for the total data
  fig = px.bar(filtered_delay_false['checkin_type'].value_counts().reset_index(), x='checkin_type',y='count', color='checkin_type', title='Number of rentals without delay per checkin type')
  col1.plotly_chart(fig)

  # Plotting the total count of rentals per checkin type for the total data
  fig = px.bar(filtered_delay_true['checkin_type'].value_counts().reset_index(), x='checkin_type',y='count', color='checkin_type', title='Number of rentals that experienced a delay per checkin type')
  col2.plotly_chart(fig)

  # Plotting the average delay at checkout per checkin type for the filtered data
  # Grouping the filtered data by checkin type
  grouped = filtered_delay.groupby('checkin_type')['waited_for_rental'].value_counts().reset_index()
  fig = px.bar(grouped, x='checkin_type', y='count', color='waited_for_rental', title='Number of rentals that waited for the previous rental to be returned per checkin type')
  col1.plotly_chart(fig)

with tab5:
    st.write("""
    ## Car Price Prediction
    Fill in the details about the car to get a predicted rental price.
    """)

    # Start a form
    with st.form(key="prediction_form"):
        st.write("### Car Information")
        
        # For categorical features, we can use a select box in the form
        model_key = st.selectbox("Model Key", options=price["model_key"].unique().tolist(), key="model_key")
        fuel = st.selectbox("Fuel", options=price["fuel"].unique().tolist(), key="fuel")
        paint_color = st.selectbox("Paint Color", options=price["paint_color"].unique().tolist(), key="paint_color")
        car_type = st.selectbox("Car Type", options=price["car_type"].unique().tolist(), key="car_type")

        # For numerical features, we can use a number input in the form
        mileage = st.number_input("Mileage", value=0, step=10, key="mileage")
        engine_power = st.number_input("Engine Power", value=0, step=10, key="engine_power")

        # For boolean features, we can use a checkbox in the form
        private_parking_available = st.checkbox("Private Parking Available", key="private_parking_available")
        has_gps = st.checkbox("Has GPS", key="has_gps")
        has_air_conditioning = st.checkbox("Has Air Conditioning", key="has_air_conditioning")
        automatic_car = st.checkbox("Automatic Car", key="automatic_car")
        has_getaround_connect = st.checkbox("Has Getaround Connect", key="has_getaround_connect")
        has_speed_regulator = st.checkbox("Has Speed Regulator", key="has_speed_regulator")
        winter_tires = st.checkbox("Winter Tires", key="winter_tires")

        # When the user hits submit, call the API with these values and display the prediction
        submit_button = st.form_submit_button(label="Predict Price")

        if submit_button:
            # Prepare the data for the API
            df = pd.DataFrame({
                "model_key": model_key,
                "mileage": mileage,
                "engine_power": engine_power,
                "fuel": fuel,
                "paint_color": paint_color,
                "car_type": car_type,
                "private_parking_available": private_parking_available,
                "has_gps": has_gps,
                "has_air_conditioning": has_air_conditioning,
                "automatic_car": automatic_car,
                "has_getaround_connect": has_getaround_connect,
                "has_speed_regulator": has_speed_regulator,
                "winter_tires": winter_tires
            }, index=[0])
            
            data = df.to_dict(orient='records')[0]
            # Make sure your API is able to receive POST requests
            response = requests.post('http://ec2-35-180-36-210.eu-west-3.compute.amazonaws.com/predict', json=data)
            # Display the prediction
            st.write("### Predicted Price")
            st.write(f"Based on the information provided, the estimated rental price is: {int(response.json()['prediction'])} $")




