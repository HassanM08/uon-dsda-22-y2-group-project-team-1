import streamlit as st
import pandas as pd
import numpy as np
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