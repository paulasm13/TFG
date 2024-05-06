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
    churn_graph(cursor)

    print("Graphics created in '.png' files.")

    cursor.close()
    conn.close()


# Grafica de lineas por autor
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

# Churn rate graph
def churn_graph(cursor):
    cursor.execute(f"SELECT file_name, code FROM {TABLE} WHERE longevity='NULL'")

    files = []
    tuples = cursor.fetchall()

    for atribute in tuples:
        files.append(atribute[0])

    conteo = Counter(files)
    tuples_counter = tuple(conteo.items())

    # Lista de archivos
    files_list = [item[0] for item in tuples_counter]

    len_del_lines = {value: 0 for value in files_list}

    for atribute in tuples:
        if atribute[0] in files_list:
            len_del_lines[atribute[0]] += 1

    cursor.execute(f"SELECT file_name, code FROM {TABLE}")

    tuples = cursor.fetchall()

    total_len_lines = {value: 0 for value in files_list}

    for atribute in tuples:
        if atribute[0] in files_list:
            total_len_lines[atribute[0]] += 1

    churn_rate = {value: 0 for value in files_list}

    for atribute in tuples:
        if atribute[0] in files_list:
            churn_rate[atribute[0]] = len_del_lines[atribute[0]] / total_len_lines[atribute[0]] * 100

    plt.figure(figsize=(11, 5))
    for item, value  in churn_rate.items():
        # Fallo GitHub duda!
        if item != 'GitHub  ':
            plt.stem(item, value, linefmt='green')
    plt.xlabel('Archivos')
    plt.ylabel('Tasa de Churn [%]')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('ChurnRate_graph.png')
 

if __name__ == "__main__":
    get_graphs()

