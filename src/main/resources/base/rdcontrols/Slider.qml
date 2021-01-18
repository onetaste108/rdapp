import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes 1.15


Item {
    id: base
    signal moved(real x, real y)

    MouseArea {
        anchors.fill: parent
        drag.target: anchor
        drag.threshold: 0
        drag.smoothed: false
        preventStealing: true
        property real pmouseX: 0
        property real pmouseY: 0
        onPressed: {
            pmouseX = mouseX
            pmouseY = mouseY
        }
        onReleased: {
            anchor.x = 0
            anchor.y = 0
        }
        onPositionChanged: {
            parent.moved(mouseX-pmouseX, mouseY-pmouseY)
            pmouseX = mouseX
            pmouseY = mouseY
        }
    }

    Shape {
        z: 100
        anchors.centerIn: parent
        opacity: 1
        ShapePath {
            PathLine {
                x: anchor.x; y: anchor.y
            }
        }
    }

    Item {
        id: anchor
        z: 100
        width: parent.width
        height: parent.height
        Rectangle {
            // color: "white"
            color: "transparent"
            anchors.fill: parent
            anchors.margins: 2
            Image {
                anchors.fill: parent
                source: "images/move-01.png"
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        border.color: "#777"
        color: "#000"
        // radius: 3
    }

}