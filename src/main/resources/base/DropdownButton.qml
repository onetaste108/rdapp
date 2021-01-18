import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "rdcontrols" as RD

Item {
    id: containter
    width: parent.width
    height: 30
    property bool active: true
    property bool hovered: hoverArea.hovered
    property bool pressed: hoverArea.containsPress
    property string name: "Dropdown"
    property variant s: style
        
    
    Rectangle {
        anchors.fill: containter
        color: parent.pressed ? s.accent : (s.dark ? "white" : "black")
        opacity: parent.pressed ? 1 : (parent.hovered ? 0.1 : 0.05)
    }
    
    RowLayout {
        anchors.fill: parent
        spacing: 0
        Label {
            text: name
            color: containter.pressed ? s.background : s.foreground
            Layout.preferredWidth: 150
            Layout.fillHeight: true
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            leftPadding: (height-contentHeight)
            opacity: 0.7
        }
    }
    

    MouseArea {
        anchors.fill: parent
        id: hoverArea
        property bool hovered: containsMouse
        // acceptedButtons: Qt.NoButton
        hoverEnabled: true
        propagateComposedEvents: true
        onPressed: {
            containter.active = !containter.active
        }
    }    

}