
    const nodeColorScale = d3.scaleOrdinal(d3.schemeRdYlGn[4])

    const withGradientEdges = function(g) {

        g.linkThreeObject(link => {
          // 2 (nodes) x 3 (r+g+b) bytes between [0, 1]
          // For example:
          // new Float32Array([
          //   1, 0, 0,  // source node: red
          //   0, 1, 0   // target node: green
          // ]);
          const colors = new Float32Array([].concat(
            ...[link.source, link.target]
              .map(nodeColorScale)
              .map(d3.color)
              .map(({ r, g, b }) => [r, g, b].map(v => v / 255)
            )));

          const material = new THREE.LineBasicMaterial({ vertexColors: THREE.VertexColors });
          const geometry = new THREE.BufferGeometry();
          geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(2 * 3), 3));
          geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

          return new THREE.Line(geometry, material);
        })
        .linkPositionUpdate((line, { start, end }) => {
          const startR = Graph.nodeRelSize();
          const endR = Graph.nodeRelSize();
          const lineLen = Math.sqrt(['x', 'y', 'z'].map(dim => Math.pow((end[dim] || 0) - (start[dim] || 0), 2)).reduce((acc, v) => acc + v, 0));

          const linePos = line.geometry.getAttribute('position');

          // calculate coordinate on the node's surface instead of center
          linePos.set([startR / lineLen, 1 - endR / lineLen].map(t =>
            ['x', 'y', 'z'].map(dim => start[dim] + (end[dim] - start[dim]) * t)
          ).flat());
          linePos.needsUpdate = true;
          return true;
        })
        ;

        return g
    }


    const withArrowLinks = function(g, arrowLength=0, relPos=1, curve=0.0) {
        g
        .linkDirectionalArrowLength(arrowLength)
        .linkDirectionalArrowRelPos(relPos)
        .linkCurvature(curve)
        ;

        return g
    }


    const withParticles = function(g, color='red', width=1, hoverPrecision=10,
        clickEmit=true) {

        g.linkDirectionalParticles("value")
        .linkDirectionalParticleSpeed(d => d.value * 0.001)
        .linkDirectionalParticleColor(() => color)
        .linkDirectionalParticleWidth(width)
        .linkHoverPrecision(hoverPrecision)
        ;

        if(!clickEmit) {
            return g
        }

        g.onLinkClick(function(link, event){
            link.value += 1
            g.emitParticle(link, event)
            window.setTimeout(()=>link.value -= 1, 1000)
        }) // emit particles on link click

        return g;
    }


    const withRandomInject = function(g, tick=100, duration=2000){

        let intervalId = setInterval(() => {
          const { nodes, links } = g.graphData();
          const id = nodes.length;

          nodes.push({ id, value: randVal() })
          links.push({ source: id, value: 2 , target: Math.round(Math.random() * (id-1)) })

          g.graphData({
            nodes, links,
          });
        }, tick);

        setTimeout(()=> clearInterval(intervalId), duration)
    }

    const setData = function(g, data) {
        g.graphData(data);
    }

    const addNode = function(g, data) {
        const { nodes, links } = g.graphData();
        nodes.push(data)
        g.graphData({
            nodes, links,
        });
    }

    const addLink = function(g, data) {
        const { nodes, links } = g.graphData();
        links.push(data)
        g.graphData({
            nodes, links,
        });
    }


    const withNodeScale = function(g){
        g.nodeAutoColorBy('value')
        .nodeColor(node => nodeColorScale(node.value))
        .nodeVal((d)=>{
            let v = d.value;
            return (v)
        })
    }


    const withBloom = function(g, BloomPass, strength=1, radius=.4, threshold=.2){

        const bloomPass = new BloomPass();
        bloomPass.strength = strength
        bloomPass.radius = radius
        bloomPass.threshold = threshold;
        g.postProcessingComposer().addPass(bloomPass);
    }

    const withEdgeText = function(g){
        g.linkThreeObjectExtend(true)
        .linkThreeObject(link => {
          // extend link with text sprite
          const sprite = new SpriteText(`${link.source} > ${link.target}`);
          // const sprite = new SpriteText(`${link.source.value}`);
          sprite.color = 'lightgrey';
          sprite.textHeight = 1.5;
          return sprite;
        })
        .linkPositionUpdate((sprite, { start, end }) => {
          const middlePos = Object.assign(...['x', 'y', 'z'].map(c => ({
            [c]: start[c] + (end[c] - start[c]) / 2 // calc middle point
          })));

          // Position sprite
          Object.assign(sprite.position, middlePos);
        });

        // Spread nodes a little wider
        g.d3Force('charge').strength(-120);

        return g;
    }


    function removeNode(node) {
      let { nodes, links } = Graph.graphData();
      links = links.filter(l => l.source !== node && l.target !== node); // Remove links attached to node
      nodes.splice(node.id, 1); // Remove node
      nodes.forEach((n, idx) => { n.id = idx; }); // Reset node ids to array index
      Graph.graphData({ nodes, links });
    }

    let randomizeValues = function() {
        let { nodes, links } = Graph.graphData();
        nodes.forEach((n, idx) => { n.value = randVal()});
        Graph.graphData({ nodes, links });

    }

    const randVal = function(){
        return Math.round(Math.random() * 20)
    }

    let tickChange = (timeout)=> {
        randomizeValues();
        t=setTimeout(()=>tickChange(timeout), timeout);
    }

    let randomizer = function(timeout=100){
        /* stop = randomizer(500) */
        setTimeout(()=>tickChange(timeout), 10)
        return stopRandomizer
    }

    let stopRandomizer = function(){
        clearInterval(t)
    }


const buildGraph = function(elementId, _initData, withRandom=true) {
    const elem = document.getElementById(elementId);
    let graph = ForceGraph3D()(elem)
        .enableNodeDrag(true)
        .graphData(_initData)
        .nodeLabel('value')
        // .onNodeClick(removeNode)
        ;

    // withGradientEdges(graph)
    withNodeScale(graph)
    withArrowLinks(graph, 3, 1, 0)
    withParticles(graph, 'white', 2, 10)

    if(withRandom) {
        withRandomInject(graph, 100, 6000)
    }
    //withEdgeText(graph)
    withBloomEvent(graph, .5, .3)
    return graph
}

withBloomEvent = function(g, ...args){
    window.addEventListener('bloompass', (e)=>bloompassEvent(e, ...args))
}

let bloompassEvent = function(e, ...args){
    console.log('bloompassEvent')
    // e.detail == UnrealBloomPass
    withBloom(Graph, e.detail, ...args)
}




        // .linkDirectionalArrowLength(3.5)
        // .linkDirectionalArrowRelPos(1)
        // .linkCurvature(0.25)

        // .linkDirectionalParticles("value")
        // .linkDirectionalParticleSpeed(d => d.value * 0.001)
        // .linkDirectionalParticleColor(() => 'red')
        // .linkDirectionalParticleWidth(1)
        // .linkHoverPrecision(10)


