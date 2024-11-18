function updateNavbarLinks() {
  fetch('/api/is_authenticated')
    .then(response => response.json())
    .then(data => {
      if (data.is_authenticated) {
        // User is authenticated
        if (!wsNotification || wsNotification.readyState == WebSocket.CLOSED || wsNotification.readyState == WebSocket.CLOSING) {
          if (wsNotification)
            wsNotification.close()
          wsNotification = null;
          notificationWebsocket('wss://42.mvpee.be/ws/notification/')
        }
        document.getElementById("community-link").style.display = "inline";
        document.getElementById("profile-link").style.display = "inline";
        document.getElementById("login-link").style.display = "none";
        document.getElementById("register-link").style.display = "none";
      }
      else {
        // User is not authenticated
        if (wsNotification) {
          wsNotification.close()
          wsNotification = null;
        }
        document.getElementById("community-link").style.display = "none";
        document.getElementById("profile-link").style.display = "none";
        document.getElementById("login-link").style.display = "inline";
        document.getElementById("register-link").style.display = "inline";
      }
    })
    .catch(error => {
      console.error("Error fetching authentication status:", error);
    }
    );
}

// Call updateNavbarLinks on page load
document.addEventListener("DOMContentLoaded", updateNavbarLinks);
