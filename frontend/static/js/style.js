function updateNavbarLinks() {
    fetch('/api/is_authenticated')
      .then(response => response.json())
      .then(data => {
        if (data.is_authenticated) {
          // User is authenticated
          document.getElementById("community-link").style.display = "inline";
          document.getElementById("profile-link").style.display = "inline";
          document.getElementById("logout-link").style.display = "inline";
          document.getElementById("login-link").style.display = "none";
          document.getElementById("register-link").style.display = "none";
        } else {
          // User is not authenticated
          document.getElementById("community-link").style.display = "none";
          document.getElementById("profile-link").style.display = "none";
          document.getElementById("logout-link").style.display = "none";
          document.getElementById("login-link").style.display = "inline";
          document.getElementById("register-link").style.display = "inline";
        }
      })
      .catch(error => {
        console.error("Error fetching authentication status:", error);
      });
  }
  
  // Call updateNavbarLinks on page load
  document.addEventListener("DOMContentLoaded", updateNavbarLinks);
  