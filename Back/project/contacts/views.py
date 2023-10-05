#Contact Forms
from project.helper import *
from project import Base, Session
from flask import Blueprint
from project.contacts.models import Contact
# Contact Form (id (AUTO INCREMENT), name, email, message(LONGTEXT))

contacts = Blueprint('contacts', __name__,url_prefix='/contacts')
@contacts.route('/', methods=['GET', 'POST'])
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