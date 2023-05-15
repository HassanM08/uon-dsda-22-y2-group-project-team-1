import psycopg2
import pandas as pd
from config import config

def query(query: str, table_name: str, output: str = 'default'):
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
        
	    # execute a statement        
        cur.execute(query)

        print('Query executed.')

        # get query output
        output = cur.fetchall()

        if output == 'df':
        
            # get column names (for if we want to make a dataframe from the output)
            cur.execute(f"Select * FROM {table_name} LIMIT 0")
            colnames = [desc[0] for desc in cur.description]

        else:
            pass      
                    
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit() # This is required for queries that alter the database.
            conn.close()
            print('Database connection closed.')

    if output == 'df':

        output_df = pd.DataFrame(data = output, columns = colnames)
        return output_df
    
    elif output == 'default':
        return output
    
    else:
        pass

