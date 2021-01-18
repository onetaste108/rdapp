import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

Rectangle {
    color: "transparent"
    property real maxChars: 2000
    // color: "red"
    id: codeEditor
    property variant s: style
    function setText(code) {
        var newText = textArea.text + code
        if (newText.length > maxChars) {
            newText = newText.slice(newText.length - maxChars)
        }
        textArea.text = newText
        flick.contentY = textArea.height - flick.height
    }
    Connections {
        target: con
        function onLogChanged(log) {
            codeEditor.setText(log)
        }
    }
    function clear() {
        textArea.text = ""
    }

    Item {
        anchors.fill: parent
        opacity: 0
        Flickable {
            id: flick
            anchors.fill: parent
            interactive: false
            clip: true
            contentWidth: width
            contentHeight: textArea.height

            Text {
                id: textArea
                width: parent.width
                // height: implicitHeight < flick.height ? flick.height : implicitHeight
                // readOnly: true
                color: s.foreground
                font.pixelSize: 12
                // tabStopDistance: 30
                wrapMode: Text.Wrap
            }
            ScrollHelper {
                flickable: flick
                anchors.fill: parent
            }
        }
    }


    LinearGradient {
        id: mask
        anchors.fill: parent
        start: Qt.point(0, 0)
        end: Qt.point(0, height)
        gradient: Gradient {
            GradientStop { position: 0; color: Qt.rgba(1,1,1,0) }
            GradientStop { position: 0.7; color: Qt.rgba(1,1,1,1) }
        }
        visible: false
    }

    OpacityMask {
        anchors.fill: parent
        source: flick
        maskSource: mask
    }

}