from server.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))

    mt5_login = db.Column(db.String(50))
    mt5_password = db.Column(db.String(100))
    mt5_server = db.Column(db.String(50))

    bot_running = db.Column(db.Boolean, default=False)


class TradeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    symbol = db.Column(db.String(10))
    action = db.Column(db.String(10))
    result = db.Column(db.String(20))
