import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3


Item {
    id: inputControl
    property string type: "str"
    property bool hovered: textField.hovered || sliderHoverMouse.containsMouse
    property bool active: textField.focus
    property bool use_slider: type == "float" || type == "int" || type == "path" || type == "file"
    property alias textInput: textField

    property string val: ""
    signal valueChanged(string newval)
    function selectAll() {
        textField.forceActiveFocus()
        textField.selectAll()
    }

    Rectangle {
        id: background
        anchors.fill: parent
        color: inputControl.active ? s.accent : (s.dark ? "white" : "black")
        opacity: inputControl.active ? 1 : (inputControl.hovered ? 0.1 : 0)
    }

    RowLayout {
        id: inputLayout
        anchors.fill: parent
        spacing: 0

        TextField {
            Layout.fillWidth: true
            Layout.fillHeight: true
            function process(v,t) {
                if (t == "float") {
                    v = parseFloat(v);
                    v = Math.round(v*10000)/10000;
                    return v
                }
                return v
            }
            
            text: process(val, type)


            id: textField
            // verticalAlignment: TextEdit.AlignVBottom
            // horizontalAlignment: TextEdit.AlignHCenter
            selectByMouse: true
            color: inputControl.active ? s.background : s.accent
            selectionColor: s.dark ? Qt.darker(s.accent, 1.2) : Qt.lighter(s.accent, 1.2)
            background: Rectangle {
                color: "transparent"
            }
            onEditingFinished: {
                inputControl.valueChanged(text)
                text = Qt.binding(function(){return process(inputControl.val, inputControl.type)})
                focus = false
                base.forceActiveFocus()
            }
            Keys.onPressed: {
                if (event.key == Qt.Key_Escape) {
                    text = Qt.binding(function(){return process(inputControl.val, inputControl.type)})
                    focus = false
                    base.forceActiveFocus()
                }
            }
            Connections {
                target: slider
                function onMoved(nval) {
                    if (inputControl.type == "int") {
                        inputControl.valueChanged(Math.floor(nval));
                    } else {
                        inputControl.valueChanged(parseFloat(val) + nval);
                    }
                }
            }
        }
        Item {
            id: slider
            visible: inputControl.use_slider
            Layout.fillHeight: true
            Layout.preferredWidth: 10
            property real step: inputControl.type == "int" ? 0.1 : 0.01
            signal moved(real x)
            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                hoverEnabled: true
                id: sliderHoverMouse
            }
            MouseArea {
                id: sliderMouse
                anchors.fill: parent
                preventStealing: true
                property real pmouseX: 0
                property real pmouseY: 0
                property int rememderInt: 0
                onPressed: {
                    slider.forceActiveFocus()
                    // con.rememberCursor()
                    pmouseX = mouseX
                    pmouseY = mouseY
                    if (inputControl.type == "int") {
                        rememderInt = parseInt(val)
                    }
                    // focus: true
                }
                onReleased: {
                    focus = false
                    base.forceActiveFocus()
                }
                onPositionChanged: {
                    var dx = mouseX-pmouseX
                    var dy = mouseY-pmouseY
                    if (inputControl.type != "int") {
                        pmouseX = mouseX
                        pmouseY = mouseY
                    }
                    if (!((dx == 0) && (dy == 0))) {
                        slider.moved(dx*slider.step - dy*slider.step)
                        // con.resetCursor()
                    }
                }
                onClicked: {
                    if (type == "path" || type == "file") {
                        openFile.open()
                    }
                }
            }
            Rectangle {
                id: sliderBackground
                anchors.fill: parent
                color: sliderMouse.pressed ? s.accent : ((inputControl.active ? !s.dark : s.dark) ? "white" : "black")
                opacity: sliderMouse.pressed ? 1 : (sliderHoverMouse.containsMouse ? 0.2 : (textField.hovered ? 0.1 : 0))
            }

            Keys.onPressed: {
                if (event.key == Qt.Key_Control) {
                    slider.step /= 10
                }
                if (event.key == Qt.Key_Shift) {
                    slider.step *= 10
                }
            }
        }
    }

    FileDialog {
        id: openFile
        selectFolder: type == "path"
        title: "Please choose a " + type
        folder: ""
        onAccepted: {
            var path = openFile.fileUrl.toString();
            path = path.replace(/^(file:\/{3})/,"/");
            var cleanPath = decodeURIComponent(path);
            inputControl.valueChanged(cleanPath)
        }
        onRejected: {
        }
    }

}