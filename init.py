"""


ARCHIVO PARA ANALIZAR UN DIRECTORIO

- Clona un repositorio 
- Analiza su contenido
- Lista los ficheros en una BBDD


"""

import os
import sys
import requests
import subprocess


def menu():
    """ Choose option. """
    if type_option == 'repo-url':
        request_url()        
    else:
        sys.exit('Usage: python3 init.py 'repo-url' <name_urlclone>]')


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


def run_user():
    """ Run user. """
    # Create the url of the api
    user_url = ("https://api.github.com/users/" + option)
    print(user_url)
    print("Analyzing user...\n")
    try:
        # Extract headers
        headers = requests.get(user_url)
        # Decode JSON response into a Python dict:
        content = headers.json()
        # Get repository url
        repo_url = content["repos_url"]
    except KeyError:
        sys.exit('An unavailable user has been entered')
    print("Analyzing repositories...\n")
    # Extract repository names
    names = requests.get(repo_url)
    # Decode JSON response into a Python dict:
    content = names.json()
    # Show repository names
    for repository in content:
        print('\nRepository: ' + str(repository["name"]))
        url = ("https://github.com/" + option + "/" + repository["name"])
        check_lenguage(url, 'https', 'github.com', option, repository["name"])


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
        absFilePath = absFilePath.replace("/" + fichero, "")
    print("This script absolute path is ", absFilePath)
    read_Directory(absFilePath, name_directory)



def read_Directory(absFilePath, repo):
    """ Extract the files from the directory. """
    #pos = ''
    print('Directory: ')
    path = absFilePath
    print(path)
    try:
        # I get a list of the files and subdirectories in the given directory
        directory = os.listdir(path)
        print(directory)
        # File...
        for i in range(0, len(directory)):
            if directory[i].endswith('.'):
                print('Python File: ' + str(directory[i]))
                pos = path + "/" + directory[i]
                #read_File(pos, repo)
            # Subdirectory...
            elif '.' not in directory[i]:
                print('\nOpening another directory...\n')
                path2 = absFilePath + '/' + directory[i]
                try:
                    read_Directory(path2, directory[i])
                except NotADirectoryError:
                    pass
    except FileNotFoundError:
        print(os.listdir(path))
        pass


if __name__ == "__main__":
    try:
        type_option = sys.argv[1]
        option = sys.argv[2]
    except:
        sys.exit("Usage: python3 init.py 'repo-url' url")
        
menu()
