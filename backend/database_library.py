from configparser import ConfigParser
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

"""
IMPORTANT! Due to difficulty with SSH in Python, it's recommended to use below line in terminal to set up SSH connection, rather than using SSH via Python.

#ssh -L 15432:localhost:5432 -p 60684 dsda@ml-lab-159578ae-dd8f-485c-a42c-959a9302b5e7.uksouth.cloudapp.azure.com

# ALternatively, if you can make it work in Python, go ahead.

# SSH tunnelling Python code below, which wouldn't work for me (GA). This is for references and potential future work.

'''
import sshtunnel

with sshtunnel.open_tunnel(
    (config["ssh"]["host"], int(config["ssh"]["port"])),
    ssh_username=config["ssh"]["user"],
    ssh_password=config["ssh"]["pass"], 
    remote_bind_address=("127.0.0.1", 5432),
) as tunnel:
    
'''

# If SSH successful, below code should work.

"""

def get_config(filename: str ='config.ini', section: str ='db') -> dict:
    """ This function reads the specified config file, and allows the user to select a section to be use as parameters for further operations. It is used as part of other functions, such as query_db.

    Args:
        filename (str, optional): The filename of the config ini file. Defaults to 'remote_config.ini'.
        section (str, optional): The section of the config file to read. Defaults to 'db'.

    Raises:
        Exception: If the section specified does not exist within the config file.

    Returns:
        dict: A dictionary of the selected config parameters, which can be fed into psycopg connection function.
    """
    # Create a parser.
    parser = ConfigParser()
    # Read config file.
    parser.read(filename)

    # Get section, default to postgresql db.
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def test_connection():
    """ Checks that user can successfully connect to database according to parameters specified in config file. If successful, returns PostgreSQL version."""
    conn = None
    try:
        # read connection parameters
        params = get_config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        output = cur.fetchone()
        print(output)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def query_db(query: str, table_name: str = None, output_format: str = 'default'):
    """Connects to Database according to config parameters and allows user to perform a query on a chosen table. User can choose to have output returned directly or in the form of a DataFrame.

    Args:
        query (str): The user-defined query to send to the database.
        table_name (str, optional): When output_format is 'df', the table being queried must be specified here in order to extract the table headers. Defaults to None.
        output_format (str, optional): Specifies whether the output of the query should be converted to a DataFrame, or remain in default format. Defaults to 'default'.
    """
    conn = None
    try:
        # Read connection parameters.
        params = get_config()

        # Connect to the PostgreSQL database.
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.autocommit = True
		
        # Create a cursor.
        cur = conn.cursor()
        
	    # Execute a query.        
        cur.execute(query)
        

        print('Query executed.')

        # Get query output.
        output = cur.fetchall()

        if output_format == 'df':
        
            # Get column names (for if we want to make a dataframe from the output).
            cur.execute(f"Select * FROM {table_name} LIMIT 0")
            colnames = [desc[0] for desc in cur.description]

        else:
            pass      
                    
	# Close the communication with the PostgreSQL database.
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    if output_format == 'df':

        output_df = pd.DataFrame(data = output, columns = colnames)
        return output_df
    
    elif output_format == 'default':
        return output
    
    else:
        pass

def table_from_df(input_df: pd.DataFrame, table_name: str):
    """Creates a table in database from a DataFrame.

    Args:
        input_df (pd.DataFrame): The DataFrame object to import to database.
        table_name (str): The name of the new table in the database.
    """
    conn = None
    try:
        # read connection parameters
        params = get_config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	    # drop table if it already exists
        cur.execute(f'DROP TABLE IF EXISTS {table_name}')

        conn.commit()
        
        # load input DataFrame to database table        
        params = get_config('config.ini','sqlalchemy')
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

