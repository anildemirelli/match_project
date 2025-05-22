from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'player_database'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    ad_soyad = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))

    mevki1 = db.Column(db.String(50))
    mevki2 = db.Column(db.String(50))
    mevki3 = db.Column(db.String(50))

    defance = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    overall = db.Column(db.Integer)

    sabit_mevki = db.Column(db.String(50))
    type = db.Column(db.String(50))
    tercih_side = db.Column(db.String(10), nullable=True)