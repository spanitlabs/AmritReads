from datetime import datetime
from book_review import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Table: Admin
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Admin(Email: {self.email})"

# Table: Book
class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # String fields
    book_title = db.Column(db.String(120), unique=True, nullable=False)
    title_slug = db.Column(db.String(100), unique=True, nullable=False)
    author_name = db.Column(db.String(80), nullable=False)
    shop_link = db.Column(db.String(100), nullable=True)
    genre = db.Column(db.String(30), nullable=True)
    cover_image_file = db.Column(db.String(50), nullable=False, default="default.jpeg")

    # Text Fields
    tiny_summary = db.Column(db.Text, nullable=True)
    review_content = db.Column(db.Text, nullable=True)
    review_content_draft = db.Column(db.Text, nullable=True)

    # Integer Fields
    isbn = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    # Others
    date_edited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship("Comment", backref="book", lazy=True)

    def __repr__(self):
        return f"Book(Title: '{self.book_title}', Author: '{self.author_name}', Cover Image: '{self.cover_image_file}', ISBN Number: '{self.isbn}')"

# Table: Comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False, default="Anonymous")
    comment_text = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Comment(email: '{self.email}', comment_text: '{self.comment_text}', book_id: '{self.book_id}', mod_verified: '{self.mod_verified}')"
