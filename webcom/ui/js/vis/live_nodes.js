var nodes = new vis.DataSet([{id:1}]);
var edges = new vis.DataSet([]);


let liveNodesWebsocketListenerInit = function(){
    window.addEventListener('websocketMessage', websocketMessageHandler)
}


window.dn = createGraph({
    nodes, edges
})

var newNode = function(id, label, extra){
    let d = extra || {}
    d.id = id
    d.label = String(label || id)

    dn.data.nodes.add(d)
    return d
}

var newEdge = function(fromId, toId, extra) {
    let d = extra || {}
    d.from = fromId
    d.to = toId
    dn.data.edges.add(d)
    return d
}


var dirtyLog = function(message) {
    document.getElementById('log_items').innerHTML += `<li>${message}</li>`
}


let websocketMessageHandler = function(ev){
    let messageEvent = ev.detail;
    let message = messageEvent.data
    let content = { text: message }
    if(message[0] == "{" && message[message.length-1] == '}') {
        content = JSON.parse(message)
    }

    console.log('Message', messageEvent)

    digestContent(content)
}


let nodeFromSocket = function(v, d, items) {
    let action = d.action
    items = items == undefined? dn.data.nodes: items;

    let func = {
        add: (v) => items.add(v)
        , remove: (v) => items.remove(v)
    }[action]

    return func(v, d)
}

let edgeFromSocket = function(v, d) {
    return nodeFromSocket(v, d, dn.data.edges)
    // return dn.data.edges.add(v)
}

let unknown = function(v, d){
    console.warn('Unknown', d)
}

let digestContent = function(content) {
    console.log('content', content)
    let func = {
        [undefined]: unknown
        , node: nodeFromSocket
        , edge: edgeFromSocket

    }[content.type];

    func = func == undefined ? unknown: func;

    return func(content.value, content)

}

;liveNodesWebsocketListenerInit();
