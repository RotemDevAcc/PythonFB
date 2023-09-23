
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

USELOGGING = False # Keep this as False if you are using HTML Live Server

if(USELOGGING):
    logging.basicConfig(
        level=logging.DEBUG,          # Set the minimum log level to display
        format='%(asctime)s [%(levelname)s]: %(message)s',
        filename='my_app.log',        # Log messages to a file (optional)
    )

# a short cut for logging
# Logging was disabled because it messed up HTML LIVE SERVER DUE TO CONSTANT REFRESHES
def log_action(message,case):
    if(not USELOGGING):
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