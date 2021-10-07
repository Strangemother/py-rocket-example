/**
 * This example shows the available edge label renderers for the canvas
 * renderer.
 */
var i,
    s,
    N = 10,
    E = 50,
    _g = {
      nodes: [],
      edges: []
    };

let createRandom = function(g) {

    // Generate a random graph:
    for (i = 0; i < N; i++)
      g.nodes.push({
        id: 'n' + i,
        label: 'Node ' + i,
        x: Math.random(),
        y: Math.random(),
        size: Math.random(),
        color: '#666'
      });

    for (i = 0; i < E; i++)
      g.edges.push({
        id: 'e' + i,
        label: 'Edge ' + i,
        source: 'n' + (Math.random() * N | 0),
        target: 'n' + (Math.random() * N | 0),
        size: Math.random(),
        color: '#ccc',
        type: ['line', 'curve', 'arrow', 'curvedArrow'][Math.random() * 4 | 0]
      });
    return g
}


// sigma.parsers.json('../g.json', {
//   container: 'graph-container'
// });

let tidy = function(d){

    for(let node of d.nodes) {
        node.x = Math.random()
        node.y = Math.random()
        node.color = '#666'
    }

    for(let edge of d.edges) {
        edge.size = Math.random()
        edge.color = '#ccc'
        console.log(edge)

    }
    return d
}
// let g = createRandom(_g)
fetch('g.json').then(x=>x.json()).then(tidy).then(
    (x)=>createGraph(x)
)

let createGraph = function(data){

    // Instantiate sigma:
    s = new sigma({
      graph: data,
      renderer: {
        container: document.getElementById('graph-container'),
        type: 'canvas'
      },
      settings: {
        edgeLabelSize: 'proportional',
        // doubleClickEnabled: false,
        minEdgeSize: 0.5,
        maxEdgeSize: 4,
        enableEdgeHovering: true,
        edgeHoverColor: 'edge',
        defaultEdgeHoverColor: '#000',
        edgeHoverSizeRatio: 1,
        edgeHoverExtremities: true,
      }
    });


    // Initialize the dragNodes plugin:
    var dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);

    dragListener.bind('startdrag', function(event) {
      console.log(event);
    });
    dragListener.bind('drag', function(event) {
      console.log(event);
    });
    dragListener.bind('drop', function(event) {
      console.log(event);
    });
    dragListener.bind('dragend', function(event) {
      console.log(event);
        reshape(s,5000)
    });

    reshape(s, 10000)
}


let reshape = function(s, seconds=500){
    s.startForceAtlas2({worker: true, barnesHutOptimize: false});
    setTimeout(function(){
        s.stopForceAtlas2();
        // s.killForceAtlas2();
    }, seconds)
}
