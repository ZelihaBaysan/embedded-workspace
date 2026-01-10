import pyodbc

# MSSQL bağlantı bilgilerini kendi sunucuna göre düzenle
server = "ZELIS\\REEDUS"
database = "MyDatabase" 
username = "sa"
password = "daryldixon"
driver = "ODBC Driver 18 for SQL Server"

conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute('SELECT id, title, content FROM documents')
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row.id}, Başlık: {row.title}, İçerik: {row.content}")

conn.close()
