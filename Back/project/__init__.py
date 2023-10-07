import json
from project.helper import *



# Start SQL
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///'+os.path.join(basedir, 'data.sqlite'), echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
# End Start SQL






    


# App Modifications
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "SECRKAIEPREVKFIED"
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit
# End App Modifications
UPLOAD_FOLDER = 'uploads'


# Creates Default books that come with the code along with an admin user
# username = admin, password = admin.
# if a user/books table already exist it does nothing
USEDEFAULTS = True


# Get the absolute path of the current directory (__init__.py directory)
current_directory = os.path.abspath(os.path.dirname(__file__))

# Define the relative path to the "Front/images" directory
relative_path = "..\\..\\Front\\images"  # Adjust the path based on your directory structure

# Join the current directory with the relative path to get the absolute path of "Front/images"
images_directory = os.path.join(current_directory, relative_path)

# Set the UPLOAD_FOLDER configuration
app.config['UPLOAD_FOLDER'] = images_directory




# Import Contacts Only After The Session Is Ready
from project.contacts.views import contacts
from project.users.models import User
from project.users.views import users
from project.books.models import Book
from project.books.views import books
app.register_blueprint(contacts)
app.register_blueprint(users)
app.register_blueprint(books)

Base.metadata.create_all(engine)

def init_default_books():
    books = [
        {"id": 1, "name": "1984", "author": "George Orwell", "release": "2018", "image": "1984.jpeg", "copies": 5},
        {"id": 2, "name": "A Brief History of Time", "author": "Stephen Hawking", "release": "2018", "image": "brief.jpeg", "copies": 5},
        {"id": 3, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "release": "2018", "image": "gatsby.jpeg", "copies": 5},
        {"id": 4, "name": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "release": "2018", "image": "harry.jpeg", "copies": 5},
        {"id": 5, "name": "To Kill a Mockingbird", "author": "Harper Lee", "release": "2018", "image": "tokillmocking.jpeg", "copies": 5},
    ]

    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query the book table
        books_in_db = session.query(Book).all()

        # If there are no books in the database, add the default books
        if not books_in_db:
            for book in books:
                session.add(Book(**book))
            session.commit()

        # Query the user table
        users_in_db = session.query(User).all()

        # If there are no users in the database, add the default user
        if not users_in_db:
            hashed_password = generate_password_hash("admin", method='sha256')
            user = User(username="admin", password=hashed_password,date="01/01/1910",gender="other", books = json.dumps([]), isAdmin=True)
            session.add(user)
            session.commit()
    except Exception as e:
        log_action(f"An error occured on default_books init: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()
if USEDEFAULTS:
        init_default_books()