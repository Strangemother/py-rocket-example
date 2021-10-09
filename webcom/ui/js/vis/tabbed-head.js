const emitEvent = function(name, detail) {
    let v = new CustomEvent(name, {detail})
    window.dispatchEvent(v)
    return v
}


const onEvent = function(name, handler) {
    return window.addEventListener(name, handler)
}
