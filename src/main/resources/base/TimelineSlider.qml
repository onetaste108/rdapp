import QtQuick 2.15

Item {
    Canvas {
        id: sliderCanvas
        anchors.fill: parent
        Connections {
            target: timeline
            function onGridChanged() {
                sliderCanvas.requestPaint()
            }
        }
        Connections {
            target: timeline
            function onFpsChanged() {
                sliderCanvas.requestPaint()
            }
        }
        Connections {
            target: style
            function onStyleChanged() {
                sliderCanvas.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = style.dark ? "white" : "black"
            ctx.lineWidth = 2
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

            ctx.stroke()
            
        }
    }
}