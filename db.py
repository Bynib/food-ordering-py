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
    
def get_food_by_Id(foodId):
    sql = 'select * from food where foodId = ?'
    with connect() as conn:
        food = conn.execute(sql, (foodId)).fetchone()
        food = dict(food)
        return food

def delete_food(foodId):
    sql = 'delete from food where foodId = ?'
    with connect() as conn:
        conn.execute(sql, (foodId))
        conn.commit()

def get_all_users():
    sql = 'select * from user'
    with connect() as conn:
        users = conn.execute(sql).fetchall()
        users = [dict(user) for user in users]
        return users
        
def get_all_user_purchases(userId):
    sql = '''
        select
            p.purchaseId,
            p.purchaseDate,
            pl.foodId,
            f.foodName,
            pl.quantity,
            f.foodPrice
        from purchase p
        left join purchase_list pl
        on p.purchaseId = pl.purchaseId
        join food f
        on f.foodId = pl.foodId
        where p.userId = ?
        order by p.purchaseId
    '''

    with connect() as conn:
        db_purchases = conn.execute(sql, (userId,)).fetchall()
        
    purchases = {}
    for purchase in db_purchases:
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
                'foodName': purchase['foodName'],
                'foodPrice': purchase['foodPrice'],
                'quantity': purchase['quantity']
            })

    return list(purchases.values())

def add_food(foodname, foodprice):
    sql = '''insert into food (foodName, foodPrice) values (?,?)'''
    with connect() as conn:
        conn.execute(sql,(foodname,foodprice))
        conn.commit()

def db_edit_food(foodname, foodprice, foodid):
    sql = 'update food set foodName = ?, foodPrice = ? where foodId = ?'
    with connect() as conn:
        foodprice = float(foodprice)
        conn.execute(sql, (foodname, foodprice, foodid))
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
    sql = 'select userId, username, isAdmin from user where username = ? and password = ?'
    with connect() as conn:
        user = conn.execute(sql,(username, password)).fetchone()
        return user


def add_purchase(userId):
    sql = 'insert into purchase (userID) values (?)'
    with connect() as conn:
        conn.execute(sql, (userId,))
        conn.commit()
        return conn.execute('select last_insert_rowid()').fetchone()[0]

def add_purchase_list(purchaseId, foodId, quantity):
    sql = 'insert into purchase_list (purchaseId, foodId, quantity) values (?,?,?)'
    print("items: ", foodId)

    with connect() as conn:
        conn.execute(sql, (purchaseId, foodId, quantity))
        conn.commit()

def all_purchase():
    sql = 'select * from purchase'
    with connect() as conn:
        purchase = conn.execute(sql).fetchall()
        purchase = [dict(p) for p in purchase]
        return purchase
    
def all_purchase_list():
    sql = 'select * from purchase_list'
    with connect() as conn:
        purchase_list = conn.execute(sql).fetchall()
        purchase_list = [dict(p) for p in purchase_list]
        return purchase_list


if __name__ == "__main__":
    create_tables()
    # add_user('bynib', 'bynibshi')
    # print(dict(login('bynib', 'bynibshi')))
    # print(db_edit_food('Biryani', 100, 1))
    # print(get_all_foods())
    print(get_all_user_purchases(2))
    # print("all purchase: ", all_purchase())
    # print("all purchase list: ", all_purchase_list())