import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    reg_data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    count_of_used_b = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    count_of_r = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    addresses = sqlalchemy.relationship('Address', backref='user')
