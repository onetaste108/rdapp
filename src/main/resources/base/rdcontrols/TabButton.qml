import QtQuick 2.15
import QtQuick.Controls 2.15

TabButton {
    id: control
    text: qsTr("Button")

    contentItem: Text {
        text: control.text
        font: control.font
        color: "red"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        color: style.dark ? "white" : "black"
        opacity: enabled ? 0.3 : 0
        border.color: control.down ? "#17a81a" : "#21be2b"
    }
}