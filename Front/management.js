document.getElementById('add-book-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const bookName = document.getElementById('bookName').value;
    const releaseDate = document.getElementById('releaseDate').value;
    const copies = document.getElementById('copies').value;
    const author = document.getElementById('author').value;
    const imageInput = document.getElementById('image');
    
    // Create a FormData object to send the form data, including the image
    const formData = new FormData();
    formData.append('name', bookName);
    formData.append('release', releaseDate);
    formData.append('copies', copies);
    formData.append('author', author);

    const fileSizeInBytes = imageInput.files[0].size;
    const maxFileSize = 2 * 1024 * 1024

    if (fileSizeInBytes > maxFileSize) {
        Message("File size exceeds the maximum allowed limit (2MB).","error");
        return;
    }
    formData.append('image', imageInput.files[0]); // Add the image file

    // Send the new book data to your Flask server using fetch with the PUT method
    fetch(localIP + '/books/managebook', {
        method: 'PUT',
        body: formData, // Use the FormData object
    })
        .then(response => response.json())
        .then(data => {
            // Handle the response from your server (e.g., success message)
            if (data.success) {
                Message(data.message, "success");
                // Optionally, you can clear the form fields after successful submission
                document.getElementById('add-book-form').reset();
            } else {
                Message(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});


// Remove Book
let booksData = [];



document.addEventListener('DOMContentLoaded', function () {
    // Wait For The Page To Load To Avoid Errors
    setTimeout(() => {
        resetBooksDisplay(); // Displays All The Books After Half a Second.
    }, 500);

});

function resetBooksDisplay(){
    // Request All Books From the server
    $.get(localIP+ "/books", function (books) {
        booksData = books;
        displayBooks(booksData, ""); // Display all books initially
    });
}

function displayBooks(books, query) {
    const bookList = $("#book-list");

    // Clear the existing book list
    bookList.empty();

    // Filter books based on the query
    const filteredBooks = books.filter(book => book.name.toLowerCase().includes(query.toLowerCase()));
    if (books.length === 0) {
        bookList.append("<p>No Registered Books.</p>");
    }
    else if (filteredBooks.length === 0) {
        bookList.append("<p>No matching books found.</p>");
    } else {
        const bookCards = filteredBooks.map((book) => {
            const card = $("<div>").addClass("col-lg-3 col-md-4 col-sm-6 mb-4");
            const cardContent = $("<div>").addClass("card h-100");
            const image = $("<img>").addClass("card-img-top").attr("src", "images/" + book.image);
            const cardBody = $("<div>").addClass("card-body");
            const title = $("<h5>").addClass("card-title").text("ID: " + book.id + " - " + book.name);
            const author = $("<p>").addClass("card-text").text("Author: " + book.author + "\nCopies: " + book.copies);
            
            const removeButton = $("<button>")
                .text("Remove")
                .addClass("btn btn-danger")
                .click(function () {
                    removeButton.prop("disabled", true);
                    fetch(localIP + '/books/managebook', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({"bookid": book.id}),
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Message(data.message, "success")
                                setTimeout(() => {
                                    resetBooksDisplay() 
                                    removeButton.prop("disabled", false);
                                }, 1000);
                            } else {
                                Message(data.message, 'error')
                                removeButton.prop("disabled", false);
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            removeButton.prop("disabled", false);
                        });
                });
        
            const editButton = $("<button>");
            const editInput = $("<input placeholder='how many copies' type='number'>");
            editButton.text("Edit Copies").addClass("btn btn-primary");
            
            editButton.click(function () {
                const inputValue = editInput.val();
                if(!inputValue) return Message("Amount Of Copies Not Chosen",'error')
                editButton.prop("disabled", true);
                fetch(localIP + '/books/managebook', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({"id": book.id, "copies": inputValue}),
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Message(data.message, "success")
                            setTimeout(() => {
                                resetBooksDisplay() 
                                editButton.prop("disabled", false);
                            }, 1000);
                        } else {
                            Message(data.message, 'error')
                            editButton.prop("disabled", false);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        editButton.prop("disabled", false);
                    });
            });
        
            cardBody.append(title, author, editButton, editInput, removeButton);
            cardContent.append(image, cardBody);
            card.append(cardContent);
            
            return card;
        });
        
        bookList.html(bookCards);
        
    }
}

$("#searchInput").on("input", function () {
    const query = $(this).val();
    displayBooks(booksData, query); // Filter and display books based on the search query
});