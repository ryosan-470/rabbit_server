from sqlalchemy.orm import synonym, relationship
from werkzeug import check_password_hash, generate_password_hash

from rabbit_server import db


class UserInfo(db.Model):
    """
    CRATE TABLE user_info (
        id primary_key unique integer,
        name text,
        mail text,
        hashed_password text,
        score integer
    )
    """
    __tablename__ = "user_info"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='', nullable=False)
    mail = db.Column(db.String(100), default='', nullable=False)
    score = db.Column(db.Integer, default=0)
    _password = db.Column('password', db.String(100), nullable=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)
    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, name, password):
        user = query(cls).filter(cls.name == name).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return "<User id={id} name={name} mail={mail} score={score} pts".format(
            id=str(self.id), name=self.name, mail=self.mail,
            score=str(self.score))


class ProblemTable(db.Model):
    """
    CREATE TABLE problem (
        problem_id integer primary_key,
        point integer,
        type text, # 問題カテゴリ
        title text,
        body text,
        hint text,
        flag text  # hashed
        is_public boolean  # 公開フラグ
    )
    """
    __tablename__ = "problem"

    problem_id = db.Column(db.Integer, primary_key=True)
    point = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(32), default='', nullable=False)
    title = db.Column(db.String(100), default='', nullable=False)
    body = db.Column(db.Text)
    hint = db.Column(db.Text)
    flag = db.Column(db.String(200), default='', nullable=False)
    is_public = db.Column(db.Boolean(False))

    def __init__(self, point, type, title, body, hint, flag, is_public):
        self.point = point
        self.type = type
        self.title = title
        self.body = body
        self.hint = hint
        self.flag = flag
        self.is_public = is_public

    def __repr__(self):
        return """
        Problem_ID: {id}, Point: {point}, type: {type}, TITLE:{title}
        FLAG:{flag} PUBLIC? {is_public}
        """.format(id=str(self.problem_id), point=str(self.point),
                   type=self.type, title=self.title, flag=self.flag,
                   is_public=self.is_public)


class ScoreTable(db.Model):
    """
    CREATE TABLE score (
        id integer primary_key,
        user_id integer,
        problem_id integer,
        solved bool,
        solved_time text
    )
    """
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.problem_id'))
    solved = db.Column(db.Boolean(False))
    solved_time = db.Column(db.DateTime())

    user = relationship("UserInfo")
    problem = relationship("ProblemTable")

    def __init__(self, user_id, problem_id, solved, solved_time):
        self.user_id = user_id
        self.problem_id = problem_id
        self.solved = solved
        self.solved_time = solved_time

    def __repr__(self):
        return """
        user_id = {user_id} problem_id = {problem_id}
        solved = {solved}
        """.format(user_id=str(self.user_id), problem_id=str(self.problem_id),
                   solved=self.solved)


class WrongAnswerTable(db.Model):
    """
    CREATE TABLE wa_table (
        id integer primary_key,
        user_id integer,
        problem_id integer,
        wa string
        date
    )
    """
    __tablename__ = "wa_table"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.problem_id'))
    wa = db.Column(db.String(100))
    date = db.Column(db.DateTime())

    user = relationship("UserInfo")
    problem = relationship("ProblemTable")

    def __init__(self, user_id, problem_id, wa, date):
        self.user_id = user_id
        self.problem_id = problem_id
        self.wa = wa
        self.date = date

    def __repr__(self):
        return """
        user_id = {user_id} problem_id = {problem_id}
        wrong_answer = {wa}
        """.format(user_id=str(self.user_id), problem_id=str(self.problem_id),
                   wa=self.wa)


class NoticeTable(db.Model):
    """
    Adminから競技者へお知らせ

    CREATE TABLE notice (
        id integer primary_key,
        title string
        body string
        date
    )
    """
    __tablename__ = "notice"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)

    def __init__(self, title, body, date):
        self.title = title
        self.body = body
        self.date = date

    def __repr__(self):
        return """
        TITLE:{title}
        {body}
        Updated:{date}""".format(
            title=self.title, body=self.body, date=self.date)

    # TO DICT
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'date': self.date
        }


class Config(db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value


    def __repr__(self):
        return "[ {key}:{value} ]".format(key=self.key, value=self.value)


def init():
    db.create_all()
