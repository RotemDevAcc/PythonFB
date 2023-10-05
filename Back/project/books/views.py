from project.helper import *
from project import Base, Session,app
from flask import Blueprint
import json
from project.books.models import Book
from project.users.models import User
ALLOWED_EXTENSIONS = {'jpeg'}

books = Blueprint('books', __name__,url_prefix='/books')
# Returns all books to the client
@books.route("/", methods=["GET"])
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
@books.route("/borrow", methods=["POST"])
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
        

# Return a book after borrowing it
@books.route("/returnbook", methods=["POST"])
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
@books.route("/managebook", methods=["PUT"])
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
@books.route("/managebook", methods=["POST"])
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
@books.route("/managebook", methods=["DELETE"]) 
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

