from helper import *
from flask import Flask,request,jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

BOOKSFILE = "books.json"
FORCESAVE = False # TODO Get Rid of this
USERSFILE = "users.json"
users = []
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpeg'}



root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Construct the path to the "Front/images" directory
images_directory = os.path.join(root_directory, "Front", "images")

app.config['UPLOAD_FOLDER'] = images_directory
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit

#app.secret_key = 'your_secret_key_here'
CORS(app)
books = [
    {"id": 1, "name": "1984", "author": "George Orwell", "release": "2018", "image": "1984.jpeg", "copies": 5},
    {"id": 2, "name": "A Brief History of Time", "author": "Stephen Hawking", "release": "2018", "image": "brief.jpeg", "copies": 5},
    {"id": 3, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "release": "2018", "image": "gatsby.jpeg", "copies": 5},
    {"id": 4, "name": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "release": "2018", "image": "harry.jpeg", "copies": 5},
    {"id": 5, "name": "To Kill a Mockingbird", "author": "Harper Lee", "release": "2018", "image": "tokillmocking.jpeg", "copies": 5},
]

@app.route("/books", methods=["GET"])
def getbooks():
    return books # Get All Books



@app.route("/books/borrow", methods=["POST"])
def borrow():
    data = request.get_json()
    book_id = data.get("id")
    book_name = data.get("name")
    boption = data.get("option")
    theuser = FindUser(users,data.get("username"),"username")
    return_date_iso = data.get("returnDate")  # Get the return date as an ISO string

    # Parse the return date from ISO string to a Python datetime object
    if not theuser:
        return jsonify({"success": False, "message": f"User Was Not Found Try Again Later"})
    

    
    if(book_id is None or book_name is None or boption is None):
        return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
    
    book = FindBook(books,book_id,"id") # check if a book exists using books dict, the bookid, and telling the function we want to search by the key "id"
    if(book is not None):
        if(book['copies'] <= 0):
            return jsonify({"success": False, "message": f"Book {book_name} is out of copies, try again later."})
        
        # check if the client already has this book
        thebook = FindUserBook(theuser['books'],book_id)
        if thebook:
            return jsonify({"success": False, "message": f"Error, You Already have this book, try again or contact us"})

        book['copies'] -= 1 # Take 1 Book from the library Count
        theuser['books'].append({"id": book['id'], "name": book['name'], "returndate": return_date_iso}) # Add the book to the client's user with id, name, return date.
        save_books() # save boooks
        save_users() # save users
        return jsonify({"success": True, "message": f"Borrowing {book_name} For {boption}", "books": theuser['books']})
    else:
        return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})


@app.route("/books/returnbook", methods=["POST"])
def returnbook():
    data = request.get_json()
    book_id = data.get("id")
    book_name = data.get("name")
    theuser = FindUser(users,data.get("username"),"username")
    # user doesn't exist in the system, stopping.
    if not theuser:
        return jsonify({"success": False, "message": f"User Was Not Found Try Again Later"})
    
    book = FindBook(books,book_id,"id") # check if a book exists using books dict, the bookid, and telling the function we want to search by the key "id"
    if(book is not None):
        book['copies'] += 1 # Return The Book To The Library Count
        userbooks = theuser['books']
        thebook = FindUserBook(userbooks,book_id)
        if thebook is None:
            return jsonify({"success": False, "message": f"Error, You Don't have this book, try again or contact us","reloadbooks":userbooks})
        
        userbooks.remove(thebook) # Remove The Book From userbooks
        theuser['books'] = userbooks # Update the user's book in the entire users dict
        save_books() # Save Books
        save_users() # Save Users
        return jsonify({"success": True, "message": f"Book {book_name} Returned Successfully", "books": theuser['books']})
    else:
        return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
        

# Management
@app.route("/addbook", methods=["PUT"])  # Changed
def addbook():

    # Image wasn't sent
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image part"})

    file = request.files['image']
    bookName = request.form.get('name')
    releaseDate = request.form.get('release')
    copies = request.form.get('copies')
    author = request.form.get('author')
    
    

    # one of the arguments wasn't met, stopping the proccess to avoid errors and returning a message to the client
    if bookName is None or releaseDate is None or copies is None or author is None:
        return jsonify({"success": False, "message": f"One of the arguments is missing Needed: (bookname, releasedate, copies, author)"})

    # book name already exists, preventing operation to avoid duplicates and having images being overwritten
    if isbooknameused(bookName):
        return jsonify({"success": False, "message": f"Book Name: {bookName} Is Already Used"})
    
    # try and upload the image
    filename,errormsg = upload_image(file,bookName)

    if not filename: 
         return jsonify({"success": False, "message": errormsg}) # Upload Failed, Returning an Error Message to the client
        
    books.append({"id":len(books) + 1, "name": bookName, "author": author ,"release": releaseDate, "image": f'{filename}', "copies": int(copies)})
    
    save_books()
    return jsonify({"success": True, "message": f"Adding {bookName} ,Release:  {releaseDate}, Copies: {copies}, author: {author}"})


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

    if(bookid is None or copies is None):
        return jsonify({"success": False, "message": f"Book ID: {bookid} was not found"})
    
    if(not copies.strip().isdigit()):
        return jsonify({"success": False, "message": f"Copies Must be a Number"})
    
    book = FindBook(books,bookid,"id")
    if(book is None):
        return jsonify({"success": False, "message": f"Book ID: {bookid} was not found"})
    
    book['copies'] = int(copies)
    save_books()
    return jsonify({"success": True, "message": f"Book {book['name']} Copies Edited To: {copies}"})
            


