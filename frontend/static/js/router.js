document.addEventListener("DOMContentLoaded", function () {
    function loadContent(page, queryString = '', addHistory = true) {

        if (queryString && !queryString.startsWith('?'))
            queryString = '?' + queryString;

        fetch(`/api/view/${page}/${queryString}`)
            .then(response => {
                if (!response.ok)
                    throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                document.getElementById('content').innerHTML = data.html;

                const errorDiv = document.getElementById('error');
                if (data.error) {
                    errorDiv.innerHTML = data.error;
                    errorDiv.style.display = 'block';
                }
                else {
                    errorDiv.innerHTML = '';
                    errorDiv.style.display = 'none';
                }

                // Add the page to history if required
                if (addHistory)
                    history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);                
            })
            .catch(error => console.error('Error loading content:', error));
    }

    // Load initial content based on URL path
    const initialPage = location.pathname.replace(/^\/|\/$/g, '') || 'home';
    const initialQuery = location.search;
    loadContent(initialPage, initialQuery, false);

    // Set up navigation links to load content without refreshing
    document.querySelectorAll("nav a.link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const url = new URL(this.href);
            const page = url.pathname.replace("/", "");
            const queryString = url.search;
            console.log('Navigation link clicked:', 'page=', page, 'queryString=', queryString);
            loadContent(page, queryString);
        });
    });

    // Handle the back and forward buttons
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page) {
            const page = event.state.page;
            const queryString = event.state.query || '';
            loadContent(page, queryString, false);
        }
        else
            loadContent('home', '', false);
    });
});
