// Function to navigate to a given page
function navigateTo(pageId, addToHistory = true) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.style.display = 'none';
    });

    // Show the selected page
    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.style.display = 'block';
    } else {
        // If the page doesn't exist, default to 'home'
        document.getElementById('home').style.display = 'block';
        pageId = 'home';
    }

    // Modify the URL without reloading the page
    if (addToHistory) {
        history.pushState({ page: pageId }, '', '#' + pageId);
    }
}

// Handle the initial page load
window.addEventListener('DOMContentLoaded', () => {
    const initialPage = location.hash ? location.hash.substring(1) : 'home';
    // Replace the current history state with the initial page
    history.replaceState({ page: initialPage }, '', '#' + initialPage);
    navigateTo(initialPage, false);
});

// Handle the browser's back and forward buttons
window.addEventListener('popstate', (event) => {
    const pageId = event.state ? event.state.page : 'home';
    navigateTo(pageId, false);
});