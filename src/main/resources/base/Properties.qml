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

            ListView {
                id: textArea
                width: parent.width
                height: contentHeight
                model: md
                spacing: 0
                interactive: false
                delegate: Item {
                    id: containter
                    width: parent.width
                    height: 30
                    property bool hovered: hoverArea.hovered || checkBox.hovered || input1.hovered || input2.hovered || input3.hovered || input4.hovered
                    function activateTimeline() {
                        if (tp == "float") {
                            if (con.timelinePropertyName == name && timeline.visible) {
                                timeline.visible = false
                            } else {
                                timeline.visible = true
                                con.setTimeline(name)
                            }
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        id: hoverArea
                        property bool hovered: containsMouse
                        // acceptedButtons: Qt.NoButton
                        hoverEnabled: true
                        propagateComposedEvents: true
                        onClicked: {
                            if (mouse.modifiers == Qt.ControlModifier) {
                                activateTimeline()
                            }
                        }    
                        onDoubleClicked: {
                            activateTimeline()
                        }
                    }
                
                    RowLayout {
                        anchors.fill: parent
                        spacing: 0
                        Label {
                            text: name
                            color: (timeline.visible && con.timelinePropertyName == name) ? s.accent : s.foreground
                            Layout.preferredWidth: 150
                            Layout.fillHeight: true
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                            leftPadding: (height-contentHeight)
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 0 
                            Item {
                                visible: tp == "bool"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Item {
                                    x: 0
                                    y: 0
                                    height: parent.height
                                    width: height
                                    id: checkBox
                                    property bool active: val1 == "True"
                                    property bool hovered: checkBoxMouse.containsMouse
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: height
                                    Rectangle {
                                        id: checkBoxBox
                                        anchors.fill: parent
                                        anchors.margins: 5
                                        color: checkBox.active ? s.accent : (s.dark ? "white" : "black")
                                        opacity: checkBox.active ? 1 : 0.2

                                        MouseArea {
                                            id: checkBoxMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            onClicked: {
                                                if (checkBox.active) {
                                                    val1 = "False"
                                                } else {
                                                    val1 = "True"
                                                }
                                            }
                                        }
                                    }
                                    Rectangle {
                                        anchors.fill: checkBoxBox
                                        color: (checkBox.active ? !s.dark : s.dark) ? "white" : "black"
                                        opacity: checkBox.hovered ? 0.2 : 0
                                    }
                                }
                            }
                            ControlInput {
                                id: input1
                                visible: (ndim > 0) && (tp != "bool")
                                val: val1
                                type: tp
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                onValueChanged: {
                                    val1 = newval
                                }
                            }
                            ControlInput {
                                id: input2
                                visible: (ndim > 1) && (tp != "bool")
                                val: val2
                                type: tp
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                onValueChanged: {
                                    val2 = newval
                                }
                            }
                            ControlInput {
                                id: input3
                                visible: (ndim > 2) && (tp != "bool")
                                val: val3
                                type: tp
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                onValueChanged: {
                                    val3 = newval
                                }
                            }
                            ControlInput {
                                id: input4
                                visible: (ndim > 3) && (tp != "bool")
                                val: val4
                                type: tp
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                onValueChanged: {
                                    val4 = newval
                                }
                            }
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        color: s.dark ? "white" : "black"
                        opacity: parent.hovered ? 0.1 : 0
                    }
                }
            }
            // ColumnLayout {
            //     id: textArea
            //     width: parent.width
            //     spacing: 0


            //     Item {
            //         Layout.fillWidth: true
            //         Layout.fillHeight: true
            //     }
            // }


            ScrollHelper {
                flickable: flick
                anchors.fill: parent
            }
        }
    }
}
