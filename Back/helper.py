
import logging

# Imports That Are Sent To app.py
from flask import Flask,request,jsonify
from flask_cors import CORS

from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import os

# logging.basicConfig(
#     level=logging.DEBUG,          # Set the minimum log level to display
#     format='%(asctime)s [%(levelname)s]: %(message)s',
#     filename='my_app.log',        # Log messages to a file (optional)
# )

# a short cut for logging
# Logging was disabled because it messedup HTML LIVE SERVER DUE TO CONSTANT REFRESHES
def log_action(message,case):
    if(True):
        print("\033[91m LOG: " + message + "\033[0m")
        return
    
    if(case is None or case == ""):
        case = "DEBUG"
    
    if(message == "" or message is None):
        logging.debug("log_action received an empty message")
        return

    case = case.upper()

    if(case == "DEBUG"):
        logging.debug(message, exc_info=True)
    elif(case == "INFO"):
        logging.info(message, exc_info=True)
    elif(case == "WARNING"):
        logging.warning(message, exc_info=True)
    elif(case == "ERROR"):
        logging.error(message, exc_info=True)
    elif(case == "CRITICAL"):
        logging.critical(message, exc_info=True)
    else:
        logging.debug("log_action was not used properly case non-existent")

# import json
# import threading
# import random
# def load_json(filename):
#     with open(filename, 'r') as file:
#         try:
#             # Load the JSON data from the file
#             data = json.load(file)

#             # Now, 'data' contains the parsed JSON content
#             # You can access and manipulate the data as needed
#             return data

#         except json.JSONDecodeError as e:
#             print("Error decoding JSON:", e)
#             return []
#         except FileNotFoundError:
#             print(f"File {filename} not found.")
#             return []
        
# def save_json(filename,table):
#     save_thread = threading.Thread(target=save_table_to_file, args=(filename, table))
#     save_thread.start()
#     # with open(filename, "w") as json_file:
#     #     json.dump(table, json_file, indent=4)

# def save_table_to_file(filename, table):
#     with open(filename, "w") as json_file:
#         json.dump(table, json_file, indent=4)



# def FindBook(table,param,way):
#     books = table
#     for book in books:
#         if book[way] == param:
#             return book
        
#     return None

# def FindUser(table,param,way):
#     users = table
#     for user in users:
#         if user[way] == param:
#             return user
        
#     return None

# def FindUserBook(table,bookid):
#     for thebook in table:
#         if thebook['id'] == bookid:
#             return thebook 
#     return None

# def generate_id(users):
#     randomid = random.randint(210000000, 450000000)

#     if len(users) > 0:
#         # Check if the generated ID is already in use
#         while any(user.get('userid') == randomid for user in users):
#             randomid = random.randint(210000000, 450000000)

#     return str(randomid)