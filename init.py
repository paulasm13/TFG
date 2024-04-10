"""


ARCHIVO PARA ANALIZAR UN DIRECTORIO

- Clona un repositorio 
- Analiza su contenido
- Lista los ficheros, y los guarda en una BBDD
- Descarta el archivo .git que se crea al clonar el repositorio (xq se crea?)


"""

import os
import sys
import requests
import subprocess
import pyodbc
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound


def menu():
    """ Choose option. """
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
    print("Analyzing repository languages...\n")
    print(repo_url)
    # Get content
    r = requests.get(repo_url)
    print(r)
    """ Run url. """
    command_line = "git clone " + repo_url
    print('Run url...')
    print(command_line)
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
    get_path(name_directory)


def get_path(name_directory):
    """ Get the path to the directory. """
    absFilePath = os.path.abspath(name_directory)
    # Check if the last element is a file
    fichero = absFilePath.split('/')[-1]
    if fichero.endswith('.'):
        absFilePath = absFilePath.replace("\\" + fichero, "")
    print("This script absolute path is ", absFilePath)
    read_Directory(absFilePath, name_directory)


def read_Directory(absFilePath, repo):
    """ Extract the files from the directory. """
    id = 0
    pos = ''
    print('Directory: ')
    path = absFilePath
    print(path)
    try:
        # I get a list of the files and subdirectories in the given directory
        directory = os.listdir(path)
        # File...
        for i in range(0, len(directory)):
            if '.' in directory[i] and not directory[i].startswith('.'):
                print('Python File: ' + str(directory[i]))
                name_file = str(directory[i])
                pos = path + "\\" + directory[i]   
                try:
                    with open(pos, 'rb') as file:
                        lexer = guess_lexer_for_filename(name_file, file.read())
                        language = lexer.name
                        print(f"El archivo {name_file} está en {language}.")
                except FileNotFoundError:
                    print(f"No se pudo abrir el archivo {name_file}.")
                except ClassNotFound:
                    print(f"No se pudo determinar el lenguaje para {name_file}.")
                    language = None
                id += 1
                add_file(id, name_file, pos, language)
            # Subdirectory...
            elif '.' not in directory[i]:
                print('\nOpening another directory...\n')
                path2 = absFilePath + '\\' + directory[i]
                try:
                    read_Directory(path2, directory[i])
                except NotADirectoryError:
                    pass
    except FileNotFoundError:
        print(os.listdir(path))
        pass


def add_file(id, name_file, pos, language):
    # Connection to SERVER
    SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
    DATABASE = 'master'

    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

    try:
        connection_server = pyodbc.connect(connectionString)
        print("Conexión exitosa con el servidor")
    except Exception as ex:
        print(f"No se pudo conectar con el servidor de la base de datos: {str(SERVER)}")

    # Create/Connection BBDD
   
    connection_server.close()

if __name__ == "__main__":
    try:
        type_option = sys.argv[1]
        option = sys.argv[2]
    except:
        sys.exit("Usage: python3 init.py 'repo-url' url")
        
menu()
