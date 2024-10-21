import os
import datetime
from cs50 import SQL
from functools import wraps
db = SQL("sqlite:///finance.db")
id = 1
symbol = "NFLX"
own_check = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND stock_symbol = ?", id, symbol)
cash = (db.execute("SELECT cash FROM users WHERE id = ?", id))
current_stocks = db.execute("SELECT stock_symbol FROM portfolio WHERE user_id = ?", id)
for stock_symbol in current_stocks:
    print(stock_symbol["stock_symbol"])