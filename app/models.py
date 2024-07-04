from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model): #user model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    entries = db.relationship('JournalEntry', backref='author', lazy='dynamic') #one-to-many relationship with JournalEntry

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) #hash the password before storing

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) # verify hashed password

class JournalEntry(db.Model): #journal entry model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #foreign key to link to User