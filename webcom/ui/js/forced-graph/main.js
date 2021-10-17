
var Graph

onEvent('node-event', function(e){
    /*
        action: "add"
        id: 5760
        type: "node"
        value:
            id: 0
            label: "0"
     */
    addNode(Graph, e.detail.value)
})

onEvent('edge-event', function(e){
    /*
    action: "add"
    id: 5760
    type: "edge"
    value:
        from: 10
        id: "10-9"
        to: 9
     */
    // Build a 'link' from this edge.
    let edge = e.detail.value
    edge.source = edge.from
    edge.target = edge.to

    addLink(Graph, edge)
})

onEvent('client-wake', function(e){
    let data = e.detail.value || {}

    let initData = data.data || {
        nodes: data.nodes || []
        , links: data.links || []
    };

    if(Graph != undefined) {
        console.warn('Resuing existing Graph')
        setData(Graph, initData)
    }

    Graph = buildGraph("3d-graph", initData, withRandom=false);
});
