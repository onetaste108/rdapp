import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import "rdcontrols" as RD

TabButton {
    property variant mstyle: style
    property bool selected: false
    property string src: undefined
    id: control
    width: 40
    height: 40
    // y: 0
    focusPolicy: Qt.NoFocus
    contentItem: Item {
    }

    background: Item {
        implicitWidth: parent.height
        implicitHeight: parent.height
        
        Rectangle {
            anchors.fill: parent
            opacity: selected ? 1 : (hovered ? 0.1 : 0)
            color: selected ? mstyle.background : (mstyle.dark ? "white" : "black")
        }
        Image {
            anchors.centerIn: parent
            // anchors.margins: 6
            id: test
            source: src
            // antialiasing: true
            visible: false

        }
        ColorOverlay{
            anchors.fill: test
            source: test
            color: selected ? style.accent : style.foreground
            // antialiasing: true
        }
        
    }
}
