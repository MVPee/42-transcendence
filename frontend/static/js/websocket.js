let ws;

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
            loadContent(`game/${data.id}`);
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

function gameWebsocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
        console.log("WebSocket connection opened.");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "player_movement") {
            console.log(`Player ${data.player} moved: ${data.direction}`);
            console.log(`player1PaddleY ${data.player1PaddleY}\nplayer2PaddleY: ${data.player2PaddleY}`);

            const paddle1 = document.getElementById("paddle1");
            const paddle2 = document.getElementById("paddle2");
            paddle1.style.top = `${data.player1PaddleY}px`;
            paddle2.style.top = `${data.player2PaddleY}px`;
        }
        else if (data.type === "player_info") {
            // Display "Player1 vs Player2"
            const playerDisplay = document.getElementById("player-display");
            playerDisplay.textContent = `${data.player1} vs ${data.player2}`;
        }
        else if (data.type === "info") {
            const infoDisplay = document.getElementById("info");
            infoDisplay.textContent = data.info;
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
    document.addEventListener("keydown", handleKeydown);
}

function handleKeydown(event) {
    if (event.key === "w" || event.key === "W") direction = "up";
    else if (event.key === "s" || event.key === "S") direction = "down";
    else return;

    if (direction && ws) {
        ws.send(
            JSON.stringify({
                type: "movement",
                direction: direction,
            })
        );
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
        const id = urls[1];
        gameWebsocket(`wss://42.mvpee.be/ws/${urls[0]}/${id}/`);
    }
    else
        disconnectWebSocket();
}