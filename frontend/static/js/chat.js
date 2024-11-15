function sendMessage(chatSocket){
	return function(e) {
		const messageInputDom = document.querySelector('#input');
		const message = messageInputDom.value;
		chatSocket.send(JSON.stringify({
			'message': message,
		}));
		messageInputDom.value = ''; //clear the writing area after message is sent
	};
}

function scrollToBottom() {
    let objDiv = document.getElementById("chat-text");
    objDiv.scrollTop = objDiv.scrollHeight;
}

function Send1v1() {
	ws.send(JSON.stringify({
		'message': '1v1',
	}));
}