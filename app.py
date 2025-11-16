from flask import Flask, render_template, request, redirect, url_for, flash, session
import db

app = Flask(__name__)
app.secret_key = "secret_key"

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    users = db.get_all_users()
    usernames = [dict(user)['username'] for user in users]
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash("All fields are required.")
        return render_template('index.html', username=username, password=password)
    if username in usernames:
        flash("Username already exists.")
        return render_template('index.html', username=username, password=password)
    if db.add_user(username, password):
        flash("Registration successful.")
        return render_template('index.html')
    
@app.route('/login', methods=['GET','POST'])
def login_route():
    # users = db.get_all_users()

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash("All fields are required.")
        return redirect(url_for('login_route'))

    user = db.login(username, password)
    if user:
        user = dict(user)
        session['user'] = user
        print('session:',session['user'])
        flash("Logged in successfully.")
        if user['isAdmin'] == 1:
            foods = db.get_all_foods()
            return redirect(url_for('admin'))
        else:
            # return redirect(url_for('index'))
            # flash("You are not an admin.")
            return redirect(url_for('customer'))
    else:
        flash("Invalid username or password.")
        return redirect(url_for('login_route'))
    
    # return render_template('dasjboard.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    print('session:',session)
    return redirect(url_for('login_route'))

@app.route('/add-food', methods=['GET', 'POST'])
def add_food():
    if request.method == 'GET':
        return render_template('add-food.html')

    foodname = request.form['foodname']
    foodprice = request.form['foodprice']

    if not foodname or not foodprice:
        flash("All fields are required.")
        return render_template('add-food.html', foodname=foodname, foodprice=foodprice)

    db.add_food(foodname, foodprice)
    flash("Food added successfully.")

    foods = db.get_all_foods()
    return redirect(url_for('admin'))


@app.route('/admin')
def admin():
    foods = db.get_all_foods()
    return render_template('admin-dashboard.html', foods=foods)

@app.route('/edit-food', methods=['GET', 'POST'])
def edit_food():
    if request.method=='GET':
        foodID = request.args.get('foodId')
        food = db.get_food_by_Id(foodID)
        return render_template('edit-food.html', food=food)
    
    foodId = request.form['foodId']
    foodname = request.form['foodname']
    foodprice = request.form['foodprice']

    if not foodname or not foodprice:
        flash("All fields are required.")
        return render_template('edit-food.html', foodname=foodname, foodprice=foodprice)
    
    if db.db_edit_food(foodname, foodprice, foodId):
        flash("Food edited successfully.")
    else:
        flash("Failed to edit food.")

    return redirect(url_for('admin'))

@app.route('/delete-food', methods=['GET', 'POST'])
def delete_food():
    foodId = request.form['foodId']
    if db.delete_food(foodId):
        flash("Food deleted successfully.")
    else:
        flash("Failed to delete food.")

    return redirect(url_for('admin'))

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'GET':
        foods = db.get_all_foods()
        purchases = db.get_all_user_purchases(session['user']['userId'])
        return render_template('customer-dashboard.html', foods=foods, purchases=purchases)

@app.route('/add-purchase', methods=['GET', 'POST'])
def add_purchase():
    userId = session['user']['userId']
    food_ids = request.form.getlist('foodId[]')
    quantities = request.form.getlist('quantity[]')
    print('user: ', session['user'])
    print('cart: ', food_ids)
    purchase_id = db.add_purchase(userId)
    if purchase_id:
        for food_id in food_ids:
            if db.add_purchase_list(purchase_id, food_id, quantities[food_ids.index(food_id)]):
                flash('Purchase added')
                return redirect(url_for('customer'))
    return redirect(url_for('customer'))
    # userId = session['user']['userId']
    # print(userId)
    # if db.add_purchase(userId, cart):
    #     flash("Purchase added successfully.")
    #     return redirect(url_for('customer'))
    # else:
    #     flash("Failed to add purchase.")
    #     return redirect(url_for('customer'))

if __name__ == "__main__":
    app.run(debug=True)