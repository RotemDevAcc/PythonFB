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
    fetch(localIP + '/addbook', {
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

// Fetch existing books and display them
$(document).ready(function () {
    resetBooksDisplay()
});

function resetBooksDisplay(){
    $.get(localIP+ "books", function (books) {
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
        filteredBooks.forEach(function (book) {
            const card = $("<div>");
            card.addClass("col-lg-3 col-md-4 col-sm-6 mb-4");

            const cardContent = $("<div>");
            cardContent.addClass("card h-100");

            const image = $("<img>");
            image.addClass("card-img-top");
            image.attr("src", "images/" + book.image);

            const cardBody = $("<div>");
            cardBody.addClass("card-body");

            const title = $("<h5>");
            title.addClass("card-title");
            title.text("ID: " + book.id + " - " + book.name);

            const author = $("<p>");
            author.addClass("card-text");
            author.text("Author: " + book.author + "\nCopies: " + book.copies);

            const removeButton = $("<button>");
            removeButton.text("Remove");
            removeButton.addClass("btn btn-danger");
            
            removeButton.click(function () {
                removeButton.prop("disabled", true);
                fetch(localIP + 'removebook', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({"bookid": book.id}),
                })
                    .then(response => response.json())
                    .then(data => {
                        // Handle the response from your server (e.g., success message)
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
            const editInput = $("<input placeholder = 'how many copies' type = 'number'>")
            editButton.text("Edit");
            editButton.addClass("btn btn-primary");
            
            editButton.click(function () {
                const inputValue = editInput.val();
                if(!inputValue) return Message("Amount Of Copies Not Chosen",'error')
                editButton.prop("disabled", true);
                fetch(localIP + 'modifybook', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({"id": book.id, "copies": inputValue}),
                })
                    .then(response => response.json())
                    .then(data => {
                        // Handle the response from your server (e.g., success message)
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

            cardBody.append(title, author, editButton);
            cardBody.append(title, author, editInput);
            cardBody.append(title, author, removeButton);
            cardContent.append(image, cardBody);
            card.append(cardContent);
            bookList.append(card);
        });
    }
}

$("#searchInput").on("input", function () {
    const query = $(this).val();
    displayBooks(booksData, query); // Filter and display books based on the search query
});