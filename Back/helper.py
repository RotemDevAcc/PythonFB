import json
import threading
import random
def load_json(filename):
    with open(filename, 'r') as file:
        try:
            # Load the JSON data from the file
            data = json.load(file)

            # Now, 'data' contains the parsed JSON content
            # You can access and manipulate the data as needed
            return data

        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return []
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return []
        
def save_json(filename,table):
    save_thread = threading.Thread(target=save_table_to_file, args=(filename, table))
    save_thread.start()
    # with open(filename, "w") as json_file:
    #     json.dump(table, json_file, indent=4)

def save_table_to_file(filename, table):
    with open(filename, "w") as json_file:
        json.dump(table, json_file, indent=4)

def FindBook(table,param,way):
    books = table
    for book in books:
        if book[way] == param:
            return book
        
    return None

def FindUser(table,param,way):
    users = table
    for user in users:
        if user[way] == param:
            return user
        
    return None

def FindUserBook(table,bookid):
    for thebook in table:
        if thebook['id'] == bookid:
            return thebook 
    return None

def generate_id(users):
    randomid = random.randint(210000000, 450000000)

    if len(users) > 0:
        # Check if the generated ID is already in use
        while any(user.get('userid') == randomid for user in users):
            randomid = random.randint(210000000, 450000000)

    return str(randomid)