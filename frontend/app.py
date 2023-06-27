import streamlit as st
import pandas as pd
import numpy as np
@st.cache_data
def connecting_to_database():
    from sshtunnel import SSHTunnelForwarder
    import psycopg2

    # SSH connection details
    ssh_host = st.secrets.ssh.host
    ssh_port =  int(st.secrets.ssh.port)
    ssh_username = st.secrets.ssh.user
    ssh_password = st.secrets.ssh.passwd

    # PostgreSQL connection details on the VM
    db_host = st.secrets.db.host  # or the IP address of the PostgreSQL server on the VM
    db_port = int(st.secrets.db.port) # the PostgreSQL port number on the VM
    db_user = st.secrets.db.user
    db_password = st.secrets.db.password

    # Establish the SSH tunnel
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=(db_host, db_port)
    ) as tunnel:
        # Connect to the PostgreSQL server through the SSH tunnel
        conn = psycopg2.connect(
            host='localhost',
            port=tunnel.local_bind_port,
            user=db_user,
            password=db_password,
            database = st.secrets.db.database
        )
        # open a cursor to perform database operations
        with conn.cursor() as cur:
            # execute a command to get a single row of data
            print("Successfully Connected!")
            cur.execute("""SELECT * from sold_houses LIMIT 5""")
            tables = cur.fetchall()
            #for table in tables:
            #    print(table[:][:5])
            cur.close()


        # Perform PostgreSQL operations
        # ...
        print("Success!!!!")
        # Close the PostgreSQL connection
        conn.close()
        return pd.DataFrame(tables)



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
    
    st.map(data)

    st.table(connecting_to_database())


def house_price_prediction_form():
    st.title('House Price Prediction')
    st.write('Fill in the details to predict the house price:')

    area = st.number_input('Area (in sq. ft.)')
    bedrooms = st.number_input('Bedrooms')
    bathrooms = st.number_input('Bathrooms')

    if st.button('Predict'):
        predicted_price = 100
        st.success(f'Predicted Price: ${predicted_price:.2f}')


# Testing Map Visualisation on the app
DATE_COLUMN =  'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data ...')
data = load_data(10000)
data_load_state.text('Done! (using st.cache)')



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