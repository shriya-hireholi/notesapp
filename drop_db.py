from notes import username, password
from sqlalchemy_utils import drop_database


drop_database(f'postgresql://{username}:{password}@localhost/toyproject')
