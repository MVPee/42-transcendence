let ws;
let moveInterval;
let currentDirection = null;

function waitingWebSocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
        // console.log("WebSocket connection opened.");
    };

    ws.onmessage = (event) => {
        let count = 0;
        const data = JSON.parse(event.data);
        if (data.type === "player_list") {
            const playerList = document.getElementById("player-list");
            playerList.innerHTML = "";
            data.players.forEach(player => {
                count++;
                const listItem = document.createElement("li");
                listItem.textContent = player;
                playerList.appendChild(listItem);
            });
            const playerCount = document.getElementById("count");
            playerCount.innerHTML = count;
        }
        else if (data.type === "redirect") {
            console.log(data.id);
            loadContent(`game/${data.game}/${data.mode}/${data.id}`);
            disconnectWebSocket();
        }
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function chatWebSocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
        console.log("WebSocket connection opened.");
        ws.send("Hello, WebSocket server!");
    };

    ws.onmessage = (event) => {
        console.log(event.data);
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function puissance4Websocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "info") {
            const infoDisplay = document.getElementById("info");
            infoDisplay.textContent = data.info;
        }
        else if (data.type === "turn") {
            const infoDisplay = document.getElementById("turn");
            infoDisplay.textContent = data.turn;
        }
        else if (data.type === "color") {
            row = data.row;
            column = data.column;
            color = data.color;
            const td = document.getElementById(`${row}-${column}`);
            td.style.backgroundColor = data.color;
        }
        else if (data.type === "redirect") {
            loadContent(`profile`);
            disconnectWebSocket();
        }
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function pongWebsocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
        console.log("WebSocket connection opened.");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "player_movement") {
            const paddle1 = document.getElementById("paddle1");
            const paddle2 = document.getElementById("paddle2");
            paddle1.style.top = `${data.player1PaddleY}px`;
            paddle2.style.top = `${data.player2PaddleY}px`;
        }
        else if (data.type === "update_ball_position") {
            const ball = document.getElementById("ball");
            ball.style.left = `${data.ball_x}px`;
            ball.style.top = `${data.ball_y}px`;
        }
        else if (data.type === "update_score") {
            const score1 = document.getElementById("score-1");
            const score2 = document.getElementById("score-2");
            score1.textContent = `${data.player1_score}`;
            score2.textContent = `${data.player2_score}`;
        }
        else if (data.type === "info") {
            const infoDisplay = document.getElementById("info");
            infoDisplay.textContent = data.info;
        }
        else if (data.type === "countdown") {
            const infoDisplay = document.getElementById("countdown");
            infoDisplay.textContent = data.message;
        }
        else if (data.type === "redirect") {
            loadContent(`profile`);
            disconnectWebSocket();
        }
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    document.removeEventListener("keydown", handleKeydown);
    document.removeEventListener("keyup", handleKeyup);
    document.addEventListener("keydown", handleKeydown);
    document.addEventListener("keyup", handleKeyup);
}

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

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
        console.log("WebSocket connection closed.");
    }
}

function checkWebsocketPage(page, queryString = '') {
    // console.log("Page:", page);
    const urls = page.split('/');
    if (urls[0] === 'chat' && urls[1]) {
        const id = urls[1];
        chatWebSocket(`wss://42.mvpee.be/ws/${urls[0]}/${id}/`);
    }
    else if (urls[0] === 'waiting') {
        const game_mode = urls[1];
        const queue_type = urls[2];
        waitingWebSocket(`wss://42.mvpee.be/ws/${urls[0]}/${game_mode}/${queue_type}/`);
    }
    else if (urls[0] === 'game') {
        const game = urls[1];
        const mode = urls[2];
        const id = urls[3];
        if (game === 'pong')
            pongWebsocket(`wss://42.mvpee.be/ws/${urls[0]}/${game}/${mode}/${id}/`);
        else if (game === 'puissance4')
            puissance4Websocket(`wss://42.mvpee.be/ws/${urls[0]}/${game}/${mode}/${id}/`);
    }
    else
        disconnectWebSocket();
}