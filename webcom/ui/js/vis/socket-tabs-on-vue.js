/*

This app manages the interface of tabbed graphs.
 */


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
            , lastSelected: undefined
        }
    }

    , mounted(){
        console.log('Tabs mounted')
        onEvent('client-wake', this.onClientWake.bind(this))
        onEvent('client-spawn', this.onClientSpawn.bind(this))
        onEvent('client-exit', this.onClientExit.bind(this))
        onEvent('client-show', this.onClientShow.bind(this))
        onEvent('client-hide', this.onClientHide.bind(this))
        emitEvent('tabs-unit', { entity: this})
    }

    , methods: {

        tabClick(pointerEvent, tab) {
            /* Given a tab button click, switch 'active' to true for all
            items with the same [tab] id.
             */
            let id = tab.id
            this.lastSelected = id

            if(pointerEvent.shiftKey) {
                this.forEachTabId(id, (t, n) => t.active = true)
                return
            }

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

        , hideTab(tabId) {
            return this.forEachTabId(tabId, (t, n) => t.active = false)
        }

        , onClientHide(event) {
            let d = event.detail
            let clientId = d.id
            let tabIndex = d.value
            let tabId = `${clientId}-${tabIndex}`
            var hiddenTabs = this.hideTab(tabId)
            if(hiddenTabs.length == 0) {
                // maybe string
                this.hideTab(tabIndex)

            }
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
            let tabId = `${clientId}-${tabIndex}`

            if(tabIndex != null) {
                this.switchToTab(tabId, appendTo)
                return
            }

            // unique tab does not exist, show all of client tabs
            // or the uppermost.
            let tagId = this.topTab(clientId)
            this.switchToTab(tabId, appendTo)
        }

        , topTab(clientId) {
            let tabIndex = this.tabCounts[clientId] - 1
            if(isNaN(tabIndex)) {
                return undefined
            }
            return `${clientId}-${tabIndex}`
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
            return tabObject
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
            return this.newTab(clientId)
        }

        , newTab(clientId) {
            let tabObject = this.generateTab(clientId)

            console.log(tabObject)

            let appendTo = this.activeCount() > 1
            this.switchToTab(tabObject.id, appendTo)
            return tabObject
        }

        , activeCount(){
            /* Return an integer count of the active panels */
            let count = 0
            this.forEachTab(t=>count+=t.active)
            return count
        }

        , onClientExit(event){
            let d = event.detail
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
