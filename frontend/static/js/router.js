function loadContent(page, queryString = '', addHistory = true) {

    if (queryString && !queryString.startsWith('?'))
        queryString = '?' + queryString;

    fetch(`/ssr/view/${page}/${queryString}`, {
        credentials: 'same-origin', // Include cookies for CSRF
    })
    .then(response => {
        if (!response.ok)
            throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {

        if (data.redirect_url)
            window.location.href = data.redirect_url;

        // Insert the HTML content
        const contentElement = document.getElementById('content');
        contentElement.innerHTML = data.html;

        /*
            WebSocket Connect and Disconnect here
        */
        checkWebsocketPage(page, queryString);

        // Execute any scripts in the loaded content
        const scripts = contentElement.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            Array.from(script.attributes).forEach(attr => { newScript.setAttribute(attr.name, attr.value); });
            if (script.src) {
                newScript.src = script.src;
                newScript.async = false;
            } else {
                newScript.textContent = script.textContent;
            }
            script.parentNode.removeChild(script);
            document.body.appendChild(newScript);
        });

        // Reattach event listeners to new links
        attachLinkEventListeners();

        updateNavbarLinks();

        // Add the page to history
        if (addHistory)
            history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);
        else
            history.replaceState({ page: page, query: queryString }, '', `/${page}${queryString}`);            
    })
    .catch(error => console.error('Error loading content:', error));
}

function attachLinkEventListeners() {
    // Remove previous event listeners to prevent duplication
    document.querySelectorAll("a.link").forEach(link => {
        link.removeEventListener("click", linkClickHandler); // Remove existing listener if any
        link.addEventListener("click", linkClickHandler);
    });
}

function linkClickHandler(event) {
    event.preventDefault();
    const url = new URL(this.href);
    const page = url.pathname.replace("/", "");
    const queryString = url.search;
    // console.log('Navigation link clicked:', 'page=', page, 'queryString=', queryString); //* DEBUG
    loadContent(page, queryString);
}

function handleFormSubmission(event) {
    const form = event.target;
    const action = form.getAttribute('action');
    const method = form.getAttribute('method').toUpperCase();
    
    if (method !== 'POST') return;

    event.preventDefault();

    const formData = new FormData(form);
    const csrfToken = formData.get('csrfmiddlewaretoken');

    // Convert form data to URL-encoded string
    const data = new URLSearchParams();
    for (const pair of formData) {
        data.append(pair[0], pair[1]);
    }

    fetch(action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
        body: data.toString(),
        credentials: 'same-origin',
    })
    .then(response => {
        if (!response.ok)
            throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        const contentElement = document.getElementById('content');
        // Insert the new page content
        
        if (data.redirect_url) {
            // Use loadContent to change the content and URL
            const page = data.redirect_url.replace('/', ''); // Get the page name without '/'
            loadContent(page);
            return;  // Exit to prevent further execution
        }
        
        contentElement.innerHTML = data.html;
        
        // Execute any scripts in the loaded content
        const scripts = contentElement.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            Array.from(script.attributes).forEach(attr => { newScript.setAttribute(attr.name, attr.value); });
            if (script.src) {
                newScript.src = script.src;
                newScript.async = false;
            } else {
                newScript.textContent = script.textContent;
            }
            script.parentNode.removeChild(script);
            document.body.appendChild(newScript);
        });

        // Reattach event listeners to new links
        attachLinkEventListeners();

        updateNavbarLinks();

        // Update the URL and history if login or register was successful
        if (data.success)
            history.pushState({ page: 'profile' }, '', '/profile');
    })
    .catch(error => {
        console.error('Error during form submission:', error);
    });
}




document.addEventListener("DOMContentLoaded", function () {
    // Handle form submissions within dynamically loaded content
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.matches('form')) {
            handleFormSubmission(event);
        }
    });
    
    // Handle the back and forward buttons
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page) {
            const page = event.state.page;
            const queryString = event.state.query || '';
            loadContent(page, queryString, false);
        }
        else loadContent('home', '', false);
    });

    // Initial attachment of event listeners
    attachLinkEventListeners();

    updateNavbarLinks();

    // Load initial content based on URL path
    const initialPage = location.pathname.replace(/^\/|\/$/g, '') || 'home';
    const initialQuery = location.search;
    loadContent(initialPage, initialQuery, false);
});
