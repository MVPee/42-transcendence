function loadContent(page, queryString = '', addHistory = true) {
    if (queryString && !queryString.startsWith('?'))
        queryString = '?' + queryString;

    fetch(`/ssr/view/${page}/${queryString}`, {
        credentials: 'same-origin',
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        const contentElement = document.getElementById('content');
        contentElement.innerHTML = data.html;

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

        attachLinkEventListeners();

        if (addHistory)
            history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);
        else
            history.replaceState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    })
    .catch(error => console.error('Error loading content:', error));
}

function attachLinkEventListeners() {
    document.querySelectorAll("a.link").forEach(link => {
        link.removeEventListener("click", linkClickHandler);
        link.addEventListener("click", linkClickHandler);
    });
}

function linkClickHandler(event) {
    const url = new URL(this.href);

    event.preventDefault();
    const page = url.pathname.replace("/", "");
    const queryString = url.search;
    loadContent(page, queryString);
}

function handleFormSubmission(event) {
    const form = event.target;
    const action = form.getAttribute('action');
    const method = form.getAttribute('method').toUpperCase();
    
    if (method !== 'POST') return;

    event.preventDefault();

    const formData = new FormData(form);  // Use FormData directly for file uploads

    fetch(action, {
        method: 'POST',
        body: formData,  // Pass FormData directly
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),  // CSRF token, if needed
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        const contentElement = document.getElementById('content');
        if (data.redirect_url) {
            const page = data.redirect_url.replace('/', '');
            loadContent(page);
            return;
        }

        contentElement.innerHTML = data.html;
        
        const scripts = contentElement.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            Array.from(script.attributes).forEach(attr => { newScript.setAttribute(attr.name, attr.value); });
            if (script.src) {
                newScript.src = script.src;
                newScript.async = false;
            } 
            else
                newScript.textContent = script.textContent;
            script.parentNode.removeChild(script);
            document.body.appendChild(newScript);
        });

        attachLinkEventListeners();
        updateNavbarLinks();
    })
    .catch(error => console.error('Error during form submission:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.matches('form'))
            handleFormSubmission(event);
    });
    
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page) {
            const page = event.state.page;
            const queryString = event.state.query || '';
            loadContent(page, queryString, false);
        }
        else
            loadContent('home', '', false);
    });

    attachLinkEventListeners();
    updateNavbarLinks();

    const initialPath = location.pathname;
    const initialPage = initialPath.replace(/^\/|\/$/g, '') || 'play';
    const initialQuery = location.search;
    loadContent(initialPage, initialQuery, false);
});
