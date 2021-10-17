

const emitEvent = function(name, detail) {
    let v = new CustomEvent(name, {detail})
    console.log('Emit', name, detail)
    window.dispatchEvent(v)
    return v
}


const onEvent = function(name, handler) {
    return window.addEventListener(name, handler)
}

let liveNodesWebsocketListenerInit = function(){
    onEvent('websocketMessage', websocketMessageHandler)
}


let websocketMessageHandler = function(ev){
    let messageEvent = ev.detail;
    let message = messageEvent.data
    let content = { text: message }
    if(message[0] == "{" && message[message.length-1] == '}') {
        content = JSON.parse(message)
    }

    //console.log('Message', messageEvent)

    digestContent(content)
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
    //console.log('digestContent', content)
    emitEvent('digestContent', content)

    let func = {
        [undefined]: unknown
        , node: nodeFromSocket
        , edge: edgeFromSocket
        , client: clientFromSocket

    }[content.type];

    return funcOrUnknown(func)(content.value, content)

}


let nodeFromSocket = function(v, d, items) {
    emitEvent('node-event', d)
}

let edgeFromSocket = function(v, d) {
    emitEvent('edge-event', d)

    //return nodeFromSocket(v, d, dn.data.edges)
    // return dn.data.edges.add(v)
}

let clientFromSocket = function(v, d, items) {
    /*
    A message regard the `type` client.
     */

    let action = d.action
    emitEvent(`client-${action}`, d)

    // return funcOrUnknown(func)(d)
}

let unknown = function(v, d){
    console.warn('!! Unknown', d)
}

let funcOrUnknown = function(f){
    return f == undefined ? unknown: f;
}

;liveNodesWebsocketListenerInit();







