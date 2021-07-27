
// let g = createRandom(_g)

var dn = {}

let download = function(name) {
    return fetch(name).then(x=>x.json()).then(tidy).then(
        (x)=>window.dn = createGraph(x)
    )
}

let tidy = function(d){

    let nodeColor = '#7ed684'
    for(let node of d.nodes) {
        // node.x = Math.random()
        // node.y = Math.random()
        node.shape = node.shape || 'box' // 'ellipse'
        node.color = node.color || {
            background: nodeColor
            , border: nodeColor
            // , border: '#257a36'
        }
        // node.label = `${node.label} ${node.x}, ${node.y}`
    }

    for(let edge of d.edges) {
        // edge.size = Math.random()

        edge.arrows = {
            to: {
              enabled: true
              ,type: 'circle'// 'vee', //arrow_types[i],
              ,scaleFactor: .3
              , arrowStrikethrough: false
            }

          }
        let y = String(edge.y ? edge.y: '0')
        let x = String(edge.x ? edge.x: '0')
        edge.label = `(${x}, ${y})`
        // console.log(edge)

    }
    return d
}



let createGraph = function(data){

  // create an array with nodes
  var nodes = new vis.DataSet(data.nodes);

  // create an array with edges
  var edges = new vis.DataSet(data.edges);

  // create a network
  var container = document.getElementById("mynetwork");
  var data = {
    nodes: nodes,
    edges: edges
  };

  var options = {
    layout: {
        // improvedLayout: false
    }
  };
  var network = new vis.Network(container, data, options);
  return {data, network}
}

var downloadAppend = function(name){

    let update = function(data) {
        if(dn.data == undefined) {
            return createGraph(data)
        }

        dn.data.edges.add(data.edges)
        dn.data.nodes.add(data.nodes)
    }

    fetch(name).then(x=>x.json()).then(tidy).then(update)
}


// download('g_vis.json')
downloadAppend('g_vis.json')
// download('g_vis.json')
