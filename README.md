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
- Doesn't work with Live Server

### Book Management
- Add and remove books from your library's collection with ease.
- Track the number of copies available for each book.
- View a list of books borrowed by users.

### User Borrowing
- Users can borrow books for different durations: a day, a week, or a month.
- Automated notifications to users and administrators when due dates expire.
- Automatic return of borrowed books when a user is deleted.

### Contact Form
- Users can contact the library via a contact form.
- Management can view and respond to user inquiries.

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

### Comes prepared for a virtual env
    pip install -r requirements.txt
    venv\Scripts\activate