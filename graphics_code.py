import pyodbc
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
from collections import defaultdict


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
    author2_graph(cursor)
    churn_graph(cursor)
    analysis_graph(cursor)

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

    author_list = [item[0] for item in tuples_counter]

    len_lines = {value: 0 for value in author_list}

    plt.figure(figsize=(11, 5))
    for atribute in tuples:
        if atribute[0] in author_list:
            len_lines[atribute[0]] += 1

    for item, value  in len_lines.items():
        if item != 'GitHub  ':
            plt.bar(item, value, color='green')

    plt.grid(axis='y', linestyle='--')
    plt.xlabel('Autor')
    plt.ylabel('Líneas que permanecen en la actualidad')
    plt.savefig('CurrentLines_graph.png')

def author2_graph(cursor):
    cursor.execute(f"SELECT author_start, code FROM {TABLE}")

    author_total = []
    tuples_total = cursor.fetchall()

    for atribute in tuples_total:
        author_total.append(atribute[0])

    conteo = Counter(author_total)
    tuples_counter = tuple(conteo.items())

    author_total_list = [item[0] for item in tuples_counter]

    len_lines_total = {value: 0 for value in author_total_list}

    for atribute in tuples_total:
        if atribute[0] in author_total_list:
            len_lines_total[atribute[0]] += 1
    
    for item, value  in len_lines_total.items():
        if item != 'GitHub  ':
            plt.bar(item, value, color='purple')

    plt.grid(axis='y', linestyle='--')
    plt.xlabel('Autor')
    plt.ylabel('Líneas totales contribuidas')
    plt.savefig('CurrentLines2_graph.png')


def churn_graph(cursor):
    cursor.execute(f"SELECT file_name, code FROM {TABLE} WHERE longevity='NULL'")

    files = []
    tuples = cursor.fetchall()

    for atribute in tuples:
        files.append(atribute[0])

    conteo = Counter(files)
    tuples_counter = tuple(conteo.items())

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
        if item != 'GitHub  ':
            plt.stem(item, value, linefmt='green')
    plt.xlabel('Archivos')
    plt.ylabel('Tasa de Churn [%]')
    plt.grid(axis='y', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('ChurnRate_graph.png')


def analysis_graph(cursor):
    cursor.execute(f"SELECT date_start, author_start FROM {TABLE}")
    
    date = []
    authors = []

    for row in cursor:
        date.append(row.date_start)
        authors.append(row.author_start)
    
    authors = set(authors)
    authors.remove('GitHub  ')

    date.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

    # Year of creation of the project
    year = datetime.strptime(date[0], '%Y-%m-%d').year
    
    lines_per_author_per_year = defaultdict(lambda: defaultdict(int))

    # Initialise dictionary with values at 0
    for y in range(year, year + 5):
        for author in authors: 
            lines_per_author_per_year[y][author] = 0

    for y in range(year, year + 5):
        cursor.execute(f"SELECT author_start, code FROM {TABLE} WHERE YEAR(date_start) = {y}")
        for row in cursor:
            author_start, code = row
            code_lines = code.strip().split('\n')
            lines_per_author_per_year[y][author_start] += len(code_lines)

    plt.figure(figsize=(14, 8))
    for year, inner_dict in lines_per_author_per_year.items():
        years = list(lines_per_author_per_year.keys())
        #print(f"YEARS_LIST: {years}")
        for author, lines_per_year in inner_dict.items():
            authors = list(inner_dict.keys())
            #print(f"AUTHORS_LIST: {authors}")
            #print(f"Year: {year}")
            #print(f"Author: {author}")
            authors = list(inner_dict.keys())
            #print(f"Number of lines: {lines_per_year}")
            plt.bar(year, lines_per_year, label=author)  

    plt.xlabel('Año')
    plt.ylabel('Número de líneas contribuidas')
    plt.legend(title='Autores')  
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.savefig('First5YearsEvolution_graph.png')


if __name__ == "__main__":
    get_graphs()

