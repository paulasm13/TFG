import pyodbc
import matplotlib.pyplot as plt


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Code'


# BBDD connection
connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(connectionString)
    print(f"Conexión exitosa con la BBDD {DATABASE}")
except Exception as ex:
    print(f"No se pudo conectar a la BBDD {DATABASE}: {str(ex)}")

cursor = conn.cursor()

# SELECT LONGEVITY

"""
dead_code = []
updated_code = []

cursor.execute(f'SELECT Longevity, Code FROM {TABLE}')

tuple_list = cursor.fetchall()

longevity_MAX = max(tuple_list, key=lambda x: x[0])[0]

print(f"Longevidad MAX: {longevity_MAX}")

for tuple in tuple_list:
    if tuple[0] == longevity_MAX:
        dead_code.append(tuple)
    elif tuple[0] == '1095':
        updated_code.append(tuple)

# [%]
dead_code_per = (len(dead_code) / len(tuple_list)) * 100

print(f"Dead Code[%]: {dead_code_per}")
print(f"Dead Code: {len(dead_code)}")
print(len(tuple_list))


updated_code_per = (len(updated_code) / len(tuple_list)) * 100
print(f"Updated Code[%]: {updated_code_per}")
print(f"Dead Code: {len(updated_code)}")



x = ['Dead code', 'Updated code']
y = [dead_code_per, updated_code_per]

# Cerrar el cursor y la conexión
cursor.close()
conn.close()

# LONGEVITY GRAPH
plt.plot(x, y)
plt.figure(figsize=(10, 6))
plt.title('Code Analysis')
plt.xlabel('Analysis')
plt.ylabel('%')
plt.grid(axis='y', linestyle='--')

# Mostrar la gráfica
plt.show()

"""