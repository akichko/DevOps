

window.addEventListener('load', function () {
	var chatForm = document.getElementById('chat-form');
	var chatInput = document.getElementById('chat-input');

	chatForm.addEventListener('submit', function (e) {
		e.preventDefault();

		var message = chatInput.value;

		add_message(message, 'self-message');

		var xhr = new XMLHttpRequest();
		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4 && xhr.status === 200) {
				var response = JSON.parse(xhr.responseText);
				// 成功した場合の処理
				var output_text = response.message.response_text;
				add_message(output_text, 'user-message');
			} else {
				console.log("Error: " + xhr.status);
			}
		};
		xhr.open("POST", "/api/chat");
		xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
		var message = chatInput.value;
		xhr.send("input_text=" + encodeURIComponent(message));

		chatInput.value = '';
	});
});

function add_message(message, class_name) {

	var chatList = document.getElementById('chat-list');
	var date = new Date();
	var time = date.toLocaleString('ja-JP', { hour: 'numeric', minute: 'numeric' });
	var li = document.createElement('li');
	li.innerHTML = '<small class="text-muted">' + time + '</small><p class="chat-bubble">' + message + '</p>';
	if (class_name === 'self-message') {
		li.classList.add('text-right');
		li.querySelector('p').classList.add('chat-right');
	} else if (class_name === 'user-message') {
		li.classList.add('chat-left');
	}
	chatList.appendChild(li);
	var chatbody = document.getElementById('chat-body');
	chatbody.scrollTop = chatList.scrollHeight;

}