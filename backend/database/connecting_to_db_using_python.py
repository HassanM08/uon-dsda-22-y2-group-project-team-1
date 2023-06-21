from sshtunnel import SSHTunnelForwarder
import psycopg2
import configparser

config = configparser.ConfigParser()
config.read("remote_config.ini")

# SSH connection details
ssh_host = config["ssh"]["host"]
ssh_port =  int(config["ssh"]["port"])
ssh_username = config["ssh"]["user"]
ssh_password = config["ssh"]["pass"]




# PostgreSQL connection details on the VM
db_host = config["db"]["host"]  # or the IP address of the PostgreSQL server on the VM
db_port = int(config["db"]["port"]) # the PostgreSQL port number on the VM
db_user = config["db"]["user"]
db_password = config["db"]["password"]

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
        database = config["db"]["database"]
    )
    # open a cursor to perform database operations
    with conn.cursor() as cur:
        # execute a command to get a single row of data
        print("Successfully Connected!")
        cur.execute("""SELECT *
FROM pg_catalog.pg_tables
WHERE schemaname != 'pg_catalog' AND 
    schemaname != 'information_schema';""")
        print(cur.fetchone())
        cur.close()


    # Perform PostgreSQL operations
    # ...
    print("Success!!!!")
    # Close the PostgreSQL connection
    conn.close()
