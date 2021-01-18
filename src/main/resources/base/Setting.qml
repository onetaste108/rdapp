import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "rdcontrols" as RD

ListView {
    // anchors.fill: parent
    // anchors.margins: 10
    model: undefined
    spacing: 0
    height: contentHeight
    interactive: false
    delegate: Item {
        id: containter
        width: parent.width
        height: 30
        property bool hovered: hoverArea.hovered || checkBox.hovered || input1.hovered || input2.hovered || input3.hovered || input4.hovered
        MouseArea {
            anchors.fill: parent
            id: hoverArea
            property bool hovered: containsMouse
            acceptedButtons: Qt.NoButton
            hoverEnabled: true
            propagateComposedEvents: true
        }    
        
        RowLayout {
            anchors.fill: parent
            spacing: 0
            Label {
                text: name
                color: s.foreground
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
                        x: 5
                        y: 0
                        height: parent.height
                        width: height
                        id: checkBox
                        property bool active: val1 == "True"
                        property bool hovered: checkBoxMouse.containsMouse
                        Layout.fillHeight: true
                        // Layout.preferredWidth: height
                        Layout.fillWidth: true
                        Rectangle {
                            id: checkBoxBox
                            anchors.fill: parent
                            radius: width/2
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
                            radius: checkBoxBox.radius
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
                        if (tp == "file") {
                            configProject.update()
                        }
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