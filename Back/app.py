from flask import Flask
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
players = [
    {"nickname":"Killer","money":5000,"level":6},
    {"nickname":"Fighter","money":15000,"level":15},
    {"nickname":"Capitalist123","money":9000000,"level":155},
]

@app.route("/")
def main():
    return players

def readjson():
    with open('players.json', 'r') as file:
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
            print("File 'players.json' not found.")
            return []

@app.route("/file")
def mainfile():
    return readjson()

if __name__ == "__main__":
    app.run(debug=True)