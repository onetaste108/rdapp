import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

Item {
        property string src: undefined
        property real margins: 0
        property color color: "red"
        property alias img: test
        property real rot: 0

        Image {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            id: test
            source: src
            visible: false
            antialiasing: false

        }

        ColorOverlay{
            anchors.fill: test
            source: test
            color: parent.color
            antialiasing: true
            transform: Rotation {
                angle: rot
                origin.x: test.width/2
                origin.y: test.height/2
            }
        }

        
        
}
