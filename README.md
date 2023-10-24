# iLibrary - Your Digital Library

iLibrary is a powerful digital library management system designed to make it easy to manage books, users, and interactions within your library. It offers a range of features to streamline your library's operations and enhance user experience.

## Features

## Default Admin User
- With a default username and password
  - Username: admin
  - Password: admin

### User Authentication
- Secure user authentication with hashed passwords for maximum security.

### Logging System
- The server always tells you what the problem is so you won't be left in the dark whenever something goes wrong
- Logging Doesn't work with Live Server

### Book Management
- Add and remove books from your library's collection with ease.
- Track the number of copies available for each book.
- View a list of books borrowed by users.


![Book Management](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help6.png)


### User Borrowing
- Users can borrow books for different durations: a day, a week, or a month.
- Automated notifications to users and administrators when due dates expire.
- Automatic return of borrowed books when a user is deleted.

![Book Borrow](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help5.png)


### Contact Form
- Users can contact the library via a contact form.

![Contact Form](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help3.png)


- Management can view all contact forms at all times.


![View Contact Form](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help4.png)

### Book Details
- For each book, provide essential information:
  - Name
  - Author
  - Cover Image
  - Release Date

## Getting Started

### Prerequisites

- Python (version: Built With: 3.11.5)
- Flask
- SQLAlchemy
- werkzeug (for password hashing)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/RotemDevAcc/PythonFB.git
   cd PythonFB

2. How To Start The Flask Server
  Navigate To PythonFB/Back
  run python/py app.py
  Flask Server Port Needs To Be //:911

3. How To Access The Interface/GUI
  open PythonFB With Visual Studio Code

  ![Open With Code](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help7.png)

  and then open Front/index.html with Live Server

  ![Open Live Server](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help8.png)


# Wanna Change The Port? 
  navigate to PythonFB/Back/app.py and change the ServerPort To whatever you want


  ![Port Back app.py](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help1.png)



  after that navigate to PythonFB/Front/script.js and change the ManualIP To true and set the ip address / port to whatever you want



  ![Port Front script.js](https://github.com/RotemDevAcc/PythonFB/raw/main/HelpImages/help2.png)


### Comes prepared for a virtual env
    pip install -r requirements.txt
    venv\Scripts\activate