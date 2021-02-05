from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import datetime
import sqlite3
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import re

from helpers import ingredientItemList, wholeNumber, convertMetric

app = Flask(__name__)

app.secret_key = 'lamp4724851'

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "GET":
        
        #Populate with published recipes on database.
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            indexRecipes = cur.execute(
                "SELECT recipe_id, title, serves, author, method FROM recipes WHERE published = 1 ORDER BY recipe_id DESC LIMIT 100")
            indexRecipes = cur.fetchall()

        indexList = []
        indexList.clear()

        for item in indexRecipes:
            dict_item = {'id': item[0], 'title': item[1], 'serves': item[2], 'author': item[3], 'method': item[4]}
            indexList.append(dict_item) 
            dict_item['method'] = dict_item['method'][0:150]
            dict_item['method'] += "..."

        
        return render_template('index.html', indexList=indexList)

@app.route("/profile", methods=["GET"])
def profile():
    
    if request.method == "GET":
        
        #Populate with published recipes on database.
        if "user_id" in session:
            session.user = session["username"]

        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            indexRecipes = cur.execute(
                "SELECT recipe_id, title, serves, author, method FROM recipes WHERE published = 1 and author = ? ORDER BY recipe_id DESC LIMIT 100", (session.user,))
            indexRecipes = cur.fetchall()

        indexList = []
        indexList.clear()

        for item in indexRecipes:
            dict_item = {'id': item[0], 'title': item[1], 'serves': item[2], 'author': item[3], 'method': item[4]}
            indexList.append(dict_item) 
            dict_item['method'] = dict_item['method'][0:150]
            dict_item['method'] += "..."

        return render_template('profile.html', indexList=indexList)


@app.route("/user_view", methods=["GET"])
def user_view():

    if request.method == "GET":
        
        #Populate with published recipes on database.
        if "user_id" in session:
            session.user = session["username"]

        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            indexRecipes = cur.execute(
                "SELECT recipe_id, title, serves, author, method FROM recipes WHERE published = 1 and author = ? ORDER BY recipe_id DESC LIMIT 100", (request.args.get("username"),))
            indexRecipes = cur.fetchall()

        indexList = []
        indexList.clear()

        for item in indexRecipes:
            dict_item = {'id': item[0], 'title': item[1], 'serves': item[2], 'author': item[3], 'method': item[4]}
            indexList.append(dict_item) 
            dict_item['method'] = dict_item['method'][0:150]
            dict_item['method'] += "..."

        return render_template('user_view.html', username=request.args.get("username"), indexList=indexList)


