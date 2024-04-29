import pyodbc
import matplotlib.pyplot as plt


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Code'


def get_graphs():
    # BBDD connection
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {DATABASE}.")
    except Exception as ex:
        print(f"Failed connection to database {DATABASE}: {str(ex)}")

    cursor = conn.cursor()

    author_graph(cursor)

    print("Graphics created in '.png' files.")

    cursor.close()
    conn.close()


def author_graph(cursor):
    cursor.execute(f'SELECT Author_beg FROM {TABLE}')

    author = []
    code = []
    for row in cursor:
        author.append(row.Author_beg)
    
    author = set(author)

    #cursor.execute(f'SELECT Code FROM {TABLE} WHERE {Author_beg} = (author[0])", )
    #for row in cursor:
    #    code.append(row.Code)

    #print(len(code))



if __name__ == "__main__":
    get_graphs()

