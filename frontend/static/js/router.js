function loadContent(page, queryString = '', addHistory = true) {
    event.preventDefault();
    if (queryString && !queryString.startsWith('?'))
        queryString = '?' + queryString;

    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/ssr/view/${page}/${queryString}`, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            try {
                const data = JSON.parse(xhr.responseText);

                const contentElement = document.getElementById('content');
                contentElement.innerHTML = data.html;

                checkWebsocketPage(page, queryString);
                loadScripts();
            }
            catch (error) {
                if (xhr.status === 404) {
                    const contentElement = document.getElementById('content');
                    contentElement.innerHTML = "<h2 class='title-card'> 404 Not Found </h2>";
                    contentElement.innerHTML += 
                    "<div class='d-flex justify-content-center'><img src='/static/favicon.ico' alt='favicon' width='40%' height='auto'></div>";
                }
                else {
                    console.error('Error parsing JSON response:', error);
                    document.getElementById('content').innerHTML = `<h1 class="text-center">Error: ${xhr.status}</h1>`;
                }
            }
        }
    };

    if (addHistory) history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    else history.replaceState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    xhr.send();
}

function handleApiResponse(action, data) {
    if (action === '/api/logout/')
        loadContent('login');
    else if (action === '/api/login/') {
        if (data.login) loadContent('profile');
        else displayErrorMessage(data.error_message);
    }
    else if (action === '/api/register/') {
        if (data.register) loadContent('profile');
        else displayErrorMessage(data.error_message);
    }
}

function displayErrorMessage(errorMessage) {
    const errorMessages = document.getElementsByClassName('error_message');
    Array.from(errorMessages).forEach(element => { element.innerHTML = errorMessage; });
}

function handleFormSubmission(event) {
    const form = event.target;
    const action = form.getAttribute('action');
    const method = form.getAttribute('method').toUpperCase();

    if (method !== 'POST') return;

    event.preventDefault();

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();

    xhr.open('POST', action, true);
    xhr.withCredentials = true;

    const csrfToken = formData.get('csrfmiddlewaretoken');
    if (csrfToken)
        xhr.setRequestHeader('X-CSRFToken', csrfToken);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            try {
                const data = JSON.parse(xhr.responseText);

                const contentElement = document.getElementById('content');
                if (data.html)
                    contentElement.innerHTML = data.html;

                loadScripts();
                updateNavbarLinks();
                
                handleApiResponse();
            }
            catch (error) {
                console.error('Error parsing JSON response:', error);
                document.getElementById('content').innerHTML = '<h1>Error loading content</h1>';
            }
        }
    };

    xhr.send(formData);
}   

function loadScripts() {
    let scripts = document.getElementById('content').getElementsByTagName('script');
    
    for (let i = 0; i < scripts.length; i++) {
        let script = document.createElement('script');
        script.type = scripts[i].type || 'text/javascript';
        if (scripts[i].src) script.src = scripts[i].src;
        else script.innerHTML = scripts[i].innerHTML;
        document.body.appendChild(script);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.matches('form'))
        handleFormSubmission(event);
    });
    
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page)
        loadContent(event.state.page, event.state.query || '', false);
    });
    
    updateNavbarLinks();
    loadContent(location.pathname.replace('/', '') || 'play', location.search, false);
});
