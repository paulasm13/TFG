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
    churn_rate_graph(conn)
    alive_lines_graph(conn)
    alive_lines_percentage_graph(conn)
    author_lines_graph(conn)
    author_lines_percentage_graph(conn)

    print("Graphics created in '.png' files.")

    conn.close()


def commits_graph(conn):
    query = f"""
    SELECT 
        t1.Repo_Name,
        YEAR(t3.Date_Start) AS Year,
        COUNT(t2.Commits) AS Commits
    FROM 
        {TABLE_1} t1
    JOIN 
        {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    JOIN 
        {TABLE_3} t3 ON t2.File_ID = t3.File_ID
    GROUP BY 
        t1.Repo_Name, YEAR(t3.Date_Start)
    ORDER BY 
        t1.Repo_Name, Year;
    """
    
    # Data to DataFrame
    data = pd.read_sql(query, conn)
    
    plt.figure(figsize=(12, 6))

    for repo in data['Repo_Name'].unique():
        repo_data = data[data['Repo_Name'] == repo]
        plt.plot(repo_data['Year'], repo_data['Commits'], label=repo)

    plt.xlabel('Año')
    plt.ylabel('Nº de commits')
    plt.title('Evolución del nº de commits')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.show()


def languages_graph(conn):
    query = f'''
    SELECT 
        t1.ID AS Repo_ID,
        t1.Repo_Name,
        t2.File_Language,
        COUNT(*) AS File_Count
    FROM 
        {TABLE_1} t1
    JOIN 
        {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    GROUP BY 
        t1.ID, t1.Repo_Name, t2.File_Language
    ORDER BY 
        t1.Repo_Name, t2.File_Language;
    '''

    # Data in a DataFrame
    df = pd.read_sql(query, conn)

    df['Total_Files'] = df.groupby('Repo_ID')['File_Count'].transform('sum')
    df['Percentage'] = (df['File_Count'] / df['Total_Files']) * 100

    # For each repository
    repos = df['Repo_Name'].unique()

    for repo in repos:
        repo_df = df[df['Repo_Name'] == repo]
        plt.figure(figsize=(10, 6))
        sns.barplot(data=repo_df, x='File_Language', y='Percentage')
        plt.title(f'Presencia de lenguajes de programación en el repositorio: {repo}')
        plt.xlabel('Lenguaje de programación')
        plt.ylabel('Porcentaje (%)')
        plt.xticks(rotation=45)
        plt.show()


