function showCustomNotification(username, message) {
    let notificationsContainer = document.getElementById('notifications');

    const notification = document.createElement('div');
    notification.style.position = 'relative';
    notification.style.background = '#444';
    notification.style.color = 'white';
    notification.style.padding = '10px 20px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0px 0px 10px rgba(0, 0, 0, 0.5)';
    notification.style.opacity = '1';
    notification.style.transition = 'opacity 0.5s ease';

    notification.innerText = `${username}: ${message}`;
    notificationsContainer.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}
