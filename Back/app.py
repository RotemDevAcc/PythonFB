from helper import *
from flask import Flask,request,jsonify
from flask_cors import CORS
from datetime import datetime

BOOKSFILE = "books.json"
FORCESAVE = False # TODO Get Rid of this
USERSFILE = "users.json"
users = []
app = Flask(__name__)
#app.secret_key = 'your_secret_key_here'
CORS(app)
books = [
    {"id": 1, "name": "1984", "author": "George Orwell", "release": "2018", "image": "images/1984.jpeg", "status": True, "return_date": None, "copies": 5},
    {"id": 2, "name": "A Brief History of Time", "author": "Stephen Hawking", "release": "2018", "image": "images/brief.jpeg", "status": True, "return_date": None, "copies": 5},
    {"id": 3, "name": "The Great Gatsby", "author": "F. Scott Fitzgerald", "release": "2018", "image": "images/gatsby.jpeg", "status": True, "return_date": None, "copies": 5},
    {"id": 4, "name": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "release": "2018", "image": "images/harry.jpeg", "status": True, "return_date": None, "copies": 5},
    {"id": 5, "name": "To Kill a Mockingbird", "author": "Harper Lee", "release": "2018", "image": "images/tokillmocking.jpeg", "status": True, "return_date": None, "copies": 5},
]

@app.route("/getbooks")
def getbooks():
    return books



@app.route("/borrow", methods=["POST"])
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
    
    book = FindBook(books,book_id,"id")
    if(book is not None):
        if(book['copies'] <= 0):
            return jsonify({"success": False, "message": f"Book {book_name} is out of copies, try again later."})
        
        book['copies'] -= 1
        theuser['books'].append({"id": book['id'], "name": book['name'], "returndate": return_date_iso})
        save_books()
        save_users()
        return jsonify({"success": True, "message": f"Borrowing {book_name} For {boption}", "books": theuser['books']})
    else:
        return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})


@app.route("/returnbook", methods=["POST"])
def returnbook():
    data = request.get_json()
    book_id = data.get("id")
    book_name = data.get("name")
    theuser = FindUser(users,data.get("username"),"username")
    
    if not theuser:
        return jsonify({"success": False, "message": f"User Was Not Found Try Again Later"})
    
    book = FindBook(books,book_id,"id")
    if(book is not None):
        book['copies'] += 1
        userbooks = theuser['books']
        thebook = FindUserBook(userbooks,book_id)
        if thebook is None:
            return jsonify({"success": False, "message": f"Error, You Don't have this book, try again or contact us","reloadbooks":userbooks})
        
        userbooks.remove(thebook)
        theuser['books'] = userbooks
        save_books()
        save_users()
        return jsonify({"success": True, "message": f"Book {book_name} Returned Successfully", "books": theuser['books']})
    else:
        return jsonify({"success": False, "message": f"Book Was Not Found Try Again Later"})
        

# Management
@app.route("/addbook", methods=["POST"])
def addbook():
    data = request.get_json()
    bookName = data.get('name')
    releaseDate = data.get("release")
    copies = data.get("copies")
    author = data.get("author")


    if bookName is None or releaseDate is None or copies is None or author is None:
        return jsonify({"success": False, "message": f"One of the arguments is missing Needed: (bookname, releasedate, copies, author)"})

    if isbooknameused(bookName):
        return jsonify({"success": False, "message": f"Book Name: {bookName} Is Already Used"})
    books.append({"id":len(books) + 1, "name": bookName, "author": author ,"release": releaseDate, "image": "images/harry.jpeg", "copies": int(copies)})
    
    save_books()
    return jsonify({"success": True, "message": f"Adding {bookName} ,Release:  {releaseDate}, Copies: {copies}, author: {author}"})

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
            


@app.route("/removebook", methods=["POST"])
def removeBook():    
    data = request.get_json()
    bookid = data.get("bookid")
    for book in books:
        if(book['id'] == bookid):
            themessage = f"Book {bookid} - {book['name']} was removed succesfully, Refreshing Page."
            books.remove(book)
            save_books()
            return jsonify({"success" : True, "message": themessage})
        
    return jsonify({"success" : False, "message": "Book Was not Found in the system"})

@app.route("/getusers",methods=["POST"])
def getusers():
    sendusers = []
    for user in users:
        sendusers.append({"userid":user["userid"], "username": user['username'], "books":user['books'], "isadmin":user['isAdmin']})
        
    return jsonify({"success": True, "data": sendusers})

@app.route("/deleteuser", methods=["POST"])
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

@app.route("/setPermissions", methods=["POST"])
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





@app.route("/register", methods=["POST"])
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
    users.append({"userid": userid, "username":uname, "password":password, "books": "", 'isAdmin':False})
    save_users()
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    uname = data.get('username')
    password = data.get("password")
    found,loggedin = check_login(uname,password)
    if(found):
        return jsonify({"success": True, "user": loggedin})

            

    return jsonify({"success": False})

            
def check_login(uname,password):
    if not uname or not password:
        return False
    
    for user in users:
        if(uname == user["username"]):
            if(password == user["password"]):
                return True,user
            
    return False,False

if __name__ == "__main__":
    if(not FORCESAVE):
        books = load_json(BOOKSFILE)
    else:
        save_books()


    users = load_json(USERSFILE)

    app.run(debug=True, port=911)