def collaborators_graph(conn):
    query = f'''
    SELECT 
        t1.Repo_Name, 
        t3.Date_Start, 
        COUNT(DISTINCT t3.Author_Start) AS Collaborators
    FROM 
        {TABLE_3} t3
    JOIN 
        {TABLE_2} t2 ON t3.File_ID = t2.File_ID
    JOIN 
        {TABLE_1} t1 ON t2.Repo_ID = t1.ID
    GROUP BY 
        t1.Repo_Name, 
        t3.Date_Start
    ORDER BY 
        t3.Date_Start;
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
    plt.legend(title='Rpositorios')
    plt.grid(True)
    plt.show()


def churn_rate_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, t3.File_Name, t3.Date_Start, t3.Longevity, t3.Code
    FROM {TABLE_1} t1
    JOIN {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    JOIN {TABLE_3} t3 ON t2.File_ID = t3.File_ID
    """
    
    # Data in DataFrame
    df = pd.read_sql_query(query, conn)
    
    #  Date_Start to datetime
    df['Date_Start'] = pd.to_datetime(df['Date_Start'])
    
    df['Year'] = df['Date_Start'].dt.year

    df_deleted = df[df['Longevity'].notnull()]
    df_total = df
    
    deleted_lines_per_year = df_deleted.groupby(['Repo_Name', 'Year']).size().unstack(fill_value=0)
    
    total_lines_per_year = df_total.groupby(['Repo_Name', 'Year']).size().unstack(fill_value=0)
    
    churn_rate_per_year = (deleted_lines_per_year / total_lines_per_year) * 100
    
    plt.figure(figsize=(10, 6))
    for repo in churn_rate_per_year.index:
        plt.plot(churn_rate_per_year.columns, churn_rate_per_year.loc[repo], label=repo)
    
    plt.xlabel('Año')
    plt.ylabel('Tasa de Churn')
    plt.title('Evolución de la Tasa de Churn')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.show()


def alive_lines_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, t3.File_Name, t3.Date_Start, t3.Longevity, t3.Code
    FROM {TABLE_1} t1
    JOIN {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    JOIN {TABLE_3} t3 ON t2.File_ID = t3.File_ID
    """
    
    # Data in DataFrame
    df = pd.read_sql_query(query, conn)
    
    df['Date_Start'] = pd.to_datetime(df['Date_Start'])
    
    df['Year'] = df['Date_Start'].dt.year
    
    df_alive = df[df['Longevity'].isnull()]
    
    alive_lines_per_year = df_alive.groupby(['Repo_Name', 'Year']).size().unstack(fill_value=0).cumsum(axis=1)
    
    plt.figure(figsize=(10, 6))
    for repo in alive_lines_per_year.index:
        plt.plot(alive_lines_per_year.columns, alive_lines_per_year.loc[repo], label=repo)
    
    plt.xlabel('Año')
    plt.ylabel('Nº de líneas permanentes')
    plt.title('Evolución de líneas permanentes en valores absolutos')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.show()


def alive_lines_percentage_graph(conn):
    query = f"""
    SELECT t1.Repo_Name, t3.File_Name, t3.Date_Start, t3.Longevity, t3.Code
    FROM {TABLE_1} t1
    JOIN {TABLE_2} t2 ON t1.ID = t2.Repo_ID
    JOIN {TABLE_3} t3 ON t2.File_ID = t3.File_ID
    """
        
    # Data in DataFrame
    df = pd.read_sql_query(query, conn)
    
    #  Date_Start to datetime
    df['Date_Start'] = pd.to_datetime(df['Date_Start'])
    
    df['Year'] = df['Date_Start'].dt.year
    
    df_alive = df[df['Longevity'].isnull()]
    df_total = df
    
    alive_lines_per_year = df_alive.groupby(['Repo_Name', 'Year']).size().unstack(fill_value=0)
    
    total_lines_per_year = df_total.groupby(['Repo_Name', 'Year']).size().unstack(fill_value=0)
    
    alive_lines_per_year_percentage = (alive_lines_per_year / total_lines_per_year) * 100

    plt.figure(figsize=(10, 6))
    for repo in alive_lines_per_year_percentage.index:
        plt.plot(alive_lines_per_year_percentage.columns, alive_lines_per_year_percentage.loc[repo], label=repo)
    
    plt.xlabel('Año')
    plt.ylabel('Porcentaje de líneas permanentes (%)')
    plt.title('Evolución de líneas permanentes en valores relativos')
    plt.legend(title='Repositorios')
    plt.grid(True)
    plt.show()


def author_lines_graph(conn):
    query = f"""
    WITH Lines_Per_Author AS (
        SELECT 
            T1.Repo_Name,
            T3.Author_Start,
            YEAR(T3.Date_Start) AS Year,
            COUNT(*) AS Lines_Developed
        FROM 
            {TABLE_1} T1
        JOIN 
            {TABLE_2} T2 ON T1.ID = T2.Repo_ID
        JOIN 
            {TABLE_3} T3 ON T2.File_ID = T3.File_ID
        GROUP BY 
            T1.Repo_Name, T3.Author_Start, YEAR(T3.Date_Start)
    )
    SELECT * FROM Lines_Per_Author;
    """
    df = pd.read_sql(query, conn)
    
    df_grouped = df.groupby(['Repo_Name', 'Year', 'Author_Start']).agg({'Lines_Developed': 'sum'}).reset_index()
    
    # Repositories list
    repos = df_grouped['Repo_Name'].unique()
    
    for repo in repos:
        df_repo = df_grouped[df_grouped['Repo_Name'] == repo]
        authors = df_repo['Author_Start'].unique()
        
        plt.figure(figsize=(10, 6))
        
        for author in authors:
            df_author = df_repo[df_repo['Author_Start'] == author]
            plt.plot(df_author['Year'], df_author['Lines_Developed'], label=author)
        
        plt.xlabel('Año')
        plt.ylabel('Nº de líneas contribuidas')
        plt.title(f'Evolución de la actividad de cada colaborador del repositorio {repo} en valores absolutos')
        plt.legend()
        plt.grid(True)
        plt.show()
    


def author_lines_percentage_graph(conn):
    query = f"""
    WITH Lines_Per_Author AS (
        SELECT 
            T1.Repo_Name,
            T3.Author_Start,
            YEAR(T3.Date_Start) AS Year,
            COUNT(*) AS Lines_Developed
        FROM 
            {TABLE_1} T1
        JOIN 
            {TABLE_2} T2 ON T1.ID = T2.Repo_ID
        JOIN 
            {TABLE_3} T3 ON T2.File_ID = T3.File_ID
        GROUP BY 
            T1.Repo_Name, T3.Author_Start, YEAR(T3.Date_Start)
    )
    SELECT * FROM Lines_Per_Author;
    """

    df = pd.read_sql(query, conn)
    
    df_grouped = df.groupby(['Repo_Name', 'Year', 'Author_Start']).agg({'Lines_Developed': 'sum'}).reset_index()

    total_lines_by_author = df_grouped.groupby(['Repo_Name', 'Author_Start'])['Lines_Developed'].transform('sum')
    df_grouped['Relative_Contribution'] = df_grouped['Lines_Developed'] / total_lines_by_author * 100
    
    # Repositories list
    repos = df_grouped['Repo_Name'].unique()
    
    for repo in repos:
        df_repo = df_grouped[df_grouped['Repo_Name'] == repo]
        authors = df_repo['Author_Start'].unique()
        
        plt.figure(figsize=(10, 6))
        
        for author in authors:
            df_author = df_repo[df_repo['Author_Start'] == author]
            plt.plot(df_author['Year'], df_author['Relative_Contribution'], label=author)
        
        plt.xlabel('Año')
        plt.ylabel('Porcentaje de líneas contribuidas (%)')
        plt.title(f'Evolución de la actividad de cada colaborador del repositorio {repo} en valores relativos')
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    get_graphs()