@app.route("/view", methods=["GET"])
def view():
    
    if request.method == "GET":

        if "user_id" in session:
            session.user = session["username"]

        session.recipe_id = request.args.get("id")

        # Get recipe from database
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()

            # Drop recipe into recipe table (minus ingredients)
            recipes = cur.execute(
                "SELECT title, serves, method, author, notes FROM recipes WHERE recipe_id = ?", (session.recipe_id,))
            recipes = cur.fetchall()

            ingredients = cur.execute(
                "SELECT ingredient, quantity, unit, item_id FROM ingredients_table WHERE recipe_id = ?", (session.recipe_id,))
            ingredients = cur.fetchall()
            
        session.title = recipes[0][0]
        session.servings = recipes[0][1]
        session.method = recipes[0][2]
        session.author = recipes[0][3]
        
        table = []
        table.clear()

        for item in ingredients:
            dict_item = {'ingredient':item[0], 'quantity':wholeNumber(item[1]), 'unit':item[2], 'item_id':item[3]}
            table.append(dict_item) 

        return render_template('view.html', recipe_id=request.args.get("id"), table=table)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    
    if request.method == "POST":

        session.item_id = request.form.get("item_id")

        if request.form.get("update") == "1":
            item_change = request.form.get("ingredient")
            
            # Process item_change.
            item_change = ingredientItemList([item_change])

            # Convert to metric (volumes:volumes, mass:mass)
            if request.form.get("convertMetric") == "1":
                item_change = convertMetric(item_change)

            dataB = (
                            (
                                item_change[0]['ingredient'], item_change[0]['quantity'], item_change[0]['unit'], str(session.item_id)
                            )
                        )

            # Prepare redirect arg. Make change to dataase.
            con = sqlite3.connect('data.db')
            with con:
                cur = con.cursor()
                session.recipe_id = cur.execute(
                        "SELECT recipe_id FROM ingredients_table WHERE item_id = ?", (session.item_id,))
                session.recipe_id = cur.fetchone()
                cur.execute(
                        "UPDATE ingredients_table SET ingredient = ?, quantity = ?, unit = ? WHERE item_id = ?",
                dataB)

        elif request.form.get("delete") == "1":
            con = sqlite3.connect('data.db')
            with con:
                cur = con.cursor()
                session.recipe_id = cur.execute(
                        "SELECT recipe_id FROM ingredients_table WHERE item_id = ?", (session.item_id,))
                session.recipe_id = cur.fetchone()
                cur.execute(
                        "DELETE FROM ingredients_table WHERE item_id = ?", (session.item_id,))

        elif request.form.get("back"):
            # Back button pressed. Need to check if item is a new entry that wasn't confirmed. If so, delete.
            con = sqlite3.connect('data.db')
            with con:
                cur = con.cursor()
                item_id = cur.execute(
                        "SELECT * FROM ingredients_table ORDER BY item_id DESC LIMIT 1")
                item_id = cur.fetchone()
                if item_id[2] == None and item_id[3] == 0.0 and item_id[4] == None:
                    cur.execute(
                            "DELETE FROM ingredients_table WHERE item_id = ?", (item_id[0],))
    
        session.recipe_id = request.form.get("editRecipe")

        # Get recipe from database
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()

            # Drop recipe into recipe table (minus ingredients)
            recipes = cur.execute(
                "SELECT title, serves, method, author, notes, published FROM recipes WHERE recipe_id = ?", (session.recipe_id,))
            recipes = cur.fetchall()

        # If number of ingredient items != 0, get list of ingredients.
            ingredients = cur.execute(
                "SELECT ingredient, quantity, unit, item_id FROM ingredients_table WHERE recipe_id = ?", (session.recipe_id,))
            ingredients = cur.fetchall()

        table = []
        table.clear()
        
        for item in ingredients:
            dict_item = {'ingredient':item[0], 'quantity':wholeNumber(item[1]), 'unit':item[2], 'item_id':item[3]}
            table.append(dict_item) 
        
        if ingredients:
            session.item_id = ingredients[0][3]

        session.title = recipes[0][0]
        session.servings = recipes[0][1]
        session.method = recipes[0][2]
        session.published = recipes[0][5]

        return render_template('edit.html', recipe_id=session.recipe_id, table=table, published=session.published)

    if request.method == "GET":

        session.recipe_id = request.args.get("id")

        # Get recipe from database
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()

            # Drop recipe into recipe table (minus ingredients)
            recipes = cur.execute(
                "SELECT title, serves, method, author, notes, published FROM recipes WHERE recipe_id = ?", (session.recipe_id,))
            recipes = cur.fetchall()

            ingredients = cur.execute(
                "SELECT ingredient, quantity, unit, item_id FROM ingredients_table WHERE recipe_id = ?", (session.recipe_id,))
            ingredients = cur.fetchall()
        
        table = []
        table.clear()
        


        for item in ingredients:
            dict_item = {'ingredient':item[0], 'quantity':wholeNumber(item[1]), 'unit':item[2], 'item_id':item[3]}
            table.append(dict_item) 
        
        if ingredients:
            session.item_id = ingredients[0][3]

        session.title = recipes[0][0]
        session.servings = recipes[0][1]
        session.method = recipes[0][2]
        session.published = recipes[0][5]

        return render_template('edit.html', recipe_id=request.args.get("id"), table=table, published=session.published)


@app.route("/edit_ingredient", methods=["POST"])
def edit_ingredient():
    


    if request.method == "POST": 

        recipe_id = request.form.get("recipe_id")

        item_id = request.form.get("edit_ingredient")
        if item_id != "add_new":

            # Get item data.
            con = sqlite3.connect('data.db')
            with con:
                cur = con.cursor()
                item = cur.execute(
                        "SELECT quantity, unit, ingredient FROM ingredients_table WHERE item_id = ?", (item_id,))
                item = cur.fetchall()
            
            itemList = []
            i = 0
            while i < 3:
                itemList.append(item[0][i])
                i += 1
            itemList[0] = wholeNumber(itemList[0])

            itemFormat = ''
            for i in itemList:
                itemFormat += str(i)
                # Insert spaces in between words
                itemFormat += " "


        else:
            # Get item_id for new item.
            con = sqlite3.connect('data.db')
            with con:
                cur = con.cursor()
                cur.execute(
                        "INSERT INTO ingredients_table (recipe_id, quantity) VALUES (?, ?)", (recipe_id, 0))
                item_id = cur.execute(
                        "SELECT * FROM ingredients_table ORDER BY item_id DESC LIMIT 1")
                item_id = cur.fetchone()

                item_id = item_id[0]

                itemFormat = ''

        return render_template('edit_ingredient.html', itemFormat=itemFormat, recipe_id=recipe_id, item_id=item_id)


@app.route("/contribute", methods=["GET", "POST"])
def contribute():
    
    if request.method == "GET":
        
        return render_template('contribute.html')
    
    if request.method == "POST":

        # NEED TO FIX SO THAT RECIPES DELETED ARE SPECFIC TO USER- ONCE LOG IN IS CREATED!
        # Remove any "unpublished" recipes from database before requesting new data.
        session.author = session["username"]

        
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            unpublished_id = cur.execute(
                "SELECT recipe_id FROM recipes WHERE published = 0 AND author = ?", (session.author,))
            unpublished_id = cur.fetchall()
            #print(unpublished_id)

            for i in unpublished_id:
                cur.execute(
                    "DELETE FROM recipes WHERE recipe_id = ? AND author = ?", ((i[0]), session.author))
                cur.execute(
                    "DELETE FROM ingredients_table WHERE recipe_id = ?", i)


        # Get requests
        session.title = request.form.get("title").title()
        session.servings = request.form.get("servings")
        session.ingredients_list = request.form.get("ingredients").split('\r\n')
        session.method = request.form.get("method")
        session.metricRequest = request.form.get("convertMetric")


        # Check if servings not a number
        if not session.servings.isnumeric():
            message = "Entry for Servings must be numeric."
            return render_template('/contribute.html', message=message)
        
        # Send user list to function. Returns ingredients as formatted list of dicts.
        table = ingredientItemList(session.ingredients_list)

        # Convert to metric (volumes:volumes, mass:mass)
        if session.metricRequest == "1":
            table = convertMetric(table)

        ## -- SQL -- ##
        session.notes = "Notes"
        session.published = 0
        session.date = datetime.datetime.now()

        print("title:", session.title)
        print("servings:", session.servings)
        print("method:", session.method)
        print("author:", session.author)
        print("notes:", session.notes)
        print("published:", session.published)

        # Submit data to databse
        data = (
            (
                session.title, session.servings, session.method, session.author, session.notes, session.published
            )
        )

        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()

            # Drop recipe into recipe table (minus ingredients)
            cur.execute(
                "INSERT INTO recipes (title, serves, method, author, notes, published) VALUES (?, ?, ?, ?, ?, ?)",
                data)
            
            # Grab recipe_id
            session.recipe_id = cur.execute("SELECT last_insert_rowid()")
            session.recipe_id = int(cur.fetchone()[0])
            #print(recipe_id)
            
            for item in table:

                dataB = (
                    (
                        item['ingredient'], item['quantity'], item['unit'], session.recipe_id
                    )
                )
                cur.execute(
                "INSERT INTO ingredients_table (ingredient, quantity, unit, recipe_id) VALUES (?, ?, ?, ?)",
                dataB)


        #print(session.metricRequest)
        #return render_template('edit.html', table=table, recipe_id=session.recipe_id)

        redirectEdit = '/edit?id='
        redirectEdit += str(session.recipe_id)
        return redirect(redirectEdit)


