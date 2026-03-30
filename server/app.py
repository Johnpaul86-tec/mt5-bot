from flask import Flask, render_template, request, redirect, session, jsonify
from server.database import init_db, db
from server.models import User, TradeLog
from server.auth import hash_password, verify_password
from server.strategy import generate_signal, connect_mt5
from functools import wraps
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

# ---------- INIT ----------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallbacksecret")

init_db(app)


# ================= LOG VIEW ================= #
@app.route("/logs")
def logs():
    log_content = ""

    if os.path.exists("bot.log"):
        with open("bot.log", "r") as f:
            log_content = f.read()

    return render_template("logs.html", logs=log_content)


# ---------- LOGIN REQUIRED ----------
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return func(*args, **kwargs)

    return wrapper


# ---------- HOME ----------
@app.route("/")
def home():
    return redirect("/login")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]

        if User.query.filter_by(username=username).first():
            return "Username already exists"

        user = User(username=username, password=hash_password(request.form["password"]))
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if not user:
            return "User not found"

        if not verify_password(request.form["password"], user.password):
            return "Wrong password"

        session["user_id"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")


# ---------- PROFILE ----------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        user.mt5_login = request.form["mt5_login"]
        user.mt5_password = request.form["mt5_password"]
        user.mt5_server = request.form["mt5_server"]

        db.session.commit()
        return redirect("/dashboard")

    return render_template("profile.html", user=user)


# ---------- DASHBOARD ----------
@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])

    trades = TradeLog.query.filter_by(user_id=user.id).all()

    wins = len([t for t in trades if t.result == "WIN"])
    losses = len([t for t in trades if t.result == "LOSS"])

    balance = 0
    if user.mt5_login:
        try:
            connect_mt5(int(user.mt5_login), user.mt5_password, user.mt5_server)
            account = mt5.account_info()
            if account:
                balance = account.balance
        except:
            balance = "Error"

    return render_template(
        "dashboard.html",
        user=user,
        balance=balance,
        trades=trades,
        wins=wins,
        losses=losses,
    )


# ---------- START BOT ----------
@app.route("/start_bot")
@login_required
def start_bot():
    user = User.query.get(session["user_id"])

    if not user.mt5_login:
        return redirect("/profile")

    try:
        login_int = int(user.mt5_login)
    except:
        return "Invalid MT5 login"

    if not connect_mt5(login_int, user.mt5_password, user.mt5_server):
        return "MT5 connection failed"

    user.bot_running = True
    db.session.commit()

    return redirect("/dashboard")


# ---------- STOP BOT ----------
@app.route("/stop_bot")
@login_required
def stop_bot():
    user = User.query.get(session["user_id"])
    user.bot_running = False
    db.session.commit()
    return redirect("/dashboard")


# ---------- SIGNAL API ----------
@app.route("/api/signal")
@login_required
def signal():
    return jsonify({"signal": generate_signal("EURUSD")})


# ---------- TRADE EXECUTION (RISK 1:3) ----------
@app.route("/execute_trade")
@login_required
def execute_trade():
    user = User.query.get(session["user_id"])

    signal = generate_signal("EURUSD")

    if signal == "HOLD":
        return redirect("/dashboard")

    price = mt5.symbol_info_tick("EURUSD").ask

    sl = price - 0.0010
    tp = price + 0.0030  # 1:3 RR

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "EURUSD",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "Bot Trade",
    }

    result = mt5.order_send(request)

    trade = TradeLog(user_id=user.id, symbol="EURUSD", action=signal, result="OPEN")

    db.session.add(trade)
    db.session.commit()

    return redirect("/dashboard")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
