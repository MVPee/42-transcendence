function displayStats(id) {
    const allBtns = document.getElementsByClassName('btn-warning');
    const allStats = document.getElementsByClassName('Statistics');
    Array.from(allStats).forEach(element => {
        element.style.display = 'none';
    });
    document.getElementById(`${id}-block`).style.display = 'block';

    //Style
    Array.from(allBtns).forEach(button => {
        button.classList.remove('btn-warning');
        button.classList.add('btn-outline-warning');
    });

    const selectedButton = document.getElementById(id);
    selectedButton.classList.remove('btn-outline-warning');
    selectedButton.classList.add('btn-warning');
}
