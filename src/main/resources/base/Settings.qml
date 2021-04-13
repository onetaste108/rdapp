import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "rdcontrols" as RD

Rectangle {
    id: propertiesBase
    property variant s: style
    color: "transparent"
    // clip: true
    ScrollView {
        id: scroll

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.contentItem: Rectangle {
            opacity: parent.pressed ? 1 : (parent.hovered ? 0.5 : 0)
            color: parent.pressed ? style.accent : (style.dark ? "white" : "black")
            implicitHeight: 6
            implicitWidth: 6
        }
        anchors.fill: parent
        Flickable {
            id: flick
            anchors.fill: parent
            anchors.margins: 10
            anchors.bottomMargin: 0

            clip: true
            // contentWidth: textArea.width
            contentHeight: textArea.height

            ColumnLayout {
                id: textArea
                width: parent.width
                spacing: 0
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    DropdownButton {
                        id: dropProject
                        Layout.fillWidth: true
                        name: "Project"
                        active: true
                    }
                    Setting {
                        visible: dropProject.active
                        Layout.fillWidth: true
                        model: configProject
                    }
                }
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    DropdownButton {
                        id: dropGeneral
                        Layout.fillWidth: true
                        name: "Output"
                    }
                    Setting {
                        visible: dropGeneral.active
                        Layout.fillWidth: true
                        model: configGeneral
                    }
                }
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    DropdownButton {
                        id: dropRender
                        Layout.fillWidth: true
                        name: "Render"
                        active: false
                    }
                    Setting {
                        visible: dropRender.active
                        Layout.fillWidth: true
                        model: configRender
                    }
                }
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    DropdownButton {
                        id: dropPreview
                        Layout.fillWidth: true
                        name: "Preview"
                        active: false
                    }
                    Setting {
                        visible: dropPreview.active
                        Layout.fillWidth: true
                        model: configPreview
                    }
                }



                RD.Button {
                    text: "Scan 3D"
                    // Layout.preferredWidth: 10
                    Layout.topMargin: 10
                    Layout.preferredHeight: 30
                    Layout.fillWidth: true
                    onClicked: {
                        con.scan()
                    }
                }


                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
            }


            ScrollHelper {
                flickable: flick
                anchors.fill: parent
            }
        }
    }
}