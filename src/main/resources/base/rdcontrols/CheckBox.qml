import QtQuick 2.12
import QtQuick.Controls 2.12

CheckBox {
    id: control
    checked: false
    indicator: Rectangle {
        anchors.fill: parent
        color: "black"
        border.color: "white"
        Rectangle {
            anchors.fill: parent
            anchors.margins: 4 
            color: "white"
            visible: control.checked
        }
    }
}