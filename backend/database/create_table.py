import psycopg2
from config import config
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def table_from_df(input_df, table_name):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	    # drop table if it already exists
        cur.execute(f'DROP TABLE IF EXISTS {table_name}')

        conn.commit()
        
        # load input DataFrame to database table        
        params = config('config.ini','sqlalchemy')
        url = URL.create(**params)
        engine = create_engine(url)
        input_df.to_sql(table_name, engine, index = False)  # We should look at the 'if_exists' parameter of this method.

        print(f'Table {table_name} created')    
                       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
