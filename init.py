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
NEW_DATABASE = 'Analysis_Github_Repository'
TABLE_1 = 'Repositories'
TABLE_2 = 'Files'

def detect_encoding(name_file):
    try:
        with open(name_file, 'rb') as f:
            raw_data = f.read()
        if not raw_data:
            return None
        result = chardet.detect(raw_data)
        print(f"RESULT: {result}")
        return result['encoding']
    except Exception as e:
        print(f"Error detecting encoding for file {name_file}: {e}")

def convert_to_utf8(name_file, original_encoding):
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
    get_directory(repo_url)

def get_directory(repo_url):
    values = repo_url.split('/')
    name_directory = values[-1]
    if '.git' in str(name_directory):
        name_directory = name_directory[0:-4]
    print("The directory is: " + name_directory)
    insert_repo_data(name_directory)
    get_bd2()
    get_path(name_directory)

def get_path(name_directory):
    absFilePath = os.path.abspath(name_directory)
    print("This script absolute path is ", absFilePath)
    read_directory(absFilePath, name_directory)

def read_directory(absFilePath, name_directory):
    path = absFilePath
    print(f"Directory: {path}")
    try:
        directory = os.listdir(path)
        print(f"List of files and subdirectories: {path}")
        for item in directory:
            if not item:
                continue
            if item.endswith('.tar.gz') or item.endswith('.zip'):
                continue
            if '.' in item and not item.startswith('.'):
                print('File: ' + item)
                name_file = item
                pos = f"{path}/{item}"
                os.chdir(path)
                cmd = f'git log --follow -- {name_file}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if result.returncode != 0:
                    print(f"Failed to get log for file {name_file}")
                    continue
                revisions = result.stdout.split('\n')
                commits_list = [atributo for atributo in revisions if 'commit' in atributo]
                commits = len(commits_list)
                original_encoding = detect_encoding(name_file)
                print(f"ORIGINAL_ENCODING: {original_encoding}")
                if original_encoding is None:
                    print(f"Skipping file {name_file} due to unknown encoding")
                    continue
                if original_encoding != 'utf-8':
                    convert_to_utf8(name_file, original_encoding)
                insert_files_data(name_file, pos, commits)
                if commits != 0:
                    git_blameall.main(name_file)
                try:
                    with open(pos, 'r', encoding='utf-8', errors='ignore') as file:
                        lexer = guess_lexer_for_filename(name_file, file.read())
                        language = lexer.name
                except FileNotFoundError:
                    print(f"File {name_file} could not be opened.")
                except ClassNotFound:
                    language = 'Archivo de datos'
                insert_files_language(name_file, language)
            elif '.' not in item:
                print('\nOpening another directory...\n')
                path2 = f"{absFilePath}/{item}"
                try:
                    read_directory(path2, item)
                except NotADirectoryError:
                    pass
    except FileNotFoundError as e:
        print(f"Error reading directory {path}: {e}")

def get_bd1():
    try:
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(connectionString)
    except pyodbc.Error as err:
        print(f"Failed connection to database {NEW_DATABASE}: {str(err)}")
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
        finally:
            connection.close()
        connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(connectionString)
    cursor_bd = conn.cursor()
    select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE_1}'"
    cursor_bd.execute(select_table_query)
    result = cursor_bd.fetchone()
    if result[0] == 0:
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

def get_bd2():
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={NEW_DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {NEW_DATABASE}: {str(ex)}")
        return
    cursor_bd = conn.cursor()
    select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE_2}'"
    cursor_bd.execute(select_table_query)
    result = cursor_bd.fetchone()
    if result[0] == 0:
        create_files_table_query = f'''
        CREATE TABLE {TABLE_2} (
            File_ID INT PRIMARY KEY IDENTITY(1,1),
            Repo_ID INT,
            File_Name VARCHAR(MAX) NOT NULL,
            File_Path VARCHAR(MAX) NOT NULL,
            File_Language VARCHAR(50),
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

def insert_files_language(name_file, language):
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
    get_bd1()
    menu()
