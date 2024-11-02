document.addEventListener("DOMContentLoaded", function () {
    function loadContent(page, addHistory = true) {
        fetch(`/api/get_html/${page}/`)
            .then(response => {
                if (!response.ok)
                    throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                document.getElementById('conten').innerHTML = data.html;

                // Add the page to history if required
                if (addHistory)
                    history.pushState({ page: page }, '', `/${page}`);
            })
            .catch(error => console.error('Error loading content:', error));
    }

    // Load initial content based on URL path
    const initialPage = location.pathname.substring(1) || 'home';
    loadContent(initialPage, false);

    // Set up navigation links to load content without refreshing
    document.querySelectorAll("nav a.link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const page = this.getAttribute("href").replace("/", "");
            loadContent(page);
        });
    });

    // Handle the back and forward buttons
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page)
            loadContent(event.state.page, false); // Load content without adding to history
        else
            loadContent('home', false); // Default to home if no state is present
    });
});
