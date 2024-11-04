let ws;

function connectWebSocket() {
    if (ws)
        ws.close();

    ws = new WebSocket("wss://42.mvpee.be/ws/test/");

    ws.onopen = () => {
        console.log("WebSocket connection opened.");
        ws.send("Hello, WebSocket server!");
    };

    ws.onmessage = (event) => {
        const messagesDiv = document.getElementById("messages");
        if (messagesDiv) {
            const message = document.createElement("p");
            message.textContent = event.data;
            messagesDiv.appendChild(message);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

function checkWebsocketPage(page) {
    if (page === 'websocket')
        connectWebSocket();
    else
        disconnectWebSocket();
}