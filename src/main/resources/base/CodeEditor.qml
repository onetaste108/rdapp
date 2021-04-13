import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15

Rectangle {
    color: "transparent"
    // border.color: "#444"
    id: codeEditor
    signal submit(string code)
    property string format: "py"
    property variant txtarea: textArea
    function unfocus() {
        textArea.focus = false
        base.forceActiveFocus()
    }
    function setText(code) {
        textArea.text = codeEditorContext.formatCode(code, codeEditor.format)
        flick.contentX = 0
        flick.contentY = 0
    }

    ScrollView {
        id: scroll
        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.contentItem: Rectangle {
            opacity: parent.pressed ? 1 : (parent.hovered ? 0.5 : 0)
            color: parent.pressed ? style.accent : (style.dark ? "white" : "black")
            implicitHeight: 10
            implicitWidth: 10
        }
        anchors.fill: parent
        Flickable {
            id: flick
            anchors.fill: parent
            clip: true
            contentWidth: textArea.width
            contentHeight: textArea.height

            function ensureVisible(r)
            {
                if (contentX >= r.x)
                    contentX = r.x;
                else if (contentX+width <= r.x+r.width)
                    contentX = r.x+r.width-width;
                if (contentY >= r.y)
                    contentY = r.y;
                else if (contentY+height <= r.y+r.height)
                    contentY = r.y+r.height-height;
            }

            Rectangle {
                visible: textArea.focus
                color: style.dark ? "white" : "black"
                opacity: 0.1
                width: flick.width
                y: textArea.cursorRectangle.y
                height: textArea.cursorRectangle.height
            }

            TextArea {
                id: textArea
                width: implicitWidth < flick.width ? flick.width : implicitWidth
                height: implicitHeight < flick.height ? flick.height : implicitHeight
                textFormat: TextEdit.RichText
                selectByMouse: true
                color: "white"
                // font.pointSize: 10
                tabStopDistance: 30
                property bool formatted: true
                property bool cursorAid: false
                signal submit(string code)

                onActiveFocusChanged: {
                    if (base.focus) focus = false
                }

                cursorDelegate: Rectangle {
                    id: myCursor
                    visible: textArea.focus
                    color: style.foreground
                    width: 2
                    Timer{
                        id: timer
                        interval: 500
                        running: true
                        repeat: true
                        onTriggered: myCursor.opacity = myCursor.opacity === 0 ? 1 : 0
                    }
                }


                onCursorRectangleChanged: if (!cursorAid) flick.ensureVisible(cursorRectangle)

                onTextChanged: {
                    if (formatted) formatted = false
                    else {
                        formatted = true
                        var cursor = cursorPosition
                        cursorAid = true
                        colorize()
                        cursorAid = false
                        cursorPosition = cursor
                    }
                }

                Connections {
                    target: style
                    function onStyleChanged() {
                        textArea.onTextChanged()
                    }
                }

                Keys.onPressed: {
                    if ((event.key == Qt.Key_Return) && (event.modifiers == Qt.ControlModifier)) {
                        codeEditor.submit(getText(0, length))
                        event.accepted = true
                        unfocus()
                    }
                    if (event.key == Qt.Key_Escape) {
                        unfocus()
                    }
                }
                Component.onCompleted: {
                    colorize()
                }
                function colorize() {
                    text = codeEditorContext.formatCode(getText(0, length), codeEditor.format)
                }

            }
            ScrollHelper {
                flickable: flick
                anchors.fill: parent
            }
        }
    }
}