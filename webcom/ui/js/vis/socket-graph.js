let graphUnits = {}

class NodeDispather {
    /*
    listen to node events and pass to the correct graphs as required.
     */
    constructor(){
        this.enableListeners()
    }

    enableListeners(){
        onEvent('node-event', this.nodeEvent.bind(this))
    }


    nodeEvent(e) {
        let d = e.detail
        console.log(d)
        // Farm to the correct graphs.

    }
}

const nodeDispatcher = new NodeDispather()

const Pipesview = {
    /*
        dispatch client messages to the correct graph using a simple key value
        pair
     */

    data() {
        return {
            messageCount: 0
        }
    }

    , mounted(){
        onEvent('node-event', this.routeMessage.bind(this))
        onEvent('tabs-unit', this.tabsUnit.bind(this))

    }

    , methods: {
        routeMessage(e){
            /*given a message, send the message to the correct graph units. */
            let d = e.detail
            console.log('routeMessage', e, d)

            this.messageCount += 1

            let outbound = this.getTargets(d)
        }

        , tabsUnit(e) {
            let entity = e.detail.entity
            this.tabUnit = entity
        }

        , getTargets(d) {
            /*
            d:
                action: "add"
                id: 6548
                type: "node"
                value:
                    id: 7
                    label: "7"
             */
            let tabId = d.tabId
            if(tabId == undefined) {
                // generate the target tabs

                // Check for active pipes
                // else send to active tab

                // else send to last selected.
                tabId = this.tabUnit.lastSelected
            }

            let clientId = d.id
            if(tabId == undefined) {
                tabId = this.tabUnit.topTab(clientId)
            }

            if(tabId == undefined) {
                let tabObject = this.tabUnit.newTab(clientId)
                tabId = tabObject.id
            }

            this.$nextTick(function(){
                graphUnits[tabId].app.newNodeObject(d.value)
            })

            /*
            tab ID[s]
            tab index[es]
            client ID[s]
            */
        }
    }
}

const GraphView = {
    template: cut('.templates .graph-view')

    , props: [
        'tabkey',
    ]

    , data() {
        return {
            ready: false
        }
    }

    , mounted() {
        console.log('GraphView mounted')
        this.buildVisual()
    }

    , methods: {

        buildVisual(){

            let networkId = `graph-${this.tabkey}`
            var container = document.getElementById(networkId);

            if(container == undefined) {
                console.warn('Cannot build', networkId)
                return
            }

            let options = this.defaultOptions()
                , n = []
                , e = []
                , nodes = new vis.DataSet(n)
                , edges = new vis.DataSet(e)
                , data = {nodes, edges}
                , network = new vis.Network(container, data, options)
                , unit = { network, container, networkId,
                           nodes, edges, n, e, app:this }

            network.once('afterDrawing', () => {
                container.style.height = '60vh'
            })

            graphUnits[this.tabkey] = unit

            this.ready = true
        }

        , defaultOptions(){
            return {
                layout: {
                  // improvedLayout: false
                  // hoverWidth:2
                }
                , edges: {
                    hoverWidth: function (width) {return width+2;}
                    , selectionWidth: function (width) {return width*2;}
                }
            };
        }

        , newNodeObject(node) {
            let d = node
            d.label = String(d.label || d.id)
            return this.pushNode(d);
        }

        , newNode(id, label, extra){
            let d = extra || {}
            d.id = id
            d.label = String(label || id)
            return this.pushNode(d);
        }

        , pushNode(node) {
            let data = graphUnits[this.tabkey]
            data.nodes.add(node)
            return node
        }

        , newEdge(fromId, toId, extra) {
            let d = extra || {}
            d.from = fromId
            d.to = toId

            let data = graphUnits[this.tabkey]
            data.edges.add(d)
            return d
        }

    }
}


  // // create an array with nodes
  // var nodes = new vis.DataSet(data.nodes);

  // // create an array with edges
  // var edges = new vis.DataSet(data.edges);

  // // create a network
  // var container = document.getElementById("mynetwork");

  // var data = {
  //   nodes: nodes,
  //   edges: edges
  // };

  // var options = {
  //     layout: {
  //         // improvedLayout: false
  //         // hoverWidth:2
  //     }
  //     , edges: {
  //         hoverWidth: function (width) {return width+2;}
  //         ,selectionWidth: function (width) {return width*2;}

  //     }
  // };

  // var network = new vis.Network(container, data, options);

  // network.once('afterDrawing', () => {
  //     container.style.height = '100vh'
  // })
  // return {data, network}
