import os
from slugify import slugify
from werkzeug.utils import secure_filename
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    abort,
    send_from_directory,
)
from flask_login import login_user, logout_user, current_user, login_required
from book_review import app, db, bcrypt, pagedown
from book_review.models import Admin, Book
from book_review.forms import LoginForm, BookForm, AdminForm, ReviewForm

# home page
@app.route("/", methods=["GET"])
def home():
    page = request.args.get("page", default=1, type=int)
    books = Book.query.paginate(page=page, per_page=8)
    return render_template("home.html", books=books, title="Home", curr_page=page)


# about page
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html", title="About")


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "success")
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            flash("Login successful", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        flash("login unsucessful", "danger")
    return render_template("login.html", form=form, title="Login as Administrator")


# logout
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# add book
@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = BookForm()

    if form.validate_on_submit():
        f = form.cover_image_file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.instance_path, "uploads", filename))
        book = Book(
            book_title=form.book_title.data,
            title_slug=slugify(form.book_title.data),
            author_name=form.author_name.data,
            cover_image_file=filename if filename else "default.jpeg",
            isbn=form.isbn.data,
            genre=form.genre.data,
            tiny_summary=form.tiny_summary.data,
        )
        try:
            db.session.add(book)
            db.session.commit()
        except:
            flash("Something went wrong while adding book to the database.", "danger")
            return render_template("add_book.html", form=form)

        flash("book successfully added to the database", "success")
        return redirect(url_for("home"))

    return render_template("add_book.html", form=form, title="Add Book")


@app.route("/add_admin", methods=["GET", "POST"])
@login_required
def add_admin():
    form = AdminForm()

    if form.validate_on_submit():
        admin_user = Admin(
            email=form.email.data,
            password=bcrypt.generate_password_hash(form.password.data).decode("utf-8"),
        )
        try:
            db.session.add(admin_user)
            db.session.commit()
            flash(
                f"Successfully registered new admin with: {form.email.data}", "success"
            )
        except:
            flash("Some error occurred", "danger")

    return render_template("add_admin.html", form=form, title="Add new admin")


# book page
@app.route("/book/<book_slug>")
def book(book_slug):
    book = Book.query.filter_by(title_slug=book_slug).first()
    return render_template("book.html", book=book, title=book.book_title)


@app.route("/genre/<name>")
def genre(name):
    return redirect(url_for("home"))


# edit book page
@app.route("/book/<book_slug>/edit", methods=["GET", "POST"])
@login_required
def edit_book(book_slug):
    book = Book.query.filter_by(title_slug=book_slug).first()

    if not book:
        abort(403)

    form = BookForm()

    if form.validate_on_submit():
        book.book_title = form.book_title.data
        book.author_name = form.author_name.data
        book.isbn = form.isbn.data
        book.tiny_summary = form.tiny_summary.data
        if form.cover_image_file.data:
            book.cover_image_file = form.cover_image_file.data
        try:
            db.session.commit()
        except:
            flash("Something went wrong while adding book to the database.", "danger")
            return render_template(
                "add_book.html", title=f"Edit {book.book_title}", form=form
            )
        flash("The book was updated!", "success")
        return redirect(url_for("book", book_slug=book.title_slug))
    elif request.method == "GET":
        form.book_title.data = book.book_title
        form.author_name.data = book.author_name
        form.isbn.data = book.isbn
        form.tiny_summary.data = book.tiny_summary

    return render_template(
        "add_book.html", title=f"Edit {book.book_title}", form=form, book=book
    )


# delete book
@app.route("/book/<book_slug>/delete", methods=["POST"])
@login_required
def delete_book(book_slug):
    book = Book.query.filter_by(title_slug=book_slug).first()

    if not book:
        abort(403)
    try:
        db.session.delete(book)
        db.session.commit()
        if book.cover_image_file != "default.jpg":
            os.remove(os.path.join(app.instance_path, "uploads", book.cover_image_file))
    except:
        flash(f"Something went wrong!", "danger")
        return redirect(url_for("edit_book", book_slug=book_slug))
    flash(f"Alright, {book.book_title} was successfully deleted", "success")
    return redirect(url_for("home"))


# review page
@app.route("/book/<book_slug>/write_review", methods=["GET", "POST"])
@login_required
def write_review(book_slug):
    form = ReviewForm()
    return render_template("write_review.html", form=form, title="Write Review")


# send image file
@app.route("/uploads/<filename>")
def send_image_file(filename):
    return send_from_directory(os.path.join(app.instance_path, "uploads"), filename)
