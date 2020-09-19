from notes import db, login_manager, app
from flask_login import UserMixin
from flask_seeder import Seeder, Faker, generator
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from notes.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(70), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    notebooks = db.relationship('Notebook', backref='Users', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return self.name


class Notebook(SearchableMixin, db.Model):
    __tablename__ = 'notebook'
    __searchable__ = ['id', 'name', 'user']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.relationship('Note', backref='Notebook', lazy=True)

    def __repr__(self):
        return self.name


class Note(SearchableMixin, db.Model):
    __tablename__ = 'note'
    __searchable__ = ['id', 'notebook', 'title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    notebook = db.Column(
        db.Integer,
        db.ForeignKey('notebook.id'),
        nullable=False)
    title = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return self.title


# class DemoSeeder(Seeder):

#     def run():
#         # print(current_user.id)
#         # user_id = current_user.get_id()
#         faker = Faker(
#             cls=Note,
#             init={
#                 "id": generator.Sequence(),
#                 "notebook": 1,
#                 "title": generator.Name(),
#                 "content": generator.String('hello how are you')
#             }
#         )

#         # Create 5 users
#         for note in faker.create(15):
#             db.session.add(note)
        
#         notebook = Faker(
#             cls=Notebook,
#             init={
#                 "id": generator.Sequence(),
#                 "name": generator.Name(),
#                 "user": 1
#             }
#         )

#         # Create 5 users
#         for ntbk in notebook.create(5):
#             db.session.add(ntbk)
#     run()
