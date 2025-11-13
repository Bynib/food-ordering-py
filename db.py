import sqlite3

db = "foodordering.db"

def connect():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    sql = ['''create table if not exists food (
            foodId integer primary key autoincrement,
            foodName text,
            foodPrice decimal
        );''',
        '''create table if not exists user (
            userId integer primary key autoincrement,
            username text,
            password text,
            isAdmin integer
        );''',
        '''create table if not exists purchase(
            purchaseId integer primary key autoincrement,
            userId integer references user(userId),
            purchaseDate text not null default current_timestamp
        );''',
        '''create table if not exists purchase_list (
            purchaseID integer references purchase(purchaseId),
            foodId integer references food(foodId),
            quantity integer,
            primary key (purchaseID, foodID)
        );''']
    
    with connect() as conn:
        for statement in sql:
            conn.execute(statement)
            conn.commit()
    
def get_all_foods():
    sql = 'select * from food'
    with connect() as conn:
        foods = conn.execute(sql).fetchall()
        foods = [dict(food) for food in foods]
        return foods

def get_all_users():
    sql = 'select * from user'
    with connect() as conn:
        users = conn.execute(sql).fetchall()
        users = [dict(user) for user in users]
        return users
        
def get_all_purchases():
    sql = '''
        select
            p.purchaseId,
            p.purchaseDate,
            pl.foodId,
            pl.quantity
        from purchase p
        left join purchase_list pl
        on p.purchaseId = pl.purchaseId
        order by p.purchaseId
    '''

    with connect() as conn:
        purchases = conn.execute(sql).fetchall()
        
    purchases = {}
    for purchase in purchases:
        pid = purchase['purchaseId']
        if pid not in purchases:
            purchases[pid] = {
                'purchaseId': pid,
                'purchaseDate': purchase['purchaseDate'],
                'items': []
            }
        if purchase['foodId'] is not None:
            purchases[pid]['items'].append({
                'foodId': purchase['foodId'],
                'quantity': purchase['quantity']
            })

    return list(purchases.values())

def add_food(foodname, foodprice):
    sql = '''insert into food (foodName, foodPrice) values (?,?)'''
    with connect() as conn:
        conn.execute(sql,(foodname,foodprice))
        conn.commit()

def add_user(username, password):
    users = get_all_users()
    isAdmin = 0
    if not users:
        isAdmin = 1
    sql = '''insert into user (username, password, isAdmin) values (?,?,?)'''
    with connect() as conn:
        conn.execute(sql, (username, password, isAdmin))
        conn.commit()

def login(username, password):
    sql = 'select * from user where username = ? and password = ?'
    with connect() as conn:
        user = conn.execute(sql,(username, password)).fetchone()
        return user


def add_purchase(userId):
    sql = 'insert into purchase (userID) values (?)'
    with connect() as conn:
        conn.execute(sql, (userId,))
        conn.commit()

def add_purchase_list(purchaseId, items):
    sql = 'insert into purchase_list (purchaseId, foodId, quantity) values (?,?,?)'
    with connect() as conn:
        for item in items:
            conn.execute(sql, (purchaseId, item.foodId, item.quantity))
            conn.commit()


if __name__ == "__main__":
    create_tables()
    # add_user('bynib', 'bynibshi')
    print(dict(login('bynib', 'bynibshi')))