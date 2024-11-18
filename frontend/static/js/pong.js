let moveInterval;
let currentDirection = null;
let phoneUp;
let phoneDown;

function handleKeydown(event) {
    let direction = null;
    if (event.key === "w" || event.key === "W") direction = "up";
    else if (event.key === "s" || event.key === "S") direction = "down";
    else return;

    if (currentDirection === direction) return;

    currentDirection = direction;

    if (moveInterval) clearInterval(moveInterval);

    moveInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(
                JSON.stringify({
                    type: "movement",
                    direction: currentDirection,
                })
            );
        }
    }, 10);
}

function handleKeyup(event) {
    let keyReleased = event.key.toLowerCase();
    if ((keyReleased === "w" && currentDirection === "up") ||
        (keyReleased === "s" && currentDirection === "down")) {
        clearInterval(moveInterval);
        moveInterval = null;
        currentDirection = null;
    }
}

function handlePhoneButton(direction) {
    if (currentDirection === direction) return;

    currentDirection = direction;

    if (moveInterval) clearInterval(moveInterval);

    if (currentDirection) {
        moveInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(
                    JSON.stringify({
                        type: "movement",
                        direction: currentDirection,
                    })
                );
            }
        }, 10);
    }
}

function stopMovement() {
    if (moveInterval) {
        clearInterval(moveInterval);
        moveInterval = null;
        currentDirection = null;
    }
}
