import os
from flask import Flask, g, session
from flask.cli import load_dotenv
from controllers.book_controller import book
from controllers.delivery_controller import delivery
from controllers.payment_controller import payment
from controllers.purchase_controller import purchase
from controllers.user_controller import user
from models.user import User
from models.book import Book
from models.delivery import DeliveryProvider
from models.delivery_assignment import DeliveryAssignment
from models.payment import Payment
from models.purchase import Purchase

from extensions import db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

db.init_app(app)


@app.before_request
def load_user():
    if "_user_id" in session:
        user = User.query.filter_by(id=session["_user_id"]).first()
        g.current_user = {
            "id": user.id,
            "name": user.name,
            "is_authenticated": True,
        }
    else:
        g.current_user = {"name": "Invitado", "is_authenticated": False}


@app.context_processor
def inject_user():
    print(g.current_user)
    return {"current_user": g.current_user}


@app.context_processor
def inject_auth_uri():
    return {"ms1_auth_uri": os.getenv("MS1_AUTH_URI") or ""}


app.register_blueprint(book, url_prefix="/book")
app.register_blueprint(user)
app.register_blueprint(delivery)
app.register_blueprint(payment)
app.register_blueprint(purchase)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001)
