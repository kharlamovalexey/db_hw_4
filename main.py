import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS client(
                    client_id serial PRIMARY KEY,
                    name varchar(50),
                    surname varchar(50),
                    email varchar(50)
                    );

                    CREATE TABLE IF NOT EXISTS phone(
                    phone_id serial PRIMARY KEY,
                    client_id int REFERENCES client(client_id),
                    phone varchar(15) NOT NULL
                    );
                    ''')
        conn.commit()

def drop_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
                    DROP TABLE IF EXISTS phone CASCADE;
                    DROP TABLE IF EXISTS client CASCADE;
                    ''')
        conn.commit()

def add_client(conn, name, surname, email, phones:list=None):
    with conn.cursor() as cur:
        cur.execute('''
                    INSERT INTO CLIENT(name, surname, email)
                    VALUES(%s, %s, %s)
                    RETURNING client_id;
                    ''',(name, surname, email))
        client_id = cur.fetchone()[0]
        print(client_id)
        conn.commit()
        if phones is not None :
            for phone in phones:
                add_phone(conn, client_id, phone)

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
                    INSERT INTO phone(client_id, phone)
                    VALUES(%s, %s);
                    ''', (client_id, phone))
        conn.commit()

def change_client(conn, client_id, name=None, surname=None, email=None, phones:list=None):
    with conn.cursor() as cur:
        cur.execute('''
                    UPDATE client 
                    SET 
                    name = %s, 
                    surname = %s,
                    email= %s
                    WHERE client_id = %s;

                    DELETE FROM phone
                    WHERE client_id = %s;
                    ''', (name, surname, email, client_id, client_id))

        conn.commit()
        for phone in phones:
            add_phone(conn, client_id, phone)
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''
                    DELETE FROM phone
                    WHERE client_id = %s and phone = %s;
                    ''', (client_id, phone))
    conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''
                    DELETE FROM phone
                    WHERE client_id = %s;

                    DELETE FROM client
                    WHERE client_id = %s
                    ''', (client_id, client_id))
    conn.commit()

def find_client(conn, name=None, surname=None, email=None, phone=None):
    sql = '''SELECT * FROM client
             WHERE client_id = client_id 
          '''
    if name:
        sql = sql + f"AND name = '{name}'"
    if surname: 
        sql = sql + f" AND  surname = '{surname}'"
    if email: 
        sql = sql + f" AND  email = '{email}'"
    if phone:
        sql = """AND client_id 
                 IN (SELECT client_id FROM phone
                 WHERE phone = '{phone}')"""
    sql = sql + ';'
    with conn.cursor() as cur:  
        cur.execute(sql)
        print (cur.fetchall())



conn = psycopg2.connect(database="pgs_db", user="postgres", password="pgs")
drop_db(conn)
create_db(conn)

add_client(conn, 'Иван', 'Иванов', 'ivanov@gmail.ru', ['+71234567', '+79874532'])
add_client(conn, 'Иван', 'Петров', 'ivanovpetrov@gmail.ru', ['+71234567111', '+7987453211'])
change_client(conn, 1, 'Иван', 'Ivanov', 'ivanov@gmail.ru',  ['+71234567', '+98745631'])

find_client(conn, name='Иван')
delete_phone(conn, 1, '+98745631')
delete_client(conn, 1)

conn.close()
