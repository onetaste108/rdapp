import QtQuick 2.15
Item {
    Canvas {
        id: gridCanvas
        anchors.fill: parent
        opacity: 0.1
        Connections {
            target: timeline
            function onGridChanged() {
                gridCanvas.requestPaint()
            }
        }
        Connections {
            target: timeline
            function onFpsChanged() {
                gridCanvas.requestPaint()
            }
        }
        Connections {
            target: style
            function onStyleChanged() {
                gridCanvas.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = style.dark ? "white" : "black"
            ctx.lineWidth = 1
            ctx.beginPath()
            
            var minInterval = 10
            var maxInterval = mapX(1/timeline.fps)-mapX(0)
            var interval = maxInterval
            interval = interval / Math.min(1, Math.pow(2, Math.floor(Math.log2(interval/minInterval))))
            var offset = mapX(0) % interval

            for (var t = mapX(timeline.xIn)+offset; t < mapX(timeline.xOut); t+=interval) {
                var x = Math.round(t)
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
            }

            var minInterval = 25
            var maxInterval = Math.abs(mapY(1) - mapY(0))
            var interval = maxInterval
            interval = interval / Math.pow(2, Math.floor(Math.log2(interval/minInterval)))
            var offset = mapY(0) % interval

            for (var t = mapY(timeline.yIn)+offset; t < mapY(timeline.yOut); t+=interval) {
                var y = Math.round(t)
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.fillText("HELLO", 0, y)
            }

            ctx.stroke()

            ctx.lineWidth = 2
            ctx.strokeStyle = style.dark ? "white" : "black"
            ctx.beginPath()
            ctx.moveTo(0, mapY(0))
            ctx.lineTo(width, mapY(0))
            ctx.stroke()
            ctx.beginPath()
            ctx.moveTo(mapX(0), 0)
            ctx.lineTo(mapX(0), height)
            ctx.stroke()
        }
    }
    Canvas {
        id: textCanvas
        anchors.fill: parent
        opacity: 0.4
        Connections {
            target: timeline
            function onGridChanged() {
                textCanvas.requestPaint()
            }
        }
        Connections {
            target: timeline
            function onFpsChanged() {
                textCanvas.requestPaint()
            }
        }
        Connections {
            target: style
            function onStyleChanged() {
                textCanvas.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.fillStyle = style.dark ? "white" : "black"
            ctx.font = "15px 'JetBrains Mono'"

            var minInterval = 25
            var maxInterval = Math.abs(mapY(1) - mapY(0))
            var interval = maxInterval
            interval = interval / Math.pow(2, Math.floor(Math.log2(interval/minInterval)))
            var offset = mapY(0) % interval

            for (var t = mapY(timeline.yIn)+offset; t < mapY(timeline.yOut); t+=interval) {
                var y = Math.round(t)
                ctx.fillText(Math.round(unmapY(t)*1000)/1000, 0+5, y-5)
            }
        }
    }
}
