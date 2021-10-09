/*

This app manages the interface of tabbed graphs.
 */

const cut = function(selector){
    let n = document.querySelector(selector)
    n.remove()
    return n.outerHTML
}


const Tabs = {
    template: cut('.templates .tabs')
    , data() {
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
        onEvent('client-show', this.onClientShow.bind(this))
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
                // this.forEachTab(function(tab, n){
                //     if (tab.id == id) {
                //         tab.active = true
                //     }
                // })
                this.forEachTabId(id, (t, n) => t.active = true)
                return
            }

            console.log('Switch to tab.')
            // Enable any tab with that ID alone.
            this.forEachTab((t, n) => t.active = t.id == id)

        }

        , switchToTab(tabId, append=false) {
            /*
            Given an existing tab ID, switch to view the tab.
             */

            // Switch all to the id,
            // setting false for all without the name.
            console.log('switch to tab', tabId)
            if(append == true) {
                // Append update.
                this.forEachTabId(tabId, (t, n) => t.active = true)
                return
            }

            this.forEachTab((tab, n) => tab.active = tab.id == tabId)

        }
        , onClientShow(event) {
            /*

            calling `show_tab(2)` in py presents d:

                action: "show"
                id: 8144
                type: "client"
                value: 2

             */
            let d = event.detail
            let clientId = d.id
            let tabIndex = d.value
            let activeCount = this.activeCount()
            let appendTo = activeCount > 1

            if(tabIndex != null) {
                tabId = `${clientId}-${tabIndex}`
                this.switchToTab(tabId, appendTo)
                return
            }

            // unique tab does not exist, show all of client tabs
            // or the uppermost.
            tabIndex = this.tabCounts[clientId] - 1
            tabId = `${clientId}-${tabIndex}`
            this.switchToTab(tabId, appendTo)


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
            this.switchToTab(tabObject.id)
        }

        , onClientSpawn(event) {
            /*
                a client "spawn" is essentially a new tab, with a subid
                of the client and the tab index.

                Generate a new tab for the client and activate it.

                if 1 or 0 tabs are active, the new tab takes focus.

                If more than 1 tab is selected, the new tab is _appended_
                to the display list
             */
            let d = event.detail
            let clientId = d.id
            console.log('Spawn Tab', event)
            let tabObject = this.generateTab(clientId)

            console.log(tabObject)

            let appendTo = this.activeCount() > 1
            this.switchToTab(tabObject.id, appendTo)
        }

        , activeCount(){
            /* Return an integer count of the active panels */
            let count = 0
            this.forEachTab(t=>count+=t.active)
            return count
        }

        , onClientExit(event){
            let d = event.detail
            // let clientId = d.id
            console.log('Exit client', event)
            // this.forEachTab(function(tab, n){
            //     if(tab.clientId == clientId) {
            //         tab.live = false
            //     }
            // })

            this.forEachClientId(d.id, function(tab, n){
                tab.live = false
            })

        }

        , forEachTabId(id, f) {
            let res = []
                , stack = (t, n) => res.push(t);
            f = f || stack;

            this.forEachTab(function(tab, n){
                if(tab.id == id) {
                    f(tab, n)
                }
            })

            return res
        }

        , forEachClientId(id, f) {
            let res = []
                , stack = (t, n) => res.push(t);
            f = f || stack;

            this.forEachTab(function(tab, n){
                if(tab.clientId == id) {
                    f(tab, n)
                }
            })

            return res
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
                , active: v < 1
            }

            this.tabs[tabId] = t
            this.tabCounts[id] = v + 1

            return t
        }
    }
}

let app = Vue.createApp({})


app.component('tabs', Tabs)
let loggerApp = Vue.createApp(Logger).mount('#logger')
let mounted = app.mount('#tabbed_ui')