#Remove Book Function
@app.route("/removebook", methods=["DELETE"]) 
def removeBook():    
    data = request.get_json()
    bookid = data.get("bookid")
    for book in books:
        if(book['id'] == bookid):
            themessage = f"Book {bookid} - {book['name']} was removed succesfully, Refreshing Page."
            delete_image(book['name']) # Deleting the image to clear space
            books.remove(book) # Removing from the dict
            save_books() # Saving
            return jsonify({"success" : True, "message": themessage})
        
    return jsonify({"success" : False, "message": "Book Was not Found in the system"})

def delete_image(filename):
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], f'{filename}.jpeg')  # Construct the full path to the image file
    
    if os.path.exists(image_path):
        os.remove(image_path)
        return True  # Image was deleted successfully
    else:
        return False  # Image does not exist

@app.route("/usersapi",methods=["GET"])
def getusers():
    sendusers = []

    # Send all users without their password
    for user in users:
        sendusers.append({"userid":user["userid"], "username": user['username'], "books":user['books'], "isadmin":user['isAdmin']})
        
    return jsonify({"success": True, "data": sendusers})


#Deletes a User From users.json by his userID
@app.route("/usersapi", methods=["DELETE"])
def deleteuser():    
    data = request.get_json()
    userid = data.get("userid")
    username = data.get("username")
    for user in users:
        if(user["userid"] == userid):
            themessage = f"Book {userid} - {username} was removed succesfully, Refreshing Page."
            users.remove(user)
            save_users()
            return jsonify({"success" : True, "message": themessage})
        
    return jsonify({"success" : False, "message": "User Was Not Found In the system."})


# Toggles Librarian access to a user
@app.route("/usersapi/setPermissions", methods=["POST"])
def setPermissions():    
    data = request.get_json()
    userid = data.get("userid")
    username = data.get("username")
    for user in users:
        if(user["userid"] == userid):
            if(user['isAdmin']):
                user['isAdmin'] = False
                themessage = f"Book {userid} - {username}'s Admin Access was removed succesfully, Refreshing Page."
            else:
                user['isAdmin'] = True
                themessage = f"Book {userid} - {username}'s Admin Access was Added succesfully, Refreshing Page."

            
            save_users()
            return jsonify({"success" : True, "message": themessage})
        
    return jsonify({"success" : False, "message": "User Was Not Found In the system."})

# checks if the book name is under use
def isbooknameused(bookName):
    for book in books:
        if book['name'] == bookName:
            return True

    return False

def save_books():
    save_json(BOOKSFILE,books)

def save_users():
    save_json(USERSFILE,users)
    

# End Management





#Registration/login system
@app.route("/accounts", methods=["PUT"])
def register():
    data = request.get_json()
    uname = data.get('username')
    password = data.get("password")
    if not uname or not password:
        return jsonify({"success": False, "message": "Username or Password not Mentioned"})
    for user in users:
        if uname == user["username"]:
            return jsonify({"success": False, "message": "user name is invalid"})
    
    userid = generate_id(users)
    users.append({"userid": userid, "username":uname, "password":password, "books": [], 'isAdmin':False})
    save_users()
    return jsonify({"success": True})

@app.route("/accounts", methods=["POST"])
def login():
    data = request.get_json()
    uname = data.get('username')
    password = data.get("password")
    found,loggedin = check_login(uname,password)
    if(found):
        return jsonify({"success": True, "user": loggedin})

            

    return jsonify({"success": False})


# Player tries to login, check the password and username he sent
def check_login(uname,password):
    if not uname or not password:
        return False # ERROR, Password or username weren't found, returning found == False
    
    for user in users:
        if(uname == user["username"]):
            if(password == user["password"]):
                return True,user # Found him, returning found == True and sending his user
            
    return False,False # User Doesn't Exist

if __name__ == "__main__":
    if(not FORCESAVE):
        books = load_json(BOOKSFILE)
    else:
        save_books()
    users = load_json(USERSFILE)
    app.run(debug=True, port=911)