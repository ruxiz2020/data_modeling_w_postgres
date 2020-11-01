import psycopg2
from sql_queries import create_table_queries, drop_table_queries

def create_database():
    """
    - Creates and sparkifydb
    - Returns the connection and cursor to sparkifydb
    """
    # connect to default database
    conn = psycopg2.connect("host=127.0.0.1 dbname=studentdb user=student password=student")
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    # create sparkify database with UTF8 encoding
    cur.execute("DROP DATABASE IF EXISTS sparkifydb")
    cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")
    # close connection to default database
    conn.close()
    # connect to sparkify database
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()
    return cur, conn


def main():
    cur, conn = create_database()
    conn.close()

if __name__ == "__main__":
    main()
