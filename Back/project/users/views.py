from project.helper import *
from project import Base, Session
from flask import Blueprint
from project.users.models import User
from project.books.views import returnallbooks
import json

users = Blueprint('users', __name__,url_prefix='/usersapi')
# gets all users and returns to the admin excluding passwords
@users.route("/",methods=["GET"])
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
@users.route("/", methods=["DELETE"])
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


# Toggles Librarian access to a user
@users.route("/setPermissions", methods=["POST"])
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



#Registration/login system
@users.route("/accounts", methods=["PUT"])
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

@users.route("/accounts", methods=["POST"])
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