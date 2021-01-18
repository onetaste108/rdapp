import QtQuick 2.15
import GL 0.1
    
Item {
    property bool targetVisible: true

    GLCanvas {
        id: rdcanvas
        objectName: "rdcanvas"
        anchors.fill: parent
        property rect renderViewport: Qt.rect(-10, -10, 2000, 2000)
        Component.onCompleted: con.qml_connect(rdcanvas)
    }

    Canvas {
        id: targetCanvas
        visible: targetVisible
        width: rdcanvas.renderViewport.width
        height: rdcanvas.renderViewport.height
        x: rdcanvas.renderViewport.x
        y: rdcanvas.renderViewport.y
        opacity: 0.25
        Connections {
            target: style
            function onStyleChanged() {
                targetCanvas.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = style.foreground
            var linewidth = 2
            ctx.lineWidth = linewidth
            ctx.beginPath()
            var line = width / 6
            ctx.moveTo(0+linewidth, 0+linewidth)
            ctx.lineTo(line, 0+linewidth)
            ctx.moveTo(width-line, 0+linewidth)
            ctx.lineTo(width-linewidth, 0+linewidth)
            ctx.lineTo(width-linewidth, line)
            ctx.moveTo(width-linewidth, height-line)
            ctx.lineTo(width-linewidth, height-linewidth)
            ctx.lineTo(width-line, height-linewidth)
            ctx.moveTo(line, height-linewidth)
            ctx.lineTo(0+linewidth, height-linewidth)
            ctx.lineTo(0+linewidth, height-line)
            ctx.moveTo(0+linewidth, line)
            ctx.lineTo(0+linewidth, 0+linewidth)
            ctx.stroke()
        }
    }
}