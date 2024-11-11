document.addEventListener("keydown", (event) => {
    let direction = null;
    if (event.key === "ArrowUp") direction = "up";
    if (event.key === "ArrowDown") direction = "down";

    if (direction) {
        ws.send(JSON.stringify({
            type: "movement",
            direction: direction,
        }));
    }
});