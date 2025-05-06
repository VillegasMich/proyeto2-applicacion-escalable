from flask import Blueprint, render_template, request, redirect, url_for, g
from models.book import Book
import os

from extensions import db

# from app import db

book = Blueprint("book", __name__)


@book.route("/catalog")
def catalog():
    books = Book.query.all()
    return render_template("catalog.html", books=books)


@book.route("/my_books")
def my_books():
    if not (g.current_user["is_authenticated"]):
        return redirect((os.getenv("MS1_AUTH_URI") or "") + "/login")
    books = Book.query.filter_by(seller_id=g.current_user["id"]).all()
    return render_template("my_books.html", books=books)


@book.route("/add_book", methods=["GET", "POST"])
def add_book():
    if not (g.current_user["is_authenticated"]):
        return redirect((os.getenv("MS1_AUTH_URI") or "") + "/login")
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        stock = int(request.form.get("stock"))
        new_book = Book(
            title=title,
            author=author,
            description=description,
            price=price,
            stock=stock,
            seller_id=g.current_user["id"],
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("book.catalog"))
    return render_template("add_book.html")


@book.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if not (g.current_user["is_authenticated"]):
        return redirect((os.getenv("MS1_AUTH_URI") or "") + "/login")
    book_to_edit = Book.query.get_or_404(book_id)
    if book_to_edit.seller_id != g.current_user["id"]:
        return "No tienes permiso para editar este libro.", 403

    if request.method == "POST":
        book_to_edit.title = request.form.get("title")
        book_to_edit.author = request.form.get("author")
        book_to_edit.description = request.form.get("description")
        book_to_edit.price = float(request.form.get("price"))
        book_to_edit.stock = int(request.form.get("stock"))
        db.session.commit()
        return redirect(url_for("book.catalog"))

    return render_template("edit_book.html", book=book_to_edit)


@book.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if not (g.current_user["is_authenticated"]):
        return redirect((os.getenv("MS1_AUTH_URI") or "") + "/login")
    book_to_delete = Book.query.get_or_404(book_id)
    if book_to_delete.seller_id != g.current_user["id"]:
        return "No tienes permiso para eliminar este libro.", 403

    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("book.catalog"))
