document.addEventListener("keydown", (event) => {
    let direction = null;
    if (event.key === "w" || event.key === "W") direction = "up";
    if (event.key === "s" || event.key === "S") direction = "down";

    if (direction) {
        ws.send(JSON.stringify({
            type: "movement",
            direction: direction,
        }));
    }
});