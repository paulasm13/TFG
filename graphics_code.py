import pyodbc
import matplotlib.pyplot as plt
from collections import Counter



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
    cursor.execute(f"SELECT author_start, code FROM {TABLE} WHERE longevity='NULL'")

    author = []
    tuples = cursor.fetchall()

    for atribute in tuples:
        author.append(atribute[0])

    conteo = Counter(author)
    tuples_counter = tuple(conteo.items())

    # Lista de autores [ana, greg, github]
    author_list = [item[0] for item in tuples_counter]

    len_lines = {value: 0 for value in author_list}


    plt.figure(figsize=(11, 5))
    for atribute in tuples:
        if atribute[0] in author_list:
            len_lines[atribute[0]] += 1

    print(len_lines)

    for item, value  in len_lines.items():
        # Fallo GitHub duda!
        if item != 'GitHub  ':
            plt.bar(item, value, color='skyblue')
    plt.xlabel('Autor')
    plt.ylabel('Líneas que permanecen en la actualidad')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('CurrentLines_graph.png')
    plt.show()  

if __name__ == "__main__":
    get_graphs()

