function displayStats(id) {
    const allStats = document.getElementsByClassName('Statistics');
    Array.from(allStats).forEach(element => {
        element.style.display = 'none';
    });
    const choosedStat = document.getElementById(id);
    choosedStat.style.display = 'block';
}