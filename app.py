import hashlib
from datetime import datetime

import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String, Text

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

CURRENCY_EUR = 978
CURRENCY_USD = 840
CURRENCY_RUB = 643
SHOP_ID = "5"
SECRET_KEY = "SecretKey01"
PAYWAY = "advcash_rub"


class Request(db.Model):
    __tablename__ = "requests"

    shop_order_id = Column(Integer, primary_key=True)
    currency = Column(Integer, nullable=False)
    amount = Column(String, nullable=False)
    submit_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"Requests({self.shop_order_id})"


Request.__table__.create(bind=db.engine, checkfirst=True)


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html", CURRENCY_EUR=CURRENCY_EUR, CURRENCY_USD=CURRENCY_USD, CURRENCY_RUB=CURRENCY_RUB
    )


@app.route("/", methods=["POST"])
def process_payment():
    user_request = Request(
        currency=int(request.form["currency"]),
        amount=f'{float(request.form["amount"]):.2f}',
        description=request.form["description"],
    )
    db.session.add(user_request)
    db.session.commit()
    if user_request.currency == str(CURRENCY_EUR):
        sign = f"{user_request.amount}:{user_request.currency}:{SHOP_ID}:{user_request.shop_order_id}{SECRET_KEY}"
        return render_template(
            "pay.html",
            amount=user_request.amount,
            currency=user_request.currency,
            hex_digest=hashlib.sha256(sign.encode("utf-8")).hexdigest(),
            shop_id=SHOP_ID,
            index=user_request.shop_order_id,
        )
    elif user_request.currency == str(CURRENCY_USD):
        payer_currency = user_request.currency
        sign = (
            f"{user_request.currency}:"
            f"{user_request.amount}:"
            f"{payer_currency}:"
            f"{SHOP_ID}:"
            f"{user_request.shop_order_id}{SECRET_KEY}"
        )
        data = {
            "description": user_request.description,
            "payer_currency": user_request.currency,
            "shop_amount": user_request.amount,
            "shop_currency": payer_currency,
            "shop_id": SHOP_ID,
            "shop_order_id": user_request.shop_order_id,
            "sign": hashlib.sha256(sign.encode("utf-8")).hexdigest(),
        }
        response = requests.post("https://core.piastrix.com/bill/create", json=data)
        url = response.json()['data']['url']
        return redirect(url)
    elif user_request.currency == str(CURRENCY_RUB):
        sign = (
            f"{user_request.amount}:{user_request.currency}:{PAYWAY}:{SHOP_ID}:{user_request.shop_order_id}{SECRET_KEY}"
        )
        data = {
            "amount": user_request.amount,
            "currency": user_request.currency,
            "payway": PAYWAY,
            "shop_id": SHOP_ID,
            "shop_order_id": user_request.shop_order_id,
            "sign": hashlib.sha256(sign.encode("utf-8")).hexdigest()
        }
        response = requests.post("https://core.piastrix.com/invoice/create", json=data)
        response_data = response.json()["data"]
        return render_template(
            "invoice.html", method=response_data["method"], action=response_data["url"], data=response_data["data"]
        )


if __name__ == "__main__":
    app.run(debug=True)
