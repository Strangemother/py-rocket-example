
let app = Vue.createApp({})

app.component('tabs', Tabs)
app.component('graph-view', GraphView)

let loggerApp = Vue.createApp(Logger).mount('#logger')
let pipedViewApp = Vue.createApp(Pipesview).mount('#piped_view')

let mounted = app.mount('#tabbed_ui')

