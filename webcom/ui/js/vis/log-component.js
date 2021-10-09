var logHistory = []

const Logger = {

    data(){
        return {
            keepHistory: true
            , mountLoadHistory: true
        }
    }


    , mounted(){
        onEvent('digestContent', this.digestContent.bind(this))
        if(this.mountLoadHistory) {
            this.loadHistory()
        }
    }

    , methods: {

        digestContent(content){
            let v = JSON.stringify(content.detail);
            callerDirtyLog(v)
            if(this.keepHistory) {
                window.logHistory.push(v)
                this.saveHistory()
            }

        }
        , saveHistory() {
            localStorage['history'] = JSON.stringify(window.logHistory)
        }

        , loadHistory() {
            let v = localStorage['history'] || "[]"
            window.logHistory = JSON.parse(v)
            for (var i = 0; i < window.history.length; i++) {
                let line = window.logHistory[i]
                if (line != undefined) {
                    callerDirtyLog(line)
                }
            }

        }
    }

}

var replayMe = function(ev){
    console.log("replay", ev)
    let data = JSON.parse(ev.currentTarget.text)
    digestContent(data)
}
