import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property var handle: undefined
    implicitWidth: 6
    implicitHeight: 6
    color: "transparent"
    property real op: 0.2
    Rectangle {
        anchors.fill: parent
        opacity: handle.hovered ? op*2 : op
        color: style.dark ? "white" : "black"
    }
}