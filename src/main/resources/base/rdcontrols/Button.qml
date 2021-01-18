import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    property color bgcolor: control.down ? mstyle.accent : (mstyle.dark ? "white" : "black")
    property color textcolor: control.down ? mstyle.background : mstyle.foreground
    property real bgopacity: control.down ? 1 : (hovered ? 0.2 : 0.05)
    property variant mstyle: style
    focusPolicy: Qt.NoFocus
    // implicitWidth: 100
    // implicitHeight: 100

    contentItem: Text {
        // width: 300
        // height: parent.height
        text: control.text
        font: control.font
        color: textcolor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        opacity: enabled ? 1.0 : 0.3
    }

    background: Rectangle {
        id: bg
        color: bgcolor
        // anchors.fill: parent
        // implicitWidth: parent.width
        // implicitHeight: parent.height
        // color: control.down ? Qt.lighter(control.color, 2) : (hovered ? Qt.lighter(control.color, 1.5) : control.color)
        // border.color: "white"
        // border.width: 1
        radius: 2
        opacity: bgopacity
    }
}