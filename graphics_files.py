import pyodbc
import matplotlib.pyplot as plt
from collections import Counter


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Files'


def get_graphs():
    # BBDD connection
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {DATABASE}.")
    except Exception as ex:
        print(f"Failed connection to database {DATABASE}: {str(ex)}")

    cursor = conn.cursor()

    language_graph(cursor)
    commits_graph(cursor)

    print("Graphics created in '.png' files.")

    cursor.close()
    conn.close()


def language_graph(cursor):
    cursor.execute(f'SELECT Language FROM {TABLE}')

    languages = []
    tuples_counter = []
    for row in cursor:
        languages.append(row.Language)

    conteo = Counter(languages)
    tuples_counter = tuple(conteo.items())

    label = [item[0] for item in tuples_counter]
    value = [item[1] for item in tuples_counter]


    plt.figure(figsize=(10, 6))
    pie_result = plt.pie(value, labels=label, autopct="%0.1f %%", shadow = True)

    for item in pie_result[1]:
        item.set_fontsize(12)

    for percentage in pie_result[2]:
        percentage.set_fontsize(12)

    plt.axis('equal') 
    plt.savefig('Language_graph.png')


def commits_graph(cursor):
    cursor.execute(f'SELECT Name, Commits FROM {TABLE}')

    tuples = cursor.fetchall()

    plt.figure(figsize=(11, 5))
    for atribute in tuples:
        plt.bar(str(atribute[0]), str(atribute[1]), color='skyblue')
    #plt.title('Cantidad de commits por archivo')
    plt.xlabel('Archivo')
    plt.ylabel('Número de commits')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('Commits_graph.png')
    #plt.show()    


if __name__ == "__main__":
    get_graphs()

