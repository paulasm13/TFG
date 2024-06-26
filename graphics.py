import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE_1 = 'Repositories'
TABLE_2 = 'Files'
TABLE_3 = 'Code'


def get_graphs():
    # BBDD connection
    connection_string = f'mssql+pyodbc://{SERVER}/{DATABASE}?trusted_connection=yes&driver=SQL+Server'

    try:
        engine = create_engine(connection_string)
        conn = engine.connect()
        print(f"Successful connection to database {DATABASE}.")
    except Exception as ex:
        print(f"Failed connection to database {DATABASE}: {str(ex)}")

    commits_graph(conn)
    languages_graph(conn)
    collaborators_graph(conn)
    churn_rate_graph(conn)
    remaining_lines_graph(conn)
    remaining_lines_percentage_graph(conn)
    author_lines_graph(conn)
    author_lines_percentage_graph(conn)

    print("Graphics created in '.png' files.")

    conn.close()

def commits_graph(conn):
    # Consulta SQL simplificada
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        COUNT(c.Code_ID) AS Commits
    FROM {TABLE_1} AS r
    JOIN {TABLE_2} AS f ON r.ID = f.Repo_ID
    JOIN {TABLE_3} AS c ON f.File_ID = c.File_ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    ORDER BY r.Repo_Name, YEAR(c.Date_Start)
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Crear el histograma
    plt.figure(figsize=(12, 8))
    for repo_name in df['Repo_Name'].unique():
        repo_data = df[df['Repo_Name'] == repo_name]
        plt.bar(repo_data['Year'], repo_data['Commits'], label=repo_name, alpha=0.7)

    plt.xlabel('Year')
    plt.ylabel('Number of Commits')
    plt.title('Number of Commits per Repository per Year')
    plt.legend()
    plt.show()


