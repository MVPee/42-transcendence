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


function loadContent(event = null, page, queryString = '', addHistory = true) {
    const contentElement = document.getElementById('content');
    if (event) event.preventDefault();
    if (queryString && !queryString.startsWith('?'))
        queryString = '?' + queryString;

    fetch(`api/view/${page}/${queryString}`, {
        credentials: 'same-origin',
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 404)
                contentElement.innerHTML = `<h1 class="text-center p-5"> Code error: ${response.status}</h1>`;
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        contentElement.innerHTML = data.html;
        checkWebsocketPage(page, queryString);
        loadScripts();
        if (addHistory) history.pushState({ page: page, query: queryString }, '', `/${page}${queryString}`);
        else history.replaceState({ page: page, query: queryString }, '', `/${page}${queryString}`);
    })
    .catch(error => console.error('Error loading content:', error));
}


function displayErrorMessage(errorMessage=null, successMessage=null) {
    const errorMessages = document.getElementsByClassName('error_message');
    const successMessages = document.getElementsByClassName('success_message');
    Array.from(errorMessages).forEach(element => { element.innerHTML = ''; element.style.display='inline';});
    Array.from(successMessages).forEach(element => { element.innerHTML = ''; element.style.display='inline';});
    if (errorMessage) Array.from(errorMessages).forEach(element => { element.innerHTML = errorMessage; });
    if (successMessage) Array.from(successMessages).forEach(element => { element.innerHTML = successMessage; });
}


function handleApiResponse(event, action, data) {
    if (action === '/api/logout/')
        loadContent(event, 'login');
    else if (action === '/api/login/') {
        if (data.login) loadContent(event, 'profile');
        else displayErrorMessage(data.error_message, data.success_message);
    }
    else if (action === '/api/register/') {
        if (data.register) loadContent(event, 'profile');
        else displayErrorMessage(data.error_message, data.success_message);
    }
    else if (action === '/api/settings/')
        displayErrorMessage(data.error_message, data.success_message);
    else if (action === '/api/block/') {
        if (data.profile) loadContent(event, 'profile', `profile=${data.profile}`, false);
        else displayErrorMessage(data.error_message, data.success_message);
    }
    else if (action === '/api/friend/') {
        if (data.profile) loadContent(event, 'profile', `profile=${data.profile}`, false);
        else displayErrorMessage(data.error_message, data.success_message);
    }
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
                
                handleApiResponse(event, action, data);
            }
            catch (error) {
                console.log(error);
                document.getElementById('content').innerHTML = '<h1>Error loading content</h1>';
            }
        }
    };

    xhr.send(formData);
} 


document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.matches('form'))
        handleFormSubmission(event);
    });
    
    window.addEventListener("popstate", function (event) {
        if (event.state && event.state.page)
        loadContent(event, event.state.page, event.state.query || '', false);
    });
    
    updateNavbarLinks();
    loadContent(null, location.pathname.replace('/', '') || 'play', location.search, false);
});
