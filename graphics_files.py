import pyodbc
import matplotlib.pyplot as plt


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Files'


# BBDD connection
connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(connectionString)
    print(f"Conexión exitosa con la BBDD {DATABASE}")
except Exception as ex:
    print(f"No se pudo conectar a la BBDD {DATABASE}: {str(ex)}")

cursor = conn.cursor()


# SELECT LANGUAGE
cursor.execute(f'SELECT Language FROM {TABLE}')

languages = []
percentages = []
for row in cursor:
    languages.append(row.Language)

for atribute in languages:
    count_atr = languages.count(atribute)
    percentage_atr = (count_atr / len(languages)) * 100
    percentages.append(percentage_atr)

# LANGUAGE GRAPH
plt.figure(figsize=(10, 6))
plt.bar(languages, percentages, color='skyblue')
plt.title('Lenguajes utilizados en el repositorio [%]')
plt.xlabel('Lenguajes')
plt.ylabel('%')
plt.grid(axis='y', linestyle='--')
#plt.savefig('Language_graph.png')
plt.show()

# SELECT COMMITS
cursor.execute(f'SELECT Name, Commits FROM {TABLE}')

tuples = cursor.fetchall()

# COMMITS GRAPH
plt.figure(figsize=(10, 6))
for atribute in tuples:
    plt.bar(str(atribute[0]), str(atribute[1]), color='skyblue')
plt.title('Número de commits por archivo')
plt.xlabel('Archivos')
plt.ylabel('Commits')
plt.grid(axis='y', linestyle='--')
plt.xticks(rotation=45)
plt.tight_layout()
#plt.savefig('Commits_graph.png')
plt.show()

cursor.close()
conn.close()