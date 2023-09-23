import json
from helper import *
Base = declarative_base()


#Book Table (id (AUTO INCREMENT), name as a string, Author, image path, amount of copies defaults to 0 )
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    author = Column(String(100))
    release = Column(String(4))
    image = Column(String(100))
    copies = Column(Integer, default=0)

#User Table (id ( AUTO INCREMENT) , username as sa tring, hashed password, books ( json object ), isAdmin Bool)
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    books = Column(Text)
    isAdmin = Column(Boolean, default=False)

# Contact Form (id (AUTO INCREMENT), name, email, message(LONGTEXT))
class Contact(Base):
    __tablename__ = 'contactforms'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text)
    

engine = create_engine('sqlite:///library.db', echo=True)
Base.metadata.create_all(engine)
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpeg'}

# Creates Default books that come with the code along with an admin user
# username = admin, password = admin.
# if a user/books table already exist it does nothing
USEDEFAULTS = True


root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Construct the path to the "Front/images" directory
images_directory = os.path.join(root_directory, "Front", "images")

app.config['UPLOAD_FOLDER'] = images_directory
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit


Session = sessionmaker(bind=engine)

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
            user = User(username="admin", password=hashed_password, books = json.dumps([]), isAdmin=True)
            session.add(user)
            session.commit()
    except Exception as e:
        log_action(f"An error occured on default_books init: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()

# Returns all books to the client
@app.route("/books", methods=["GET"])
def getbooks():
    session = Session()
    try:
        books = session.query(Book).all()
        # Convert SQLAlchemy model objects to dictionaries
        books_dict_list = [{"id": book.id, "name": book.name, "author": book.author, "release": book.release, "image": book.image, "copies": book.copies} for book in books]
        return jsonify(books_dict_list)
    except Exception as e:
        log_action(f"An error occured on /books GET: {str(e)}","debug")
        return jsonify({}) # Return something even if fails to avoid client side errors too
    finally:
        # Close the session afterwards
        session.close() 
    


# Borrows a Book By its ID
@app.route("/books/borrow", methods=["POST"])
def borrow():
    data = request.get_json()
    book_id = data.get("id")
    book_name = data.get("name")
    boption = data.get("option")
    username = data.get("username")
    return_date_iso = data.get("returnDate")

    session = Session()

    theuser = session.query(User).filter_by(username=username).first()
    try:
        if not theuser:
            return jsonify({"success": False, "message": f"User Was Not Found Try Again Later"})

        if book_id is None or book_name is None or boption is None:
            return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
    
        book = session.query(Book).filter_by(id=book_id).first()

        if book is not None:
            if book.copies <= 0:
                return jsonify({"success": False, "message": f"Book {book_name} is out of copies, try again later."})

            # Check if the user already has this book
            theuser_books = json.loads(theuser.books)
            userbooks = session.query(Book).filter(Book.id.in_([book['id'] for book in theuser_books])).all()
            if book in userbooks:
                return jsonify({"success": False, "message": f"Error, You Already have this book, try again or contact us"})

            # Save the borrowed book to the user's JSON data
            theuser_books.append({"id": book.id, "name": book.name, "returndate": return_date_iso})

            book.copies -= 1
            theuser.books = json.dumps(theuser_books)
            session.commit()
            return jsonify({"success": True, "message": f"Borrowing {book_name} For {boption}", "returnDate": return_date_iso, "books": theuser_books})
        else:
            
            return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
    except Exception as e:
        log_action(f"An error occured on borrow POST: {str(e)}","debug")
    finally:
        # Close the session afterwards
        session.close()
        
def serialize_book(book):
    return {
        "id": book.id,
        "name": book.name,
        "returndate": book.author,
    }


# Return a book after borrowing it
@app.route("/books/returnbook", methods=["POST"])
def returnbook():
    data = request.get_json()
    #parameters sent by the client
    book_id = data.get("id")
    book_name = data.get("name")
    username = data.get("username")

    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query the user by username
        user = session.query(User).filter_by(username=username).first()

        # If the user doesn't exist in the system, return an error
        if not user:
            return jsonify({"success": False, "message": f"User Was Not Found Try Again Later"})

        # Query the book by ID
        book = session.query(Book).filter_by(id=book_id).first()

        if book:
            book.copies += 1  # Return The Book To The Library Count

            # Check if the user has the book
            user_books = json.loads(user.books)
            user_book = next((b for b in user_books if b['id'] == book_id), None)

            if user_book:

                user_books.remove(user_book)  # Remove The Book From user_books

                user.books = json.dumps(user_books)  # Update the user's books in the database

                session.commit()  # Commit the transaction
                return jsonify({"success": True, "message": f"Book {book_name} Returned Successfully", "books": user_books})
            else:
                return jsonify({"success": False, "message": f"Error, You Don't have this book, try again or contact us"})
        else:
            return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
    except Exception as e:
        log_action(f"An error occured on returnbook POST: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()
        

# Management - Admin Stuff

# Adds a New Book That all clients can see in the books section
@app.route("/addbook", methods=["PUT"])
def addbook():
    # Image wasn't sent
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image part"})

    file = request.files['image']
    bookName = request.form.get('name')
    releaseDate = request.form.get('release')
    copies = request.form.get('copies')
    author = request.form.get('author')
    session = Session()
    try:
        # one of the arguments wasn't met, stopping the process to avoid errors and returning a message to the client
        if bookName is None or releaseDate is None or copies is None or author is None:
            return jsonify({"success": False, "message": "One of the arguments is missing. Needed: (bookname, releasedate, copies, author)"})

        # book name already exists, preventing the operation to avoid duplicates and having images being overwritten
        if isbooknameused(bookName):
            return jsonify({"success": False, "message": f"Book Name: {bookName} Is Already Used"})

        # try and upload the image
        filename, errormsg = upload_image(file, bookName)

        if not filename:
            return jsonify({"success": False, "message": errormsg})  # Upload Failed, Returning an Error Message to the client

        new_book = Book(name=bookName, author=author, release=releaseDate, image=filename, copies=int(copies))

        # Save The New Book To database
        session.add(new_book)
        session.commit()
        return jsonify({"success": True, "message": f"Adding {bookName}, Release: {releaseDate}, Copies: {copies}, author: {author}"})
    except Exception as e:
        log_action(f"An error occured on addbook PUT: {str(e)}","debug")
        return jsonify({"success": False, "message": f"Couldn't Add the book, Try again later."})
    finally:
        # Close the session afterwards
        session.close()

    



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file,bookName):
    # Check if a file is uploaded
    if not file:
        return jsonify({"error": "No file part"})

    file = file

    # Check if the file has a valid extension
    if not allowed_file(file.filename):
        return False,"Invalid file extension. Only PNG files are allowed."

    # Check if the file size is within the limit
    if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
        return False,"File size exceeds the limit of 2 MB."
    
    file.seek(0)

    # If all checks pass, save the file to the upload folder
    if file:
        filename = secure_filename(f'{bookName}.{ALLOWED_EXTENSIONS}')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename,""


# Change the amount of copies a book has
@app.route("/modifybook", methods=["POST"])
def modifybook():
    data = request.get_json()
    bookid = data.get('id')
    copies = data.get("copies")

    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        if bookid is None or copies is None:
            return jsonify({"success": False, "message": f"Book ID or Copies is missing"})

        if not copies.strip().isdigit():
            return jsonify({"success": False, "message": f"Copies Must be a Number"})

        # Query the book by ID
        book = session.query(Book).filter_by(id=bookid).first()

        if book:
            book.copies = int(copies)
            session.commit()  # Commit the transaction
            return jsonify({"success": True, "message": f"Book {book.name} Copies Edited To: {copies}"})
        else:
            return jsonify({"success": False, "message": f"Book ID: {bookid} was not found"})
    except Exception as e:
        log_action(f"An error occurred on modifybook POST: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()
            


#Remove Book Function
@app.route("/removebook", methods=["DELETE"]) 
def removeBook():
    data = request.get_json()
    bookid = data.get("bookid")

    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query the book by ID
        book = session.query(Book).filter_by(id=bookid).first()

        if book:
            themessage = f"Book {bookid} - {book.name} was removed successfully, Refreshing Page."
            delete_image(book.image)  # Deleting the image to clear space
            session.delete(book)  # Removing from the database
            session.commit()  # Commit the transaction
            return jsonify({"success": True, "message": themessage})
        else:
            return jsonify({"success": False, "message": "Book Was not Found in the system"})
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()

def delete_image(filename):
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], f'{filename}.jpeg')  # Construct the full path to the image file
    
    if os.path.exists(image_path):
        os.remove(image_path)
        return True  # Image was deleted successfully
    else:
        return False  # Image does not exist

