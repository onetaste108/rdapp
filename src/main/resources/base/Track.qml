import QtQuick 2.15
import QtQml.Models 2.15
import QtQuick.Shapes 1.15



Item {
    id: trackArea
    property variant s: style
    clip: true
    function mapX(x) {
        return ((x-timeline.xIn) / (timeline.xOut-timeline.xIn)) * width
    }
    function unmapX(x) {
        return ((x / width) * (timeline.xOut-timeline.xIn)) + timeline.xIn
    }
    function mapY(y) {
        return ((y-timeline.yIn) / (timeline.yOut-timeline.yIn)) * height
    }
    function unmapY(y) {
        return ((y / height) * (timeline.yOut-timeline.yIn)) + timeline.yIn
    }
    MouseArea {
        anchors.fill: parent
        property real px: 0
        property real py: 0
        property real hotx: 0
        property real hoty: 0
        onClicked: {
            if (mouse.modifiers == Qt.ControlModifier) {
                timeline.addKeyframe(unmapX(mouseX), unmapY(mouseY))
            }
        }
        onPressed: {
            px = mouseX
            py = mouseY
            hotx = mouseX
            hoty = mouseY
        }
        onPositionChanged: {
            if (mouse.modifiers == Qt.AltModifier) {
                var fact = 0.995
                var sx = Math.pow(fact, (mouseX-px))
                var sy = Math.pow(fact, (-mouseY+py))
                var mx = unmapX(hotx)
                var my = unmapY(hoty)
                var xIn = timeline.xIn
                var xOut = timeline.xOut
                var yIn = timeline.yIn
                var yOut = timeline.yOut
                var xl = xOut - xIn
                var yl = yOut - yIn
                var xhl = mx-xIn
                var yhl = yl/2
                timeline.setGrid(
                    (xIn-mx)*sx+mx, (xOut-mx)*sx+mx,
                    (yIn-my)*sy+my, (yOut-my)*sy+my
                )
            } else {
                timeline.setGrid(
                        timeline.xIn - (unmapX(mouseX)-unmapX(px)), timeline.xOut - (unmapX(mouseX)-unmapX(px)),
                        timeline.yIn - (unmapY(mouseY)-unmapY(py)), timeline.yOut - (unmapY(mouseY)-unmapY(py))
                    )
            }

            px = mouseX
            py = mouseY
        }
    }


    Canvas {
        id: pathCanvas
        anchors.fill: parent
        Connections {
            target: timeline
            function onPathChanged() {
                pathCanvas.requestPaint()
            }
        }
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var pts = timeline.getPath()
            if (pts.length > 0) {

                if (pts[0][0][0] > timeline.xIn) {
                    ctx.beginPath()
                    ctx.strokeStyle = s.foreground
                    ctx.moveTo(0, mapY(pts[0][0][1]))
                    ctx.lineTo(mapX(pts[0][0][0]), mapY(pts[0][0][1]))
                    ctx.stroke()
                }
                if (pts[pts.length-1][0][0] < timeline.xOut) {
                    ctx.beginPath()
                    ctx.strokeStyle = s.foreground
                    ctx.moveTo(width, mapY(pts[pts.length-1][0][1]))
                    ctx.lineTo(mapX(pts[pts.length-1][0][0]), mapY(pts[pts.length-1][0][1]))
                    ctx.stroke()
                }

                ctx.strokeStyle = s.foreground
                ctx.beginPath()            
                for (var i = 0; i < pts.length; i++) {
                    if (i == 0) {
                        ctx.moveTo(mapX(pts[i][0][0]), mapY(pts[i][0][1]))
                    } else {
                        ctx.bezierCurveTo(
                            mapX(pts[i-1][2][0]), mapY(pts[i-1][2][1]),
                            mapX(pts[i][1][0]), mapY(pts[i][1][1]),
                            mapX(pts[i][0][0]), mapY(pts[i][0][1]))
                    }
                }
                ctx.stroke()
            }
        }
    }


    DelegateModel {
        id: trackModel
        model: timeline

        delegate: Item {
            id: keyframeHandle

            // console.log(posx[0][0])
            x: mapX(keyframe[0][0])
            y: mapY(keyframe[0][1])

            Item {
                id: inHandle
                x: mapX(keyframe[1][0]) - keyframeHandle.x
                y: mapY(keyframe[1][1]) - keyframeHandle.y
                Shape {
                    opacity: 1
                    ShapePath {
                        strokeColor: s.accent
                        PathLine {
                            x: -inHandle.x; y: -inHandle.y
                        }
                    }
                }
                Rectangle {
                    width: 10
                    height: 10
                    radius: 5
                    anchors.centerIn: parent
                    color: s.accent
                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: {
                            var pos = mapToItem(trackArea, mouseX, mouseY)
                            timeline.moveInp(index, unmapX(pos.x), unmapY(pos.y), mouse.modifiers != Qt.AltModifier)
                        }
                    }
                }
            }
            Item {
                id: outHandle
                x: mapX(keyframe[2][0]) - keyframeHandle.x
                y: mapY(keyframe[2][1]) - keyframeHandle.y
                Shape {
                    opacity: 1
                    ShapePath {
                        strokeColor: s.accent
                        PathLine {
                            x: -outHandle.x; y: -outHandle.y
                        }
                    }
                }
                Rectangle {
                    width: 10
                    height: 10
                    radius: 5
                    anchors.centerIn: parent
                    color: s.accent
                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: {
                            var pos = mapToItem(trackArea, mouseX, mouseY)
                            timeline.moveOut(index, unmapX(pos.x), unmapY(pos.y), mouse.modifiers != Qt.AltModifier)
                        }
                    }
                }

            }
            Rectangle {
                id: kf
                width: 18
                height: 18
                radius: 9
                border.color: s.accent
                anchors.centerIn: parent
                color: hoverArea.containsMouse ? s.accent : s.background
                MouseArea {
                    id: hoverArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                }
                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    onPositionChanged: {
                        var pos = mapToItem(trackArea, mouseX, mouseY)
                        timeline.moveKeyframe(index, unmapX(pos.x), unmapY(pos.y))
                    }
                    onClicked: {
                        if (mouse.modifiers == Qt.ControlModifier) {
                            timeline.removeKeyframe(index)
                        }
                    }
                    onDoubleClicked: {
                        input1.selectAll()
                    }
                }
                ControlInput {
                    id: input1
                    visible: active ? true : (hoverArea.containsMouse)
                    val: keyframe[0][1]
                    type: "float"
                    height: 30
                    width: 100
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: -35
                    use_slider: false
                    textInput.horizontalAlignment: TextEdit.AlignHCenter
                    onValueChanged: {
                        timeline.setValue(index, newval)
                    }
                }
            }
        }
        // Item {
        //     x: mapX(outx)
        //     y: mapY(outx)
        //     Rectangle {
        //         width: 10
        //         height: 10
        //         radius: 10
        //         anchors.centerIn: parent
        //         color: "#FF0"
        //     }
        // }
    }

    Repeater {
        anchors.fill: parent
        model: trackModel
    }



    // Canvas {
    //     id: gridCanvas
    //     anchors.fill: parent
    //     Connections {
    //         target: timeline
    //         function onGridChanged() {
    //             gridCanvas.requestPaint()
    //         }
    //     }
    //     onPaint: {
    //         var ctx = getContext("2d")
    //         ctx.clearRect(0, 0, width, height)
    //         ctx.strokeStyle = "#FFF"
    //         ctx.beginPath()
            
    //         for (var i = 0; i < trackModel.count; i++) {
    //             var k = timeline.getKeyframe(i)
    //             var x = mapX(k[0])
    //             var y = mapY(k[1])
    //             if (i == 0) {
    //                 ctx.moveTo(x, y)
    //             } else {
    //                 var inx = mapX(k[2])
    //                 var iny = mapY(k[3])
    //                 ctx.bezierCurveTo(poutx, pouty, inx, iny, x, y)
    //             }
    //             poutx = mapX(k[4])
    //             pouty = mapY(k[5])
    //         }
    //         ctx.stroke()
    //     }
    // }
}