let userName = null
let isAdmin = false;
let userBooks = null;



let localIP = `${window.location.protocol}//${window.location.hostname}:911/`; // Read Your Local IP Automaticlly 
const ManualIP = false; // Insert IP Manually
if (ManualIP){
    localIP = "http://127.0.0.1:911/" // Change This To Whatever You Want Default: http://127.0.0.1:911/
}


// User Logged in, Load His Details and save to localstorage
function UserLoggedin(user){
    if (!user) return
    var userData = {
        "username": user.username,
        "admin": user.isAdmin,
        "books": user.books
    };
    userName = user.username
    isAdmin = user.isAdmin

    userBooks = user.books ? user.books : null
    localStorage.setItem("saveduser",JSON.stringify(userData))
}




function Message(message, type){

    // Play A Notification Sound
    var audio = document.getElementById("notificationSound");
    if (audio) {
        audio.play();
    }

    // If type not selected play a default color
    if(!type){
        type = "linear-gradient(to right, #00b09b, #96c93d)"
    }else if (type == "error"){
        type = "linear-gradient(to right, #F74141, #B30000)"
    }else if (type == "info"){
        type = "linear-gradient(to right, #25A9F6, #0067CE)"
    }else if (type == "success"){
        type = "linear-gradient(to right, #00A510, #167e21)"
    }
    Toastify({
        text: message,
        style: {
            background: type, // Customize the background color
        },
        className: "custom-toastify", // Add a custom CSS class for styling
        position: "bottom-center", // Change the position of the notification
        duration: 3000, // Duration in milliseconds
        gravity: "top", // Change the direction of the notification animation
    }).showToast();
}

let loggingout = false;

// Log Out Proccess
function logout(){
    if(loggingout) return
    loggingout = true

    // Remove localStorage
    let saveduser = JSON.parse(localStorage.getItem("saveduser"));
    if(saveduser) localStorage.removeItem("saveduser")
    userName = null
    if (isAdmin){
        isAdmin = false;  
    }
    
    // Notify The Client we are logging him out
    Message("Logging Out",'info') 
    // Delay by 1.5 seconds so he will have time to read the notification.
    setTimeout(() => {
        loggingout = false
        window.location.href = 'index.html';
    }, 1500);
}



// Logs the client back automaticlly whenever he changes page or simply logs back on to the website
function autologin(){
    let saveduser = JSON.parse(localStorage.getItem("saveduser"));
    if(saveduser){
        userName = saveduser.username
        isAdmin = saveduser.admin
        userBooks = saveduser.books
    }
}


// Syncronize the client's Books with the server's database
function ModifyBooks(books){
    userBooks = books

    var userData = {
        "username": userName,
        "admin": isAdmin,
        "books": userBooks
    };
    localStorage.setItem("saveduser",JSON.stringify(userData))
}

function hasBook(id){
    if (!userBooks || userBooks.length == 0){
        return false
    }

    for (let index = 0; index < userBooks.length; index++) {
        const element = userBooks[index];
        if(element.id == id) return true
    }
}

autologin()