def languages_graph(conn):
    # Consulta SQL
    query = f'''
    SELECT 
        r.Repo_Name,
        f.File_Language,
        COUNT(f.File_ID) AS File_Count
    FROM {TABLE_1} AS r
    JOIN {TABLE_2} AS f ON r.ID = f.Repo_ID
    GROUP BY r.Repo_Name, f.File_Language
    ORDER BY r.Repo_Name, f.File_Language
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Crear una tabla dinámica para la gráfica de barras apiladas
    pivot_df = df.pivot(index='Repo_Name', columns='File_Language', values='File_Count').fillna(0)
    
    # Normalizar los datos para obtener los porcentajes
    pivot_df_percent = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

    # Crear la gráfica de barras apiladas
    pivot_df_percent.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20')

    plt.xlabel('Repository')
    plt.ylabel('Percentage')
    plt.title('Percentage of Languages per Repository')
    plt.legend(title='Language', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def collaborators_graph(conn):
    # Consulta SQL
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        COUNT(DISTINCT c.Author_Start) AS Collaborators_Count
    FROM {TABLE_1} AS r
    JOIN {TABLE_2} AS f ON r.ID = f.Repo_ID
    JOIN {TABLE_3} AS c ON f.File_ID = c.File_ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    ORDER BY r.Repo_Name, YEAR(c.Date_Start)
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Crear la gráfica de evolución temporal
    plt.figure(figsize=(12, 8))

    for repo_name, data in df.groupby('Repo_Name'):
        plt.plot(data['Year'], data['Collaborators_Count'], marker='o', linestyle='-', label=repo_name)

    plt.xlabel('Year')
    plt.ylabel('Number of Collaborators')
    plt.title('Number of Collaborators Over Time')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def churn_rate_graph(conn):
    # Consulta SQL
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        SUM(CASE WHEN c.Comment_Boolean = 0 AND c.Longevity IS NOT NULL THEN 1 ELSE 0 END) AS Lines_Deleted,
        SUM(1) AS Total_Lines
    FROM {TABLE_1} AS r
    JOIN {TABLE_2} AS f ON r.ID = f.Repo_ID
    JOIN {TABLE_3} AS c ON f.File_ID = c.File_ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    ORDER BY r.Repo_Name, YEAR(c.Date_Start)
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Calcular la tasa de churn
    df['Churn_Rate'] = df['Lines_Deleted'] / df['Total_Lines']
    
    # Crear la gráfica de evolución de la tasa de churn
    plt.figure(figsize=(12, 8))

    for repo_name, data in df.groupby('Repo_Name'):
        plt.plot(data['Year'], data['Churn_Rate'], marker='o', linestyle='-', label=repo_name)

    plt.xlabel('Year')
    plt.ylabel('Churn Rate')
    plt.title('Churn Rate Evolution Over Time')
    plt.legend(title='Repositories', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def remaining_lines_graph(conn):
    # Consulta SQL
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        COUNT(*) AS Remaining_Lines_Count
    FROM {TABLE_3} AS c
    LEFT JOIN {TABLE_2} AS f ON c.File_ID = f.File_ID
    LEFT JOIN {TABLE_1} AS r ON f.Repo_ID = r.ID
    WHERE c.Longevity = 'NULL' AND C.Comment_Boolean = '0'
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    ORDER BY Year
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Convertir el año a tipo int para asegurar su correcta visualización
    df['Year'] = df['Year'].astype(int)

    # Crear la gráfica de evolución del número de líneas con longevidad 0 respecto al tiempo
    plt.figure(figsize=(12, 8))

    # Iterar sobre cada repositorio único en el DataFrame y graficar
    for repo_name, data in df.groupby('Repo_Name'):
        plt.plot(data['Year'], data['Remaining_Lines_Count'], marker='o', linestyle='-', label=repo_name)

    plt.xlabel('Year')
    plt.ylabel('Remaining Lines Count')
    plt.title('Evolution of Remaining Lines Over Time')
    plt.legend(title='Repositories', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def remaining_lines_percentage_graph(conn):
    # Consulta SQL
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        COUNT(*) AS Total_Lines_Count,
        SUM(CASE WHEN c.Longevity = 'NULL' AND c.Comment_Boolean = '0' THEN 1 ELSE 0 END) AS Remaining_Lines_Count
    FROM {TABLE_3} AS c
    LEFT JOIN {TABLE_2} AS f ON c.File_ID = f.File_ID
    LEFT JOIN {TABLE_1} AS r ON f.Repo_ID = r.ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    ORDER BY Year
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Convertir el año a tipo int para asegurar su correcta visualización
    df['Year'] = df['Year'].astype(int)

    # Calcular el porcentaje de líneas restantes
    df['Remaining_Lines_Percentage'] = (df['Remaining_Lines_Count'] / df['Total_Lines_Count']) * 100

    # Crear la gráfica de evolución del porcentaje de líneas restantes respecto al tiempo
    plt.figure(figsize=(12, 8))

    # Iterar sobre cada repositorio único en el DataFrame y graficar
    for repo_name, data in df.groupby('Repo_Name'):
        plt.plot(data['Year'], data['Remaining_Lines_Percentage'], marker='o', linestyle='-', label=repo_name)

    plt.xlabel('Year')
    plt.ylabel('Remaining Lines Percentage')
    plt.title('Evolution of Remaining Lines Percentage Over Time')
    plt.legend(title='Repositories', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def author_lines_graph(conn):
    # Consulta SQL para obtener la actividad de cada autor en cada repositorio
    query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        c.Author_Start AS Author,
        COUNT(*) AS Lines_Count
    FROM {TABLE_3} AS c
    LEFT JOIN {TABLE_2} AS f ON c.File_ID = f.File_ID
    LEFT JOIN {TABLE_1} AS r ON f.Repo_ID = r.ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start), c.Author_Start
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    df = pd.read_sql_query(query, conn)

    # Convertir el año a tipo int para asegurar su correcta visualización
    df['Year'] = df['Year'].astype(int)

    # Crear una gráfica para cada repositorio
    for repo_name, repo_data in df.groupby('Repo_Name'):
        plt.figure(figsize=(10, 6))
        
        # Iterar sobre cada autor único en el DataFrame y graficar
        for author, data in repo_data.groupby('Author'):
            plt.plot(data['Year'], data['Lines_Count'], marker='o', linestyle='-', label=author)
        
        plt.title(f'Author Activity Over Years in {repo_name}')
        plt.xlabel('Year')
        plt.ylabel('Lines Count')
        plt.legend(title='Authors', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def author_lines_percentage_graph(conn):
    # Consulta SQL para obtener el número total de líneas en cada repositorio para cada año
    total_lines_query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        COUNT(*) AS Total_Lines
    FROM {TABLE_3} AS c
    LEFT JOIN {TABLE_2} AS f ON c.File_ID = f.File_ID
    LEFT JOIN {TABLE_1} AS r ON f.Repo_ID = r.ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start)
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    total_lines_df = pd.read_sql_query(total_lines_query, conn)

    # Consulta SQL para obtener el número de líneas por autor en cada repositorio para cada año
    author_lines_query = f'''
    SELECT 
        r.Repo_Name,
        YEAR(c.Date_Start) AS Year,
        c.Author_Start AS Author,
        COUNT(*) AS Author_Lines
    FROM {TABLE_3} AS c
    LEFT JOIN {TABLE_2} AS f ON c.File_ID = f.File_ID
    LEFT JOIN {TABLE_1} AS r ON f.Repo_ID = r.ID
    GROUP BY r.Repo_Name, YEAR(c.Date_Start), c.Author_Start
    '''

    # Ejecutar la consulta y cargar los datos en un DataFrame de pandas
    author_lines_df = pd.read_sql_query(author_lines_query, conn)

    # Fusionar los datos de líneas totales y líneas por autor
    merged_df = pd.merge(author_lines_df, total_lines_df, on=['Repo_Name', 'Year'])

    # Calcular el porcentaje de líneas por autor respecto al número total de líneas del repositorio para cada año
    merged_df['Lines_Percentage'] = (merged_df['Author_Lines'] / merged_df['Total_Lines']) * 100

    # Crear una gráfica para cada repositorio
    for repo_name, repo_data in merged_df.groupby('Repo_Name'):
        plt.figure(figsize=(10, 6))
        
        # Iterar sobre cada autor único en el DataFrame y graficar
        for author, data in repo_data.groupby('Author'):
            plt.plot(data['Year'], data['Lines_Percentage'], marker='o', linestyle='-', label=author)
        
        plt.title(f'Author Lines Percentage Over Years in {repo_name}')
        plt.xlabel('Year')
        plt.ylabel('Lines Percentage')
        plt.legend(title='Authors', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    get_graphs()

