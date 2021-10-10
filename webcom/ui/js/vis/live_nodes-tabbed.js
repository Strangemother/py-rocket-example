/*

A simple "Live" nodes and edges graph implementation through websockets.

1. Recieve JSON string from the socket `websocketMessageHandler``
2. parse and digest `digestContent`

 */


// const emitEvent = function(name, detail) {
//     let v = new CustomEvent(name, {detail})
//     window.dispatchEvent(v)
//     return v
// }


// const onEvent = function(name, handler) {
//     return window.addEventListener(name, handler)
// }


var nodes = new vis.DataSet([{id:1}]);
var edges = new vis.DataSet([]);


let liveNodesWebsocketListenerInit = function(){
    onEvent('websocketMessage', websocketMessageHandler)
}


// window.dn = createGraph({
//     nodes, edges
// })

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


var callerDirtyLog = function(message) {
    let v =  `<li>
        <a href='javascript:;' onclick='replayMe(event)'>${message}</a>
    </li>`
    document.getElementById('log_items').innerHTML += v
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


let clientFromSocket = function(v, d, items) {
    /*
    A message regard the `type` client.
     */

    console.log('clientFromSocket', v,d)
    let action = d.action

    let func = {
          //wake: (data) => emitEvent('client-wake', data)
          // , spawn: (data) => emitEvent('client-spawn', data)
        // , remove: (v) => items.remove(v)
    }[action]

    emitEvent(`client-${action}`, d)

    return funcOrUnknown(func)(d)
}


let funcOrUnknown = function(f){
    return f == undefined ? unknown: f;
}


let discoverParent = function(data){
    /* Given a 'node' type, discover the target graph and return its data structure. */

    /*

    data:
        action: "add"
        id: 20500
        type: "node"
        value: {id: 0, label: '0'}

    1. If the data has no graph target, select the uppermost, or "active"
     */


}

let nodeFromSocket = function(v, d, items) {
    /*
        Given a message from the a socket pump, digest the node
        action and execute.

            {
                action: 'add'
                value:  {"id": 0, "label": "0"}
            }

        value for action `add` and `remove` are objects for the graph ui.
        Any valid object value for the function is accepted:

            value = {"id": 0, "label": "0"}
            // action add becomes:
            window.dn.data.nodes.add(value)

        A remove call may accept an `id` only

            {
                action: 'remove'
                value: 0
            }

            // resolves to:
            window.dn.data.nodes.remove(0)


     */
    /*
        v2 in the mutli view, the DN should access the live graph for this node.
     */
    let action = d.action

    if(items == undefined) {
        items = discoverParent(d)
    }

    let func = {
          add: (v) => items.add(v)
        , remove: (v) => items.remove(v)
    }[action]

    return funcOrUnknown(func)(v, d)
    // return func(v, d)
}

let edgeFromSocket = function(v, d) {
    return nodeFromSocket(v, d, dn.data.edges)
    // return dn.data.edges.add(v)
}


let unknown = function(v, d){
    console.warn('!! Unknown', d)
}


let digestContent = function(content) {
    /*
        Given the content `type`, farm the message to [type]FromSocket
        function. If the type is unknown send to the `unknown` function

            {
                type: 'node'
                , action: 'add'
                , value:  {"id": 0, "label": "0"}
            }

        The value content is specific to the called function

     */
    console.log('digestContent', content)
    emitEvent('digestContent', content)

    let func = {
        [undefined]: unknown
        , node: nodeFromSocket
        , edge: edgeFromSocket
        , client: clientFromSocket

    }[content.type];

    return funcOrUnknown(func)(content.value, content)

}


;liveNodesWebsocketListenerInit();
