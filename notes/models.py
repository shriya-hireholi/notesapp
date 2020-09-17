from notes import db, login_manager, app
from flask_login import UserMixin, current_user
from flask_seeder import Seeder, Faker, generator
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
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


class Notebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.relationship('Note', backref='Notebook', lazy=True)

    def __repr__(self):
        return self.name


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notebook = db.Column(
        db.Integer,
        db.ForeignKey('notebook.id'),
        nullable=False)
    title = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return self.title


class DemoSeeder(Seeder):

    def run():
        # print(current_user.id)
        # user_id = current_user.get_id()
        faker = Faker(
            cls=Note,
            init={
                "id": generator.Sequence(),
                "notebook": 1,
                "title": generator.Name(),
                "content": generator.String('hello how are you')
            }
        )

        # Create 5 users
        for note in faker.create(15):
            db.session.add(note)
        
        notebook = Faker(
            cls=Notebook,
            init={
                "id": generator.Sequence(),
                "name": generator.Name(),
                "user": 1
            }
        )

        # Create 5 users
        for ntbk in notebook.create(5):
            db.session.add(ntbk)
    run()
