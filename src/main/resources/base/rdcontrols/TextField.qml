import QtQuick 2.15
import QtQuick.Controls 2.15

TextField {
    id: control
    color: style.accent
    selectByMouse: true
    background: Rectangle {
        color: style.dark ? "white" : "black"
        opacity: (control.focus ? 0.2 : (control.hovered ? 0.1 : 0))
        // border.color: control.focus ? "#aaa" : "#666"
        // radius: 3
    }
}
