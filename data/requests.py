import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Request(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.schema.ForeignKey('users.tg_id'))
    user = sqlalchemy.orm.relationship('User')
