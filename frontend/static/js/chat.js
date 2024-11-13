function sendMessage(chatSocket){
	return function(e) {
		const sender_username = JSON.parse(document.getElementById('sender_username').textContent);
		const messageInputDom = document.querySelector('#input');
		const message = messageInputDom.value;
		chatSocket.send(JSON.stringify({
			'username': sender_username,
			'message': message,
		}));
		messageInputDom.value = ''; //clear the writing area after message is sent
	};
}


function scrollToBottom() {
    let objDiv = document.getElementById("chat-text");
    objDiv.scrollTop = objDiv.scrollHeight;
}