@app.route("/check", methods=["GET", "POST"])
def confirm():

    if request.method == "POST":
        # submit data to databse
        session.dataC = ((
            request.form.get("recipe_id"),
        ))
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute(
                "UPDATE recipes SET published = 1 WHERE recipe_id = ?", session.dataC)

    return redirect('/')


@app.route("/delete", methods=["POST"])
def delete():

    recipe_id = request.form.get("deleteRecipe")
    con = sqlite3.connect('data.db')
    with con:
        cur = con.cursor()
        cur.execute(
                "DELETE FROM ingredients_table WHERE recipe_id = ?", (recipe_id,))
        cur.execute(
                "DELETE FROM recipes WHERE recipe_id = ?", (recipe_id,))

    return redirect('/profile')


@app.route("/edit_method", methods=["GET", "POST"])
def edit_method():
    
    if request.method == "GET":
        return render_template('/edit_method.html')

    if request.method == "POST": 
        recipe_id = request.form.get("edit_method")
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            method = cur.execute(
                    "SELECT method FROM recipes WHERE recipe_id = ?", (recipe_id,))
            method = cur.fetchone()
            placeholderText = method[0]

        return render_template('edit_method.html', placeholderText=placeholderText, recipe_id=recipe_id)



@app.route("/update_method", methods=["POST"])
def update_method():
    
    if request.method == "POST":
        
        session.recipe_id = request.form.get("editRecipe")
        method = request.form.get("method")

        # Update database
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            cur.execute(
                    "UPDATE recipes SET method = ? WHERE recipe_id = ?", (method, session.recipe_id))

        redirectEdit = '/edit?id='
        redirectEdit += str(session.recipe_id[0])
        return redirect(redirectEdit)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')

    if request.method == "POST":
        # Checks.
        if not request.form.get("username"):
            message = "Please provide a username."
            return render_template('register.html', message=message)

        if len(request.form.get("username")) < 6 or len(request.form.get("username")) > 30:
            message = "Username must be between 6-30 characters long."
            return render_template('register.html', message=message)

        if not request.form.get("password"):
            message = "Please provide a password."
            return render_template('register.html', message=message)

        if len(request.form.get("password")) < 8:
            message = "Password must be at least 8 characters long."
            return render_template('register.html', message=message)
        
        if not request.form.get("confirmation"):
            message = "Please confirm password."
            return render_template('register.html', message=message)

        if request.form.get("password") != request.form.get("confirmation"):
            message = "Passwords do not match. Please try again."
            return render_template('register.html', message=message)

        # Check if user already exists.
        username = request.form.get("username")
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            usernameCheck = cur.execute(
                    "SELECT * FROM users WHERE username = ?", (username,))
            usernameCheck = cur.fetchall()

            if len(usernameCheck) > 0:
                message = "Username already exists."
                return render_template('register.html', message=message)

            cur.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", 
                (username, generate_password_hash(request.form.get("password")))
            )


    return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            message = "Please provide a username."
            return render_template('register.html', message=message)

        # Ensure password was submitted
        elif not request.form.get("password"):
            message = "Please provide password."
            return render_template('register.html', message=message)

        # Query database for username
        con = sqlite3.connect('data.db')
        with con:
            cur = con.cursor()
            rows = cur.execute(
                    "SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
            rows = cur.fetchall()
    
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            message = "Invalid username and/or password."
            return render_template('login.html', message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        session["username"] = rows[0][1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")