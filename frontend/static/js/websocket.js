let ws;
let wsNotification;

function notificationWebsocket(link) {
    wsNotification = new WebSocket(link);

    wsNotification.onopen = () => {
        console.log("Notification connection opened.");
    };

    wsNotification.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
            showCustomNotification(data.username, data.message);
        }
    };

    wsNotification.onclose = () => {
        console.log("Notification connection closed.");
        wsNotification = new WebSocket(link);
    };

    wsNotification.onerror = (error) => {
        console.error("WebSocket error:", error);
        wsNotification = new WebSocket(link);
    };
}

function chatWebSocket(link) {
    if (ws)
        ws.close();

    ws = new WebSocket(link);

    ws.onopen = () => {
        console.log("WebSocket connection opened.");
    };

    ws.onmessage = (event) => {
        console.log(event);
		const data = JSON.parse(event.data)
		render_message(data.username, data.message);
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

	const submit_button = document.getElementById('submit')
    submit_button.removeEventListener("click", sendMessage(ws));
	submit_button.addEventListener("click", sendMessage(ws))
	const input = document.getElementById('input')
    input.removeEventListener("keypress", SendOnEnter(ws));
	input.addEventListener("keypress", SendOnEnter(ws))
	scrollToBottom();
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

function pongWebsocket(link, mode) {
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
            if (mode === '2v2') {
                const paddle3 = document.getElementById("paddle3");
                const paddle4 = document.getElementById("paddle4");
                paddle3.style.top = `${data.player3PaddleY}px`;
                paddle4.style.top = `${data.player4PaddleY}px`;
            }
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

    document.removeEventListener("keyup", handleKeyup);
    document.removeEventListener("keydown", handleKeydown);

    document.addEventListener("keyup", handleKeyup);
    document.addEventListener("keydown", handleKeydown);
}

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
        console.log("WebSocket connection closed.");
    }
}

function checkWebsocketPage(page, queryString = '') {
    if (!wsNotification || wsNotification.readyState == WebSocket.CLOSED || wsNotification.readyState == WebSocket.CLOSING) {
        if (wsNotification)
            wsNotification.close()
            wsNotification = null;
        notificationWebsocket('wss://42.mvpee.be/ws/notification/')
    }

    // console.log("Page:", page); //* DEBUG
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
            pongWebsocket(`wss://42.mvpee.be/ws/${urls[0]}/${game}/${mode}/${id}/`, mode);
        else if (game === 'puissance4')
            puissance4Websocket(`wss://42.mvpee.be/ws/${urls[0]}/${game}/${mode}/${id}/`);
    }
    else
        disconnectWebSocket();
}