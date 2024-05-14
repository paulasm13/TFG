"""

ARCHIVO PARA ANALIZAR UN REPOSITORIO

- Clona un repositorio 
- Analiza su contenido
- Lista el contenido del repositorio
- Crea una BBDD 'Analysis_Github_Repository'
- Crea la tabla 'Repositories' con los repositorios analizados
- Crea la tabla 'Files' con los ficheros de cada repositorio

"""

import os
import sys
import requests
import subprocess
import pyodbc
import git_blameall
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound


# Global variables
SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'master'
NEW_DATABASE = 'Analysis_Github_Repository'
TABLE_1 = 'Repositories'
TABLE_2 = 'Files'


def menu():
    if type_option == 'repo-url':
        request_url()
    else:
        sys.exit("Usage: python3 init.py repo-url <name_urlclone>")


def request_url():
    """ Request url by shell. """
    values = option.split("/")
    try:
        protocol = values[0].split(':')[0]
        type_git = values[2]
        user = values[3]
        repo = values[4][0:-4]
    except:
        sys.exit('ERROR --> Usage: http://TYPEGIT/USER/NAMEREPO.git')
    # Check url
    check_url(protocol, type_git)
    # Clone repo
    run_url(protocol, type_git, user, repo)


def check_url(protocol, type_git):
    """ Check url sintax. """
    if protocol != 'https':
        sys.exit('Usage: https protocol')
    elif type_git != 'github.com':
        sys.exit('Usage: github.com')

    
def run_url(protocol, type_git, user, repo):
    # Create the url of the api
    repo_url = (protocol + "://" + type_git + "/" + user + "/" +
                repo + ".git")
    print("Analyzing repository...\n")
    # Get content
    r = requests.get(repo_url)
    """ Run url. """
    command_line = "git clone " + repo_url
    print('Run url...')
    # Run in the shell the command_line
    subprocess.call(command_line)
    get_directory(repo_url)


def get_directory(repo_url):
    """ Get the name of the downloaded repository directory. """
    # Get values from the url
    values = repo_url.split('/')
    # Last item in the list
    name_directory = values[-1]
    # Remove extension .git
    if '.git' in str(name_directory):
        name_directory = name_directory[0:-4]
    print("The directory is: " + name_directory)
    insert_repo_data(name_directory)
    get_bd2()
    get_path(name_directory)


def get_path(name_directory):
    """ Get the path to the directory. """
    absFilePath = os.path.abspath(name_directory)
    # Check if the last element is a file
    fichero = absFilePath.split('/')[-1]
    if fichero.endswith('.'):
        absFilePath = absFilePath.replace("\\" + fichero, "")
    print("This script absolute path is ", absFilePath)
    read_directory(absFilePath, name_directory)


def read_directory(absFilePath, name_directory):
    """ Extract the files from the directory. """
    pos = ''
    print('Directory: ')
    path = absFilePath
    print(path)
    try:
        # Get a list of files and subdirectories in the specified directory
        directory = os.listdir(path)
        print(directory)
        # File...
        for i in range(0, len(directory)):
            if '.' in directory[i] and not directory[i].startswith('.'):   
                print('Python File: ' + str(directory[i]))
                name_file = str(directory[i])
                pos = path + "\\" + directory[i]
                # GET ALL REVISIONS
                os.chdir(path)
                cmd = f'git log --follow -- {name_file}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                revisions = result.stdout.split('\n')
                commits_list = [atributo for atributo in revisions if 'commit' in atributo]
                commits = int(len(commits_list))
                print('insert_files_data!!!!')
                insert_files_data(name_file, pos, commits)
                if commits != 0: 
                    print('BLAMEALL------')
                    git_blameall.main(name_file)
                try:
                    with open(pos, 'rb') as file:
                        lexer = guess_lexer_for_filename(name_file, file.read())
                        language = lexer.name                
                except FileNotFoundError:
                    print(f"File {name_file} could not be opened.")
                except ClassNotFound:
                    print(f"The language for {name_file} could not be determined. Maybe it is a binary or data file.")
                    language = 'Archivo de datos'
                insert_files_language(language)
                print('INSERT_FILES_LANGUAGE......')
            # Subdirectory...
            elif '.' not in directory[i]:
                print('\nOpening another directory...\n')
                path2 = absFilePath + '\\' + directory[i]
                try:
                    read_directory(path2, directory[i])
                except NotADirectoryError:
                    pass
    except FileNotFoundError:
        print(os.listdir(path))
        pass
    

def get_bd1():
    # Connection to MASTER DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

    try:
        connection = pyodbc.connect(connectionString, autocommit=True)
        print("Successful connection to database MASTER")
    except Exception as ex:
        print(f"Failed connection to database MASTER: {str(ex)}")

    # New database
    cursor = connection.cursor()
    try:
        cursor.execute(f'CREATE DATABASE {NEW_DATABASE}')
        print(f"The {NEW_DATABASE} database has been successfully created.")
    except Exception as ex:
        print(f"Failed to create database {NEW_DATABASE}: {str(ex)}")

    # Close connection to MASTER DATABASE
    connection.close()

    # Connection to 'Analysis_Github_Repository' DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {NEW_DATABASE}")
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")

    cursor_bd = conn.cursor()

    create_repo_table_query = f'''
    CREATE TABLE {TABLE_1} (
        ID INT PRIMARY KEY,
        Repo_Name VARCHAR(MAX) NOT NULL,
    )
    '''

    cursor_bd.execute(create_repo_table_query)
    conn.commit()
    conn.close()


def get_bd2():
    # Connection to 'Analysis_Github_Repository' DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {NEW_DATABASE}")
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")

    cursor_bd = conn.cursor()

    create_files_table_query = f'''
    CREATE TABLE {TABLE_2} (
        File_ID INT PRIMARY KEY,
        Repo_ID INT,
        File_Name VARCHAR(MAX) NOT NULL,
        File_Path VARCHAR(MAX) NOT NULL,
        File_Language VARCHAR(50),
        Commits INT,
        FOREIGN KEY (Repo_ID) REFERENCES {TABLE_1}(ID),
    )
    '''

    print ("FILES_DATABASE CREADAAAAA")
    try:
        cursor_bd.execute(create_files_table_query)
    except Exception as ex:
        print(f"Failed : {str(ex)}")
    conn.commit()
    conn.close()


def insert_repo_data(name_directory):
    # Connection to 'Analysis_Github_Repository' DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {NEW_DATABASE}")
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")

    cursor_bd = conn.cursor()
    
     # ID PRIMARY KEY
    try:
        cursor_bd.execute(f"SELECT MAX(ID) FROM {TABLE_1}")
        last_id = cursor_bd.fetchone()[0]

        if last_id is None:
            last_id = 0

        new_id = last_id + 1

    except Exception as e:
        print("Error when incrementing the ID:", e)
        return None

    insert_query = f"INSERT INTO {TABLE_1} (ID, Repo_Name) VALUES (?, ?)"
    data_to_insert = (new_id, name_directory)
    cursor_bd.execute(insert_query, data_to_insert)
    conn.commit()
    conn.close()


def insert_files_data(name_file, pos, commits):
    # Connection to 'Analysis_Github_Repository' DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {NEW_DATABASE}")
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")

    cursor_bd = conn.cursor()
    
     # ID PRIMARY KEY
    try:
        cursor_bd.execute(f"SELECT MAX(File_ID) FROM {TABLE_2}")
        last_id = cursor_bd.fetchone()[0]

        if last_id is None:
            last_id = 0

        new_id = last_id + 1

    except Exception as e:
        print("Error when incrementing the ID:", e)
        return None
    
    # ID FOREIGN KEY
    cursor_bd.execute(f"SELECT MAX(ID) FROM {TABLE_1}")
    repo_id = cursor_bd.fetchone()[0]
    print(f"repo_id.... {repo_id}")

    if repo_id is None:
        repo_id = 0


    insert_query = f"INSERT INTO {TABLE_2} (File_ID, Repo_ID, File_Name, File_Path, Commits) VALUES (?, ?, ?, ?, ?)"
    data_to_insert = (new_id, repo_id, name_file, pos, commits)
    cursor_bd.execute(insert_query, data_to_insert)
    conn.commit()
    conn.close()

def insert_files_language(language):
    # Connection to 'Analysis_Github_Repository' DATABASE 
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'

    try:
        conn = pyodbc.connect(connectionString)
        print(f"Successful connection to database {NEW_DATABASE}")
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")

    cursor_bd = conn.cursor()

    insert_query = f"INSERT INTO {TABLE_2} (File_Language) VALUES (?)"
    data_to_insert = (language)
    cursor_bd.execute(insert_query, data_to_insert)
    conn.commit()
    conn.close()
    

if __name__ == "__main__":
    try:
        type_option = sys.argv[1]
        option = sys.argv[2]
        get_bd1()
        menu()
    except:
        sys.exit("Usage: python3 init.py 'repo-url' <url_repo>")