# gets all users and returns to the admin excluding passwords
@app.route("/usersapi",methods=["GET"])
def getusers():
    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query all users from the database
        users = session.query(User).all()

        # Create a list of users to send in the response
        sendusers = [{"userid": user.id, "username": user.username, "books": json.loads(user.books), "isadmin": user.isAdmin} for user in users]

        return jsonify({"success": True, "data": sendusers})
    except Exception as e:
        log_action(f"An error occurred on userapi GET: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()



#Deletes a User From users.json by his userID
@app.route("/usersapi", methods=["DELETE"])
def deleteuser():
    data = request.get_json()
    userid = data.get("userid")
    
    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Retrieve the user from the database by user ID
        user = session.query(User).filter_by(id=userid).first()

        if user:
            themessage = f"User {user.username} was removed successfully, Refreshing Page."
            
            userbooks = json.loads(user.books)
            if(len(userbooks) > 0):
                totalreturns = returnallbooks(userbooks)
                themessage = f"User {user.username} was removed successfully, Refreshing Page And Returning {totalreturns} Books."
            else:
                log_action("Not","debug")
            
            
            # Delete the user from the database
            session.delete(user)
            
            # Commit the changes to the database
            session.commit()
            
            
            return jsonify({"success": True, "message": themessage})
        
        return jsonify({"success": False, "message": "User Was Not Found In the system."})
    except Exception as e:
        log_action(f"An error occurred on usersapi DELETE: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()

# Returns All Book To Storage
def returnallbooks(books):
    session = Session()
    try:
        totalreturns = 0
        for book in books:
            book = session.query(Book).filter_by(id=book['id']).first()

            if book:
                totalreturns += 1
                book.copies += 1  # Return The Book To The Library Count
                session.commit()  # Commit the transaction

        return totalreturns
    except Exception as e:
        log_action(f"An error occurred on returnallbooks Failed To Return Books: {str(e)}","debug")
        return False
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()
        

# Toggles Librarian access to a user
@app.route("/usersapi/setPermissions", methods=["POST"])
def setPermissions():
    data = request.get_json()
    userid = data.get("userid")
    session = Session()
    # Retrieve the user from the database by user ID
    try: 
        user = session.query(User).filter_by(id=userid).first()
        
        if user:
            user.isAdmin = not user.isAdmin  # Toggle the isAdmin flag
            
            # Commit the changes to the database
            session.commit()
            if user.isAdmin:
                themessage = f"User {user.username}'s Admin Access was Added successfully, Refreshing Page."
            else:
                themessage = f"User {user.username}'s Admin Access was removed successfully, Refreshing Page."
            
            return jsonify({"success": True, "message": themessage})
    except Exception as e:
        log_action(f"An error occurred setpermissions: {str(e)}","debug")
    finally:
        session.close()

    return jsonify({"success": False, "message": "User Was Not Found In the system."})

# checks if the book name is under use
def isbooknameused(bookName):
    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query the database to check if the book name is already used
        book_exists = session.query(Book).filter_by(name=bookName).first()

        return book_exists is not None  # If a book with the given name exists, return True
    
    except Exception as e:
        log_action(f"An error occurred on isbooknameused: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()



# End Management





#Registration/login system
@app.route("/accounts", methods=["PUT"])
def register():
    data = request.get_json()
    uname = data.get('username')
    password = data.get("password")
    
    if not uname or not password:
        return jsonify({"success": False, "message": "Username or Password not Mentioned"})
    
    # Check if the username already exists in the database
    session = Session()
    try:
        
        existing_user = session.query(User).filter_by(username=uname).first()
        
        if existing_user:
            return jsonify({"success": False, "message": "Username is already taken"})
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Create a new user object and add it to the database
        new_user = User(username=uname, password=hashed_password, books = json.dumps([]), isAdmin=False)
        
        session.add(new_user)
        session.commit()
    except Exception as e:
        log_action(f"An error occurred on put accounts: {str(e)}","debug")
    finally:
        session.close()
    
    return jsonify({"success": True, "message": "Registration successful"})

@app.route("/accounts", methods=["POST"])
def login():
    data = request.get_json()
    uname = data.get('username')
    password = data.get("password")
    
    if not uname or not password:
        return jsonify({"success": False, "message": "Username or Password not Mentioned"})
    session = Session()
    try:
        # Retrieve the user from the database by username
        user = session.query(User).filter_by(username=uname).first()
        if not user:
            return jsonify({"success": False, "message": "Username not found"})
        
        # Check if the password is correct using check_password_hash
        if check_password_hash(user.password, password):
            return jsonify({"success": True, "user": {"userid": user.id, "username": user.username, "isAdmin": user.isAdmin, "books": json.loads(user.books)}})
        
        return jsonify({"success": False, "message": "Incorrect password"})
    except Exception as e:
        log_action(f"An error occurred on post accounts: {str(e)}","debug")
    finally:
        session.close()
#End registration system

#Contact Forms
@app.route('/contacts', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        session = Session()
        try:
            
            # one of the arguments wasn't met, stopping the process to avoid errors and returning a message to the client
            if name is None or email is None or message is None:
                return jsonify({"success": False, "message": "One of the arguments is missing. Needed: (name, email, message)"})
            
            if iscontactmailused(email):
                return jsonify({"success": False, "message": "You have already contacted us, we will look into your request as soon as possible."})

            new_form = Contact(name=name, email=email, message = message)
            log_action(f"Submitting: {name} {email} {message}","debug")
            session.add(new_form)
            log_action("Submitted","debug")
            session.commit()
            return jsonify({"success": True, "message": "Your Feedback was sent successfully"})
        except Exception as e:
            log_action(f"An error occurred on post contacts: {str(e)}","debug")
        finally:
            session.close()
    elif request.method == 'GET':
        session = Session()
        try:

            contacts = session.query(Contact).all()
            contacts_dict_list = [{"id": contact.id, "name": contact.name, "email": contact.email, "message": contact.message} for contact in contacts]
            return jsonify(contacts_dict_list)
        except Exception as e:
            log_action(f"An error occured on get contacts: {str(e)}","debug")
            return jsonify({}) # Return something even if fails to avoid client side errors too
        finally:
            session.close()

def iscontactmailused(email):
    # Create a new session using SQLAlchemy's sessionmaker
    session = Session()

    try:
        # Query the database to check if the book name is already used
        email_exists = session.query(Contact).filter_by(email=email).first()

        return email_exists is not None  # If a book with the given name exists, return True
    
    except Exception as e:
        log_action(f"An error occurred on iscontactmailused: {str(e)}","debug")
    finally:
        # Always close the session after use, even in case of exceptions
        session.close()

#End contact forms

if __name__ == "__main__":
    if USEDEFAULTS:
        init_default_books()
    app.run(debug=True, port=911)