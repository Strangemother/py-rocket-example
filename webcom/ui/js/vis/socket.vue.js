/*

This app manages the interface of tabbed graphs.
 */
const Tabs = {
    data() {
      return {
            tabs: {
                1: {
                    title: "tab one"
                    , id: 1
                }
            }
            , clients: []
            , tabCounts: {
                1:1
            }
        }
    }

    , mounted(){
        console.log('Tabs mounted')
        onEvent('client-wake', this.onClientWake.bind(this))
        onEvent('client-spawn', this.onClientSpawn.bind(this))
        onEvent('client-exit', this.onClientExit.bind(this))
    }

    , methods: {

        tabClick(pointerEvent, tab) {
            /* Given a tab button click, switch 'active' to true for all
            items with the same [tab] id.
             */
            console.log(pointerEvent, tab)
            /*
                switch tabs
                If shift: append tab
             */
            let id = tab.id

            if(pointerEvent.shiftKey) {
                // only manipulate tabs with this ID,
                // ignoring other tab states.
                console.log('active without closing others')
                this.forEachTab(function(tab, n){
                    if (tab.id == id) {
                        tab.active = true
                    }
                })

                return
            }

            console.log('Switch to tab.')
            // Enable any tab with that ID alone.
            this.forEachTab((tab, n) => tab.active = tab.id == id)

        }

        , onClientWake(event){
            /*
            A new client is awake, telling this interface.
            Bank as a user, and supply a new tab with the ID.
             */
            let d = event.detail
            console.log('onClientWake', d)

            let id = d.id
            let tabObject = this.generateTab(id)

            console.log(tabObject)
            this.clients.push(id)
        }

        , onClientSpawn(event) {
            let d = event.detail
            let clientId = d.id
            console.log('Spawn Tab', event)
            let tabObject = this.generateTab(clientId)

            console.log(tabObject)
        }

        , onClientExit(event){
            let d = event.detail
            let clientId = d.id
            console.log('Exit client', event)
            this.forEachTab(function(tab, n){
                if(tab.clientId == clientId) {
                    tab.live = false
                }
            })
        }

        , forEachTab(func) {
            for(let tabName in this.tabs) {
                let tab = this.tabs[tabName]
                func(tab, tabName)
            }
        }


        , generateTab(clientId) {
            let id = clientId
            let v = this.tabCounts[id];
            v = v == undefined? 0: v;
            var tabId = `${id}-${v}`

            let t = {
                clientId: id
                , id: tabId
                , initIndex: v
                , title: tabId
                , live: true
                , active: true
            }

            this.tabs[tabId] = t
            this.tabCounts[id] = v + 1

            return t
        }
    }
}

let app = Vue.createApp(Tabs)

let mounted = app.mount('#tabbed_ui')
