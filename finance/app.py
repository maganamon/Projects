import os
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


def is_positive_integer(n):
    return n % 1 == 0 and n > 0


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # weird bug where session["user_id"] switches from a list to an int. So this is how I solved that.
    if type(session["user_id"]) == int:
        id = session["user_id"]
    else:
        user_id = session["user_id"]
        id = user_id[0]["id"]
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", id)
    current_stocks = db.execute("SELECT stock_symbol FROM portfolio WHERE user_id = ?", id)
    cash = (db.execute("SELECT cash FROM users WHERE id = ?", id)[0]["cash"])
    prices = {}
    vtotal = 0
    # loop through to find current prices of each stock and update into prices dict
    for stock_symbol in current_stocks:
        temp = {}
        symbol = stock_symbol["stock_symbol"]
        new = lookup(symbol)
        price = new.get("price")
        temp.update({symbol: price})
        prices.update(temp)
    for row in portfolio:
        vtotal = vtotal + (row["stock_quantity"]) * (prices[row["stock_symbol"]])
    truetotal = cash + vtotal
    return render_template("index.html", portfolio=portfolio, prices=prices, cash=cash, truetotal=truetotal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # get the ID of user in current session
    if type(session["user_id"]) == int:
        id = session["user_id"]
    else:
        user_id = session["user_id"]
        id = user_id[0]["id"]
        print(request.form.get("shares"))
    # check how much money they have
    cash = float(db.execute("SELECT cash FROM users WHERE id = ?", id)[0]["cash"])
    # if get render temp.
    if request.method == "GET":
        return render_template("buylook.html")
    # Make sure user doesn't leave input fields empty
    elif not request.form.get("symbol") or not (request.form.get("shares")):
        return apology("Missing Input :(", 403)
    # Check that user inputed a valid symbol
    elif ((lookup(request.form.get("symbol")) == None)):
        return apology("Invalid Symbol")
    elif is_number((request.form.get("shares"))) == False:
        return apology("You can't buy letters. Silly Goose.")
    elif (float(request.form.get("shares"))) <= 0:
        return apology("You can't buy 0 or Negative stocks. Sorry.")
    elif is_positive_integer(float(request.form.get("shares"))) == False:
        return apology("You can only buy whole stocks.")
    # Check that user has enough money to buy stock(s)
    if request.method == "POST":
        temp_share = request.form.get("shares")
        temp_price = (lookup(request.form.get("symbol")).get("price"))
    if (cash < ((float(temp_share)) * (float(temp_price)))):
        return apology("Insufficient Funds. Not enough money.", 403)
    else:
        stock_amount = float(request.form.get("shares"))
        symbol_3 = lookup(request.form.get("symbol"))
        symbol = symbol_3.get("symbol")
        company = symbol_3.get("name")
        stock_price = symbol_3.get("price")
        total_cost = (stock_amount * stock_price)
        # Get the current time
        now = datetime.datetime.now()
        # Format the time as a string in the SQL TIMESTAMP format
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        # change users cash amount to reflect buy
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, id)
        # check if user owns the stock to INSERT a new row.
        own_check = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND stock_symbol = ?", id, symbol)
        if not own_check:
            db.execute("INSERT INTO portfolio (user_id, stock_symbol, stock_quantity, company) VALUES (?, ?, ?, ?)",
                       id, symbol, stock_amount, company)
        # if user already owns stock. UPDATE
        else:
            db.execute("UPDATE portfolio SET stock_quantity = stock_quantity + ? WHERE user_id = ? AND stock_symbol = ?",
                       stock_amount, id, symbol)
        # INSERT into Transaction
        db.execute("INSERT INTO transactions (user_id, stock_symbol, stock_quantity, transaction_type, transaction_time, amount) VALUES (?, ?, ?, ?, ?, ?)",
                   id, symbol, stock_amount, "buy", timestamp, total_cost)
        return redirect("/"), flash("Stock successfully bought!")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    if type(session["user_id"]) == int:
        id = session["user_id"]
    else:
        user_id = session["user_id"]
        id = user_id[0]["id"]
    history = db.execute("SELECT * FROM transactions WHERE user_id = ?", id)
    prices = {}
    for stock_symbol in history:
        temp = {}
        symbol = stock_symbol["stock_symbol"]
        new = lookup(symbol)
        price = new.get("price")
        temp.update({symbol: price})
        prices.update(temp)
    return render_template("history.html", history=history, prices=prices)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("lookup.html")
    elif not request.form.get("symbol"):
        return apology("You input nothing :(", 400)
    elif (lookup(request.form.get("symbol")) == None):
        return apology("Sorry, That stock symbol doesn't exist", 400)
    else:
        symbol = request.form.get("symbol")
        info = lookup(symbol)
        return render_template("info.html", info=info)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif (not request.form.get("username") or not request.form.get("password")):
        return apology("Whoops, looks like you didn't fill something out.", 400)
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
    if (len(rows) != 0):
        return apology("Username already taken.", 400)
    elif (request.form.get("password") != request.form.get("confirmation")):
        return apology("The passwords didn't match. Try Again.", 400)
    else:
        password = request.form.get("password")
        username = request.form.get("username")
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        uid = db.execute("SELECT id FROM users WHERE (username = ?) AND (hash = ?)", username, hash)
        session["user_id"] = uid
        return redirect("/"), flash("Registered!")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # get user id
    if type(session["user_id"]) == int:
        id = session["user_id"]
    else:
        user_id = session["user_id"]
        id = user_id[0]["id"]
    # db search to get their current stocks to put into 'stocklist' later
    current_stocks = db.execute("SELECT stock_symbol FROM portfolio WHERE user_id = ?", id)
    # find how much cash the user has in account
    cash = float((db.execute("SELECT cash FROM users WHERE id = ?", id)[0]["cash"]))
    # a dictionary of stock users stock prices
    prices = {}
    # list of users current owned stocks for protection against selling unowned stocks
    stocklist = [stock["stock_symbol"] for stock in current_stocks]
    for stock_symbol in current_stocks:
        temp = {}
        symbol = stock_symbol["stock_symbol"]
        new = lookup(symbol)
        price = new.get("price")
        temp.update({symbol: price})
        prices.update(temp)
    # render template if Method is GET
    if request.method == "GET":
        return render_template("sell.html", current_stocks=current_stocks)
    # if Method is POST, make variables
    if request.method == "POST":
        if request.form.get("symbol") not in stocklist:
            return apology("You tried to sell a stock you don't own.")
        elif is_number((request.form.get("shares"))) == False:
            return apology("You can't sell letters. Silly Goose.")
        stock_sell = request.form.get("symbol")
        float_stock_amt = float(request.form.get("shares"))
        get_user_amount = db.execute("SELECT stock_quantity FROM portfolio WHERE stock_symbol = ? AND user_ID = ? ", stock_sell, id)
        user_amount = get_user_amount[0]["stock_quantity"]
        sellstock = lookup(stock_sell)
        price = sellstock.get("price")
        total = float_stock_amt * price
    if float_stock_amt <= 0:
        return apology("You can't sell 0 or Negative stocks. Sorry.")
    elif float_stock_amt > user_amount:
        return apology("You tried to sell more stocks than you own.")
    else:
        # Get the current time
        now = datetime.datetime.now()
        # Format the time as a string in the SQL TIMESTAMP format
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("UPDATE portfolio SET stock_quantity = stock_quantity - ? WHERE user_id = ? AND stock_symbol = ?",
                   float_stock_amt, id, stock_sell)
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total, id)
        db.execute("INSERT INTO transactions (user_id, stock_symbol, stock_quantity, transaction_type, transaction_time, amount) VALUES (?, ?, ?, ?, ?, ?)",
                   id, stock_sell, float_stock_amt, "sell", timestamp, total)
        last_check = db.execute("SELECT stock_quantity FROM portfolio WHERE stock_symbol = ? AND user_ID = ? ", stock_sell, id)
        zero_check = last_check[0]["stock_quantity"]
        if zero_check == 0:
            db.execute("DELETE FROM portfolio WHERE stock_symbol = ? AND user_ID = ? ", stock_sell, id)
        return redirect("/"), flash("Successfully Sold!")
