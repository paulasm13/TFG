"""

ARCHIVO PARA ANALIZAR UN REPOSITORIO

"""

import os
import sys
import subprocess
import pyodbc
import git_blameall
import chardet
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound

# Global variables
SERVER = 'LAPTOP-E26LIVT1\\SQLEXPRESS'
DATABASE = 'master'
NEW_DATABASE = 'NUEVO'
TABLE_1 = 'Repositories'
TABLE_2 = 'Files'
EXCLUDED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".exe", ".dll", ".ico", ".db", 
    ".dat", ".class", ".o", ".pyc", ".mp3", ".mp4", ".wav", ".avi", ".bak", 
    ".tmp", ".docx", ".pptx", ".zip", ".tar.gz", ".rar"]
EXCLUDED_DIRECTORIES = ["node_modules", "vendor", "Pods"]


def remove_excluded(repo_path):
    print('\n')    
    def is_excluded(file_path):
        # Check excluded files
        for ext in EXCLUDED_EXTENSIONS:
            if file_path.endswith(ext):
                return True
        # Check excluded directories
        for dir in EXCLUDED_DIRECTORIES:
            if dir in file_path.split(os.path.sep):
                return True
        return False

    files_removed = []
    directories_removed = []

    # Remove excluded files from the cloned repository
    for root, dirs, files in os.walk(repo_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if is_excluded(file_path):
                try:
                    os.remove(file_path)
                    files_removed.append(file_path)
                    print(f'File removed: {file_path}')
                except OSError as e:
                    print(f'Remove error file {file_path}: {e}')
        
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if dir in EXCLUDED_DIRECTORIES:
                try:
                    os.rmdir(dir_path)
                    directories_removed.append(dir_path)
                    print(f'Directory removed: {dir_path}')
                except OSError as e:
                    print(f'Remove error directory {dir_path}: {e}')

    print(f'Total files removed: {len(files_removed)}')
    print(f'Total directories removed: {len(directories_removed)}\n')


def remove_empty_files(repo_path):
    empty_files_removed = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Remove files size of 0 bytes
                if os.path.getsize(file_path) == 0:
                    os.remove(file_path)
                    empty_files_removed.append(file_path)
                    print(f'Empty file removed: {file_path}')
            except OSError as e:
                print(f'Remove error file {file_path}: {e}')
    print(f'Total empty files removed: {len(empty_files_removed)}\n')
        

def detect_encoding(name_file):
    try:
        with open(name_file, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for file {name_file}: {e}")


def convert_to_utf8(name_file, original_encoding):
    # Temporal file
    temp_file_path = name_file + '.tmp'
    try:
        with open(name_file, 'r', encoding=original_encoding, errors='replace') as f:
            content = f.read()
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(temp_file_path, name_file)
    except Exception as e:
        print(f"Error converting file {name_file} to UTF-8: {e}")


def menu():
    if len(sys.argv) != 3 or sys.argv[1] != 'repo-url':
        sys.exit("Usage: python3 init.py repo-url <name_urlclone>")
    option = sys.argv[2]
    request_url(option)


def request_url(option):
    values = option.split("/")
    try:
        protocol = values[0].split(':')[0]
        type_git = values[2]
        user = values[3]
        repo = values[4][0:-4]
    except IndexError:
        sys.exit('ERROR --> Usage: http://TYPEGIT/USER/NAMEREPO.git')
    check_url(protocol, type_git)
    run_url(protocol, type_git, user, repo)


def check_url(protocol, type_git):
    if protocol != 'https':
        sys.exit('Usage: https protocol')
    elif type_git != 'github.com':
        sys.exit('Usage: github.com')


def run_url(protocol, type_git, user, repo):
    repo_url = f"{protocol}://{type_git}/{user}/{repo}.git"
    print("Analyzing repository...\n")
    command_line = f"git clone {repo_url}"
    print('Run url...')
    result = subprocess.run(command_line, shell=True)
    if result.returncode != 0:
        print(f"Failed to clone repository {repo_url}")
        return
    # Extracting the directory name from the repo URL
    name_directory = repo
    print("\n")
    remove_empty_files(name_directory)
    remove_excluded(name_directory)
    get_directory(repo_url)


def get_directory(repo_url):
    values = repo_url.split('/')
    name_directory = values[-1]
    if '.git' in str(name_directory):
        name_directory = name_directory[0:-4]
    print("The directory is: " + name_directory)
    insert_repo_data(name_directory)
    get_table2()
    get_path(name_directory)


def get_path(name_directory):
    absFilePath = os.path.abspath(name_directory)
    print("This script absolute path is ", absFilePath)
    read_directory(absFilePath, name_directory)


def read_directory(absFilePath, name_directory):
    path = absFilePath
    print(f"Directory: {path}")
    try:
        directory_list = os.listdir(path)
        print(f"List of files and subdirectories: {directory_list}")
        # Discard '.git' directory for analysis
        if '.git' in directory_list:
            directory_list.remove('.git')
        for item in directory_list:
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                name_file = os.path.basename(full_path)
                print(f'File: {name_file}')
                try:
                    os.chdir(path)
                    cmd = f'git log --follow -- {name_file}'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    if result.returncode != 0:
                        print(f"Failed to get log for file {name_file}")
                        continue
                    revisions = result.stdout.split('\n')
                    commits_list = [atributo for atributo in revisions if 'commit' in atributo]
                    commits = int(len(commits_list))
                    original_encoding = detect_encoding(name_file)
                    if original_encoding != 'utf-8':
                        convert_to_utf8(name_file, original_encoding)
                    insert_files_data(name_file, full_path, commits)
                    if commits != 0:
                        git_blameall.main(name_file)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                            lexer = guess_lexer_for_filename(name_file, file.read())
                            language = lexer.name
                    except FileNotFoundError:
                        print(f"File {name_file} could not be opened.")
                    except ClassNotFound:
                        language = 'Archivo de datos'
                    insert_files_language(language, name_file)
                except FileNotFoundError:
                    print(f"File {name_file} not found during processing.")
                    continue
            elif os.path.isdir(full_path):
                print('\nOpening another directory...\n')
                read_directory(full_path, item)
    except FileNotFoundError as e:
        print(f"Error reading directory {path}: {e}")
        pass


def get_table1():
    # Check that the DB is exiting
    try:
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(connectionString)
    except pyodbc.Error as err:
        print(f"Failed connection to database {NEW_DATABASE}: {str(err)}")
        # Connection to MASTER DATABASE
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
        try:
            connection = pyodbc.connect(connectionString, autocommit=True)
            print("Successful connection to database MASTER")
        except Exception as ex:
            print(f"Failed connection to database MASTER: {str(ex)}")
            return
        cursor = connection.cursor()
        try:
            cursor.execute(f'CREATE DATABASE {NEW_DATABASE}')
            print(f"The {NEW_DATABASE} database has been successfully created.")
        except Exception as ex:
            print(f"Failed to create database, maybe {NEW_DATABASE} already exists: {str(ex)}")
        # Close connection to MASTER DB
        connection.close()
        # Connection to 'Analysis_Github_Repository' DB
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(connectionString)
    # Create 'TABLE_1' or not
    cursor_bd = conn.cursor()
    select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE_1}'"
    cursor_bd.execute(select_table_query)
    result = cursor_bd.fetchone()
    if result[0] > 0:
        print(f"The table '{TABLE_1}' exists in the database.")
    else:
        print(f"The table '{TABLE_1}' does not exist in the database.")
        create_repo_table_query = f'''
        CREATE TABLE {TABLE_1} (
            ID INT PRIMARY KEY IDENTITY(1,1),
            Repo_Name VARCHAR(MAX) NOT NULL
        )
        '''
        cursor_bd.execute(create_repo_table_query)
        conn.commit()
        print(f"{TABLE_1} table created successfully")
    conn.close()


def get_table2():
    # Connection to 'Analysis_Github_Repository' DB
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")
    # Create table or not
    cursor_bd = conn.cursor()
    select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE_2}'"
    cursor_bd.execute(select_table_query)
    result = cursor_bd.fetchone()
    if result[0] > 0:
        #print(f"The table '{TABLE_2}' exists in the database.")
        ""
    else:
        print(f"The table '{TABLE_2}' does not exist in the database.")
        create_files_table_query = f'''
        CREATE TABLE {TABLE_2} (
            File_ID INT PRIMARY KEY IDENTITY(1,1),
            Repo_ID INT,
            File_Name VARCHAR(MAX) NOT NULL,
            File_Path VARCHAR(MAX) NOT NULL,
            File_Language VARCHAR(MAX),
            Commits INT,
            FOREIGN KEY (Repo_ID) REFERENCES {TABLE_1}(ID)
        )
        '''
        cursor_bd.execute(create_files_table_query)
        conn.commit()
        print(f"{TABLE_2} table created successfully")
    conn.close()


def insert_repo_data(name_directory):
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")
        return
    cursor_bd = conn.cursor()
    insert_query = f"INSERT INTO {TABLE_1} (Repo_Name) VALUES (?)"
    cursor_bd.execute(insert_query, name_directory)
    conn.commit()
    conn.close()


def insert_files_data(name_file, pos, commits):
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")
        return
    cursor_bd = conn.cursor()
    cursor_bd.execute(f"SELECT MAX(ID) FROM {TABLE_1}")
    repo_id = cursor_bd.fetchone()[0]
    insert_query = f"INSERT INTO {TABLE_2} (Repo_ID, File_Name, File_Path, Commits) VALUES (?, ?, ?, ?)"
    data_to_insert = (repo_id, name_file, pos, commits)
    cursor_bd.execute(insert_query, data_to_insert)
    conn.commit()
    conn.close()


def insert_files_language(language, name_file):
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")
        return
    cursor_bd = conn.cursor()
    update_query = f"UPDATE {TABLE_2} SET File_Language = ? WHERE File_Name = ?"
    data_to_update = (language, name_file)
    cursor_bd.execute(update_query, data_to_update)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    get_table1()
    menu()
