var client_id = 2345
var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);

ws.onmessage = function(event) {
    var messages = document.getElementById('log_items')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)

    window.dispatchEvent(new CustomEvent('websocketMessage', {detail: event}))
};


function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}
