import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    comments_graph(conn)
    comments_percentage_graph(conn)
    deleted_lines_graph(conn)            
    alive_lines_percentage_graph(conn) 
    author_activity_graph(conn)
    author_activity_percentage_graph(conn)

    print("Graphics created in '.png' files.")

    conn.close()


def commits_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, YEAR(t3.Date_Start) AS Year,
    COUNT(t2.Commits) AS Commits
    FROM {TABLE_1} t1
    JOIN {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    JOIN {TABLE_3} t3 ON t2.File_ID = t3.File_ID
    GROUP BY t1.Repo_Name, YEAR(t3.Date_Start)
    ORDER BY t1.Repo_Name, Year;
    """
    
    # DataFrame
    data = pd.read_sql(query, conn)
    
    plt.figure(figsize=(12, 6))

    for repo in data['Repo_Name'].unique():
        repo_data = data[data['Repo_Name'] == repo]
        plt.plot(repo_data['Year'], repo_data['Commits'], label=repo)

    plt.xlabel('Año')
    plt.ylabel('Nº de commits')
    plt.title('Evolución del nº de commits')
    plt.legend(title='Repositorios')
    plt.xticks(repo_data['Year'].unique())
    plt.grid(True)
    plt.show()


def languages_graph(conn):
    query = f'''
    SELECT t1.ID AS Repo_ID, t1.Repo_Name, t2.File_Language,
    COUNT(*) AS File_Count
    FROM {TABLE_1} t1
    JOIN {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    WHERE t2.File_Language != 'Archivo de datos'
    GROUP BY t1.ID, t1.Repo_Name, t2.File_Language
    ORDER BY t1.Repo_Name, t2.File_Language;
    '''

    # DataFrame
    df = pd.read_sql(query, conn)

    df['Total_Files'] = df.groupby('Repo_ID')['File_Count'].transform('sum')
    df['Percentage'] = (df['File_Count'] / df['Total_Files']) * 100

    repos = df['Repo_Name'].unique()

    for repo in repos:
        repo_df = df[df['Repo_Name'] == repo]
        plt.figure(figsize=(10, 6))
        sns.barplot(data=repo_df, x='File_Language', y='Percentage')
        plt.title(f'Presencia de lenguajes de programación en el repositorio: {repo}')
        plt.xlabel('Lenguaje de programación')
        plt.ylabel('Porcentaje (%)')
        plt.ylim(0, 100)
        plt.xticks(rotation=45)
        plt.show()


def collaborators_graph(conn):
    query = f'''
    SELECT t1.Repo_Name, t3.Date_Start, 
    COUNT(DISTINCT t3.Author_Start) AS Collaborators
    FROM {TABLE_3} t3
    JOIN {TABLE_2} t2 ON t3.File_ID = t2.File_ID
    JOIN {TABLE_1} t1 ON t2.Repo_ID = t1.ID
    GROUP BY t1.Repo_Name, t3.Date_Start
    ORDER BY t3.Date_Start;
    '''

    df = pd.read_sql_query(query, conn)

    df['Date_Start'] = pd.to_datetime(df['Date_Start'])

    df['Year'] = df['Date_Start'].dt.year

    df_grouped = df.groupby(['Repo_Name', 'Year'])['Collaborators'].sum().reset_index()

    pivot_df = df_grouped.pivot(index='Year', columns='Repo_Name', values='Collaborators')

    plt.figure(figsize=(10, 6))
    for column in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[column], marker='o', label=column)

    plt.xlabel('Año')
    plt.ylabel('Nº de colaboradores')
    plt.title('Evolución del nº de colaboradores')
    plt.legend(title='Repositorios')
    plt.xticks(pivot_df.index.unique())
    plt.grid(True)
    plt.show()


def comments_graph(conn):
    query = f'''
    SELECT T1.Repo_Name, COUNT(T3.Code_ID) AS Num_Comments
    FROM {TABLE_1} T1
    JOIN {TABLE_2} T2 ON T1.ID = T2.Repo_ID
    JOIN {TABLE_3} T3 ON T2.File_ID = T3.File_ID
    WHERE T3.Comment_Boolean = 1 AND T3.Longevity = 'NULL'
    GROUP BY T1.Repo_Name
    ORDER BY T1.Repo_Name
    '''

    df = pd.read_sql(query, conn)

    plt.figure(figsize=(10, 6))
    plt.bar(df['Repo_Name'], df['Num_Comments'])
    plt.xlabel('Repositorio')
    plt.ylabel('Nº de líneas de comentario')
    plt.title('Comentarios por repositorio en valores absolutos')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


def comments_percentage_graph(conn):
    query = f'''
    SELECT T1.Repo_Name, SUM(CASE WHEN T3.Comment_Boolean = 1 AND T3.Longevity = 'NULL' THEN 1 ELSE 0 END) AS Num_Comments,
        COUNT(CASE WHEN T3.Longevity = 'NULL' THEN T3.Code_ID ELSE NULL END) AS Total_Lines
    FROM {TABLE_1} T1
    JOIN {TABLE_2} T2 ON T1.ID = T2.Repo_ID
    JOIN {TABLE_3} T3 ON T2.File_ID = T3.File_ID
    GROUP BY T1.Repo_Name
    ORDER BY T1.Repo_Name
    '''

    df = pd.read_sql(query, conn)

    df['Percentage_Comments'] = (df['Num_Comments'] / df['Total_Lines']) * 100

    plt.figure(figsize=(10, 6))
    plt.bar(df['Repo_Name'], df['Percentage_Comments'])
    plt.xlabel('Repositorio')
    plt.ylabel('Porcentaje de líneas de comentario (%)')
    plt.title('Comentarios por repositorio en valores relativos')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylim(0, 100)
    plt.show()


def deleted_lines_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, YEAR(t3.Date_Start) AS Year,
           COUNT(CASE WHEN t3.Longevity = 'NULL' THEN 1 END) AS Alive_Lines,
           COUNT(*) AS Total_Lines
    FROM {TABLE_3} t3
    JOIN {TABLE_2} t2 ON t3.File_ID = t2.File_ID
    JOIN {TABLE_1} t1 ON t2.Repo_ID = t1.ID
    GROUP BY t1.Repo_Name, YEAR(t3.Date_Start)
    ORDER BY t1.Repo_Name, YEAR(t3.Date_Start);
    """
    
    # DataFrame
    df = pd.read_sql_query(query, conn)

    df['Deleted_Lines'] = (df['Total_Lines'] - df['Alive_Lines']) 

    plt.figure(figsize=(14, 8))

    repos = df['Repo_Name'].unique()

    for repo in repos:
        repo_data = df[df['Repo_Name'] == repo]
        plt.plot(repo_data['Year'], repo_data['Deleted_Lines'], marker='o', label=repo)
    
    plt.xlabel('Año')
    plt.ylabel('Nº de líneas eliminadas')
    plt.title('Evolución de líneas eliminadas a lo largo del tiempo')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.xticks(repo_data['Year'].unique())
    plt.show()

def alive_lines_percentage_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, YEAR(t3.Date_Start) AS Year,
           COUNT(CASE WHEN t3.Longevity = 'NULL' THEN 1 END) AS Alive_Lines,
           COUNT(*) AS Total_Lines
    FROM {TABLE_3} t3
    JOIN {TABLE_2} t2 ON t3.File_ID = t2.File_ID
    JOIN {TABLE_1} t1 ON t2.Repo_ID = t1.ID
    GROUP BY t1.Repo_Name, YEAR(t3.Date_Start)
    ORDER BY t1.Repo_Name, YEAR(t3.Date_Start);
    """
    
    # DataFrame
    df = pd.read_sql_query(query, conn)

    df['Alive_Lines_Percentage'] = (df['Alive_Lines'] / df['Total_Lines']) * 100

    plt.figure(figsize=(14, 8))

    repos = df['Repo_Name'].unique()

    for repo in repos:
        repo_data = df[df['Repo_Name'] == repo]
        plt.plot(repo_data['Year'], repo_data['Alive_Lines_Percentage'], marker='o', label=repo)
    
    plt.xlabel('Año')
    plt.ylabel('Porcentaje de líneas permanentes (%)')
    plt.title('Evolución de líneas permanentes a lo largo del tiempo')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.xticks(repo_data['Year'].unique())
    plt.show()


def author_activity_graph(conn):
    query_repo_name = f"""
    SELECT DISTINCT T1.Repo_Name
    FROM {TABLE_1} T1
    JOIN {TABLE_2} T2 ON T1.ID = T2.Repo_ID
    JOIN {TABLE_3} T3 ON T2.File_ID = T3.File_ID
    """
    
    query_lines_created = f"""
    SELECT T1.Repo_Name, YEAR(T3.Date_Start) AS Year, T3.Author_Start,
        COUNT(*) AS Lines_Created
    FROM {TABLE_1} T1
    JOIN {TABLE_2} T2 ON T1.ID = T2.Repo_ID
    JOIN {TABLE_3} T3 ON T2.File_ID = T3.File_ID
    WHERE T3.Author_Start != 'GitHub'
    GROUP BY T1.Repo_Name, YEAR(T3.Date_Start), T3.Author_Start
    ORDER BY T1.Repo_Name, Year, T3.Author_Start;
    """
    
    df_repo_name = pd.read_sql(query_repo_name, conn)
    df_lines_created = pd.read_sql(query_lines_created, conn)

    for repo_name in df_repo_name['Repo_Name'].unique():
        df_repo = df_lines_created[df_lines_created['Repo_Name'] == repo_name]
        
        plt.figure(figsize=(10, 6))
        
        authors = df_repo['Author_Start'].unique()
        
        for author in authors:
            author_data = df_repo[df_repo['Author_Start'] == author]
            plt.plot(author_data['Year'], author_data['Lines_Created'], marker='o', label=author)

    plt.xlabel('Año')
    plt.ylabel('Nº de líneas contribuidas')
    plt.title(f'Evolución de la actividad de cada colaborador del repositorio {repo_name} en valores absolutos')
    plt.legend(loc="upper right", frameon=False)
    plt.grid(True)
    plt.xticks(author_data['Year'].unique())
    plt.tight_layout()
    plt.show()
    

def author_activity_percentage_graph(conn):
    query_lines_created = f"""
    SELECT T1.Repo_Name, YEAR(T3.Date_Start) AS Year, T3.Author_Start,
        COUNT(*) AS Lines_Created
    FROM {TABLE_1} T1
    JOIN {TABLE_2} T2 ON T1.ID = T2.Repo_ID
    JOIN {TABLE_3} T3 ON T2.File_ID = T3.File_ID
    WHERE T3.Author_Start != 'GitHub'
    GROUP BY T1.Repo_Name, YEAR(T3.Date_Start), T3.Author_Start
    ORDER BY T1.Repo_Name, Year, T3.Author_Start;
    """
    
    df_lines_created = pd.read_sql(query_lines_created, conn)

    # Total lines per repository
    total_lines_by_repo_year = df_lines_created.groupby(['Repo_Name', 'Year'])['Lines_Created'].sum().reset_index()
    total_lines_by_repo_year.rename(columns={'Lines_Created': 'Total_Lines_Created'}, inplace=True)
    
    df_merged = pd.merge(df_lines_created, total_lines_by_repo_year, on=['Repo_Name', 'Year'])
    
    df_merged['Percentage_Lines_Created'] = (df_merged['Lines_Created'] / df_merged['Total_Lines_Created']) * 100
    
    for repo_name in df_merged['Repo_Name'].unique():
        df_repo = df_merged[df_merged['Repo_Name'] == repo_name]
        
        plt.figure(figsize=(10, 6))
        
        authors = df_repo['Author_Start'].unique()
        
        for author in authors:
            author_data = df_repo[df_repo['Author_Start'] == author]
            plt.plot(author_data['Year'], author_data['Percentage_Lines_Created'], marker='o', label=author)
        
        plt.xlabel('Año')
        plt.ylabel('Porcentaje de líneas contribuidas (%)')
        plt.title(f'Evolución de la actividad de cada colaborador del repositorio {repo_name} en valores relativos')
        plt.legend(loc="upper right", frameon=False)
        plt.grid(True)
        plt.xticks(author_data['Year'].unique())
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    get_graphs()
    

