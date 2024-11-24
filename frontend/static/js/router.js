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
                console.error('Error parsing JSON response:', error);
                document.getElementById('content').innerHTML = `<h1 class="text-center">Error: ${xhr.status}</h1>`;
            }
        }
    };

    if (addHistory) history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    else history.replaceState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    xhr.send();
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
                contentElement.innerHTML = data.html;

                loadScripts();
                updateNavbarLinks();
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
