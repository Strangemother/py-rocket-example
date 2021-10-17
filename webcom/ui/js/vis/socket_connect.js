var client_id = Math.random().toString(8).slice(2)
var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);

ws.onmessage = function(event) {
    window.dispatchEvent(new CustomEvent('websocketMessage', {detail: event}))

    var messages = document.getElementById('log_items')
    if(messages == null) {
        return
    }
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)

};


function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}

