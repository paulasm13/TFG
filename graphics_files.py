import pyodbc
import matplotlib.pyplot as plt


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
    percentages = []
    for row in cursor:
        languages.append(row.Language)

    for atribute in languages:
        count_atr = languages.count(atribute)
        percentage_atr = (count_atr / len(languages)) * 100
        percentages.append(percentage_atr)

    plt.figure(figsize=(10, 6))
    plt.bar(languages, percentages, color='skyblue')
    plt.title('Lenguajes utilizados en el repositorio [%]')
    plt.xlabel('Lenguajes')
    plt.ylabel('%')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('Language_graph.png')


def commits_graph(cursor):
    cursor.execute(f'SELECT Name, Commits FROM {TABLE}')

    tuples = cursor.fetchall()

    plt.figure(figsize=(10, 6))
    for atribute in tuples:
        plt.bar(str(atribute[0]), str(atribute[1]), color='skyblue')
    plt.title('Número de commits por archivo')
    plt.xlabel('Archivos')
    plt.ylabel('Commits')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('Commits_graph.png')
    #plt.show()    


if __name__ == "__main__":
    get_graphs()

