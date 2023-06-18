import streamlit as st
import pandas as pd
import numpy as np


def display_undervalued_houses():
    st.title('House Price Prediction')
    listings = {'listingID':[1,2,3],
                'Location':["London", "Nottingham", "Manchester"],
                'Bedrooms':[2,3,2],
                'Bathrooms':[1,1,2],
                'Garden':[False, True, True],
                'Price': [250000, 275000, 260000],
                'Predicted_Price':[280000, 270000, 250000]}
    df = pd.DataFrame(listings)
    df['difference'] = df['Predicted_Price'] - df['Price']
    l = st.selectbox("Location:", np.insert(df.Location.unique(),0,'All'))
    if l=='All':
        st.table(df)
    else:
        st.table(df[df['Location']==l])

    ck = st.checkbox("Show undervalued houses")
    if ck==True:
        df.query("difference > 0").iloc[:,:-2]


def house_price_prediction_form():
    st.title('House Price Prediction')
    st.write('Fill in the details to predict the house price:')

    area = st.number_input('Area (in sq. ft.)')
    bedrooms = st.number_input('Bedrooms')
    bathrooms = st.number_input('Bathrooms')

    if st.button('Predict'):
        predicted_price = 100
        st.success(f'Predicted Price: ${predicted_price:.2f}')

# Main App
def main():
    st.sidebar.title('Navigation')
    app_mode = st.sidebar.selectbox('Select App Mode', ['Undervalued Houses', 'House Price Prediction'])

    if app_mode == 'Undervalued Houses':
        display_undervalued_houses()
    elif app_mode == 'House Price Prediction':
        house_price_prediction_form()

if __name__ == '__main__':
    main()