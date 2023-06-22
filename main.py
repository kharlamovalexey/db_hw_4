import psycopg2

def create_tables(cur):
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

def drop_tables(cur):
    cur.execute('''
                DROP TABLE IF EXISTS phone CASCADE;
                DROP TABLE IF EXISTS client CASCADE;
                ''')

def add_client(cur, name, surname, email, phones:list=None):
    cur.execute('''
                INSERT INTO CLIENT(name, surname, email)
                VALUES(%s, %s, %s)
                RETURNING client_id;
                ''',(name, surname, email))

    client_id = cur.fetchone()[0]
   
    if phones is not None :
        for phone in phones:
            add_phone(cur, client_id, phone)
    return client_id

def add_phone(cur, client_id, phone):
    cur.execute('''
                INSERT INTO phone(client_id, phone)
                VALUES(%s, %s);
                ''', (client_id, phone))

def change_client(cur, client_id, name=None, surname=None, email=None, phones:list=None):
    cur.execute('''
                UPDATE client 
                SET 
                name = COALESCE(%s, name), 
                surname = COALESCE(%s, surname),
                email= COALESCE(%s, surname)
                WHERE client_id = %s;
                ''', (name, surname, email, client_id,))

    if phones is not None:
        delete_phone(cur,client_id=client_id)
        for phone in phones:
            add_phone(cur, client_id, phone)

def delete_phone(cur, client_id, phone=None):
    if phone is None:
        cur.execute('''
                DELETE FROM phone
                WHERE client_id = %s;
                ''', (client_id,))
    else:
        cur.execute('''
                DELETE FROM phone
                WHERE client_id = %s and phone = %s;
                ''', (client_id, phone))

def delete_client(cur, client_id):
    cur.execute('''
                DELETE FROM phone
                WHERE client_id = %s;

                DELETE FROM client
                WHERE client_id = %s
                ''', (client_id, client_id))

def find_client(cur, name='NULL', surname='NULL', email='NULL', phone='NULL'):
    cur.execute('''SELECT * FROM client
                WHERE client_id = client_id
                AND name = COALESCE({}, name)
                AND  surname = COALESCE({}, surname)
                AND  email = COALESCE({}, email)
                AND client_id 
                    IN (SELECT client_id FROM phone
                    WHERE phone = COALESCE('{}', phone));'''.format (name, surname, email, phone))

    return cur.fetchall()

def show_client(cur, client_id):
    cur.execute('''SELECT * FROM client
            WHERE client_id = %s
            ''', (client_id,))

    client = cur.fetchone()
    print(client[0])
    print(f'id:{client[0]} Имя:{client[1]} Фамилия:{client[2]} email:{client[3]}')

    cur.execute('''SELECT * FROM phone
            WHERE client_id = %s
            ''', (client_id,))
    phones =  cur.fetchall()
    print('Телефоны:')
    for phone in phones:
        print(phone[2])

if __name__ == '__main__':
    with psycopg2.connect(host = 'localhost',  database="postgres", user="postgres", password="pgs") as conn:
        with conn.cursor() as cur:
            drop_tables(cur)
            create_tables(cur)

            client_1 = add_client(cur, 'Иван', 'Иванов', 'ivanov@gmail.ru', ['+79998887766', '+79998887767'])
            client_2 = add_client(cur, 'Петр', 'Петров', 'petrov@gmail.ru', ['+78985556633', '+78985556636'])
            client_3 = add_client(cur, 'Сидор', 'Сидоров', 'sidirovSS@gmail.ru', ['+71231234567', '+755533322211'])

            change_client(cur, client_1, name='Ivan', surname='Ivanov',  phones=['+79998887764', '+79998887765'])
            # change_client(cur, client_1, name='Ivan', surname='Ivanov', )

            rec = find_client(cur, phone = '+78985556636')
            print(rec)

            delete_phone(cur, 1, '+78985556636')
            show_client(cur, client_1)
            delete_client(cur, 1)

            show_client(cur, client_2)
            show_client(cur, client_3)

    
