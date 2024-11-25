let ws;
let wsNotification;

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

function retriggerAnimation(object)
{
	object.style.animation = "none"; // Stop animation
	void object.offsetHeight;         // Trigger reflow
	object.style.animation = "";      // Restart animation
}

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
        wsNotification = null;
    };

    wsNotification.onerror = (error) => {
        wsNotification = null;
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
        }
        else if (data.type === "redirect") {
            loadContent(event, `game/${data.game}/${data.mode}/${data.id}`);
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
            loadContent(event, `profile`);
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
            setTimeout(() => {
                infoDisplay.style.opacity = '0';
                setTimeout(() => infoDisplay.remove(), 500);
            }, 5000);
        }
        else if (data.type === "countdown") {
            const infoDisplay = document.getElementById("countdown");
            infoDisplay.textContent = data.message;
        }
        else if (data.type === "redirect") {
            loadContent(event, `profile`);
            disconnectWebSocket();
        }
        else if (data.type === "update_game_header")
        {
            const header = document.getElementById(`game-header`);
			const game = document.getElementById(`game`);
            header.style.visibility = 'visible'
			game.style.visibility = 'visible'
            const player1Image = document.getElementById(`player1-image`);
            const player1Name = document.getElementById(`player1-name`);
            player1Image.src = data.player1Image;
            player1Name.textContent = data.player1Name;
            const player2Image = document.getElementById(`player2-image`);
            const player2Name = document.getElementById(`player2-name`);
            player2Image.src = data.player2Image;
            player2Name.textContent = data.player2Name;
			retriggerAnimation(player1Name);
			retriggerAnimation(player2Name);
			retriggerAnimation(player1Image);
			retriggerAnimation(player2Image);
        }
        else if (data.type === "announcement")
        {
            const game = document.getElementById(`game`);
            const announcements = document.getElementById(`announcements_div`);
            const header = document.getElementById(`game-header`);
            removeAllChildNodes(announcements);
            if (data.message === ""){
                game.style.visibility = 'visible';
            }
            else {
                let delay = 0;
                let words = data.message.split(" ");
                words.forEach((word) =>
                {
                    var span = document.createElement("span");
                    span.textContent = `${word}`;
                    span.className= "announcement_name";
                    if (word === "VS") {
                    span.className = "announcement_VS";
                    } else if (word === "Victory") {
                    span.className = "announcement_victory";
                    }
                    span.style.setProperty('--delay', `${delay}s`);
                    announcements.appendChild(span);
                    delay += 0.5;
                }
                );
            }
        }
        else if (data.type === "scoreboard")
        {
            const game = document.getElementById(`game`);
            const header = document.getElementById(`game-header`);
            const scoreboard = document.getElementById(`scoreboard`);
            const scoreboardRows = document.getElementById(`scoreboard-rows`);
            removeAllChildNodes(scoreboardRows);
            if (data.array === "")
            {
				game.style.visibility = 'visible'
                scoreboard.style.visibility = 'hidden';
            }
            else
            {
                game.style.visibility = 'hidden';
                header.style.visibility = 'hidden';
                scoreboard.style.visibility = 'visible';
				let array = JSON.parse(data.array);
				array.forEach((entry, index) =>{
					let player = entry.player;
					let score = entry.score;
					const tr = document.createElement('tr');
					const td1 = document.createElement('td');
					const avatar = document.createElement('img');
					const player_name = document.createElement('a');
					const crown = document.createElement('img');
					td1.className="align-middle";
					avatar.className="scoreboard-avatar";
					avatar.setAttribute('alt', 'avatar');
					avatar.setAttribute('src', `${player.avatar.url}`);
					player_name.textContent = `${player.username}`;
					player_name.setAttribute('href', `/profile?profile=${player.username}`)
					if (index != 0)
						player_name.className = "text-white"
					else
						player_name.className = "text-red"
					td1.appendChild(avatar);
					td1.appendChild(player_name);
					if (index <= 2)
					{
						let crown_link;
						if (index == 0)
							crown_link = '/static/assets/gold_crown.png'
						else if (index == 1)
							crown_link = '/static/assets/argent_crown.png'
						else
							crown_link = '/static/assets/bronze_crown.png'
						crown.setAttribute('src', `${crown_link}`);
						crown.className="scoreboard-avatar";
						td1.appendChild(crown);
					}
					const td2 = document.createElement('td');
					td2.className="align-middle";
					td2.innerHTML = `${score}`;
					tr.appendChild(td1);
					tr.appendChild(td2);
					scoreboardRows.appendChild(tr);
				});
				retriggerAnimation(scoreboard);
			}
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