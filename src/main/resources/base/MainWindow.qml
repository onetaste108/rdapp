import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import GL 0.1
import QtQuick.Dialogs 1.0
import "rdcontrols" as RD
import QtQml 2.15



ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1280
    height: 720
    title: "rdapp - " + con.version()
    minimumWidth: 400
    minimumHeight: 300
    color: style.background
    property variant prevVisibility: visibility

    Item {
        id: base
        anchors.fill: parent
        focus: true

        Connections {
            target: con
            function onUnfocus() {
                base.forceActiveFocus()
            }
        }

        // Rectangle {
        //     x: 40
        //     y: 40
        //     width: 20
        //     height: 20
        //     radius: 10
        //     color: parent.focus ? "green" : "red"
        //     z: 10
        // }

        Keys.onPressed: {
            if (event.key == Qt.Key_F11) {
                if (mainWindow.visibility != Window.FullScreen) {
                    mainWindow.prevVisibility = mainWindow.visibility
                    mainWindow.visibility = Window.FullScreen
                } else {
                    mainWindow.visibility = mainWindow.prevVisibility
                }
            }
            if (event.key == Qt.Key_F10) {
                viewport.targetVisible = !viewport.targetVisible
            }
            if (event.key == Qt.Key_F9) {
                log.visible = !log.visible
            }
            if (event.key == Qt.Key_Space) {
                con.playPause()
            }
            if (event.key == Qt.Key_Backspace) {
                log.clear()
            }
            if (event.modifiers & Qt.ControlModifier && event.key == Qt.Key_S) {
                if (event.modifiers & Qt.ShiftModifier) {
                    saveAsFile.folder = con.project_path()
                    saveAsFile.open()
                } else {
                    if (con.project_path().length > 0) {
                        con.save_as(con.project_path())
                    } else {
                        saveAsFile.folder = con.project_path()
                        saveAsFile.open()
                    }
                }
            }
            if (event.key == Qt.Key_0) {
                con.set_cam(0)
            }
            if (event.key == Qt.Key_1) {
                con.set_cam(1)
            }
            if (event.key == Qt.Key_2) {
                con.set_cam(2)
            }
            if (event.key == Qt.Key_3) {
                con.set_cam(3)
            }
            if (event.key == Qt.Key_4) {
                con.set_cam(4)
            }
            if (event.key == Qt.Key_5) {
                con.set_cam(5)
            }
            if (event.key == Qt.Key_6) {
                con.set_cam(6)
            }
        }

        DropArea {
            id: dropArea
            anchors.fill: parent
            onDropped: {
                con.drop(drop.urls)
                configProject.update()
                dropArea.focus = false
                base.forceActiveFocus()
            }
        }

        // MouseArea {
        //     anchors.fill: parent
        //     onClicked: {
        //         console.log("CLIK")
        //     }
        // }

        SplitView {
            id: split_else_menu
            handle: RD.SplitHandle {
                handle: SplitHandle
                op: 0.1
            }
            anchors.fill: parent
            SplitView {
                id: split_rd_timeline
                handle: RD.SplitHandle {
                    id: split_rd_timeline_handle
                    handle: SplitHandle
                    op: 0.1
                }
                SplitView.fillWidth: true
                SplitView.minimumWidth: 64
                SplitView.fillHeight: true
                orientation: Qt.Vertical
                Item {
                    SplitView.fillWidth: true
                    SplitView.minimumHeight: 64
                    SplitView.fillHeight: true
                    clip: true
                    Viewport {
                        id: viewport
                        anchors.fill: parent
                    }
                    Logger {
                        id: log
                        height: 200
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.bottomMargin: -15
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        opacity: 0.5
                    }
                }
                Timeline {
                    visible: timeline.visible
                    SplitView.fillWidth: true
                    SplitView.preferredHeight: 150
                    SplitView.minimumHeight: 80
                }
                
            }
            Rectangle {
                id: menu
                SplitView.fillHeight: true
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 270
                color: "transparent"
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: header.height
                        Rectangle {
                            anchors.fill: parent
                            color: style.dark ? "white" : "black"
                            opacity: 0.1
                        }
                        RowLayout {
                            width: parent.width
                            id: header
                            Item {
                                Layout.fillHeight: true
                                Layout.fillWidth: true
                                RD.Icon {
                                    anchors.fill: parent
                                    anchors.topMargin: 4
                                    anchors.leftMargin: 10
                                    color: style.accent
                                    src: "../icons/rdapp.png"
                                }
                            }
                            Rectangle {
                                color: "red"
                                // Layout.fillHeight: true
                                Layout.fillWidth: true
                            }
                            TabBar {
                                id: bar
                                // Layout.fillWidth: true
                                // Layout.height: 30
                                // color: style.background
                                background: null
                                RDTabButton {
                                    selected: bar.currentIndex == 0
                                    src: "icons/prop.png"
                                }
                                RDTabButton {
                                    selected: bar.currentIndex == 1
                                    src: "icons/script.png"
                                }
                                RDTabButton {
                                    selected: bar.currentIndex == 2
                                    src: "icons/shader.png"
                                }
                                RDTabButton {
                                    selected: bar.currentIndex == 3
                                    src: "icons/setting.png"
                                }
                            }
                        }
                    }
                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: bar.currentIndex
                        Properties {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            // anchors.fill: parent
                        }


                        Item {
                            CodeEditor {
                                id: codeEditor
                                anchors.fill: parent
                                format: "py"
                                onSubmit: {
                                    con.runScript(code)
                                }
                                onVisibleChanged: {
                                    if (!visible) {
                                        unfocus()
                                    }
                                }
                            }
                            Connections {
                                target: con
                                function onCodeUpdated() {
                                    codeEditor.setText(con.getProjectCode())
                                }
                            }

                        }
                        Item {
                            id: activityTab
                            CodeEditor {
                                id: shaderEditor
                                anchors.fill: parent
                                format: "glsl"
                                Connections {
                                    target: con
                                    function onShaderUpdated(code) {
                                        shaderEditor.setText(con.getProjectShader())
                                    }
                                }
                                onSubmit: {
                                    con.setProjectShader(code)
                                }
                                onVisibleChanged: {
                                    if (!visible) {
                                        unfocus()
                                    }
                                }
                            }
                        }

                        Settings {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                        }
                    }
                    Rectangle {
                        id: buttonsContainer
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        color: "transparent"
                        property real mmargins: 6
                        property real mspacing: 6

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: buttonsContainer.mmargins
                            spacing: buttonsContainer.mspacing
                            RowLayout {
                                Layout.fillHeight: true
                                Layout.fillWidth: true
                                spacing: buttonsContainer.mspacing
                                RD.Button {
                                    visible: con.state == "LIVE"
                                    text: "Snap"
                                    Layout.preferredWidth: 10
                                    Layout.fillHeight: true
                                    Layout.fillWidth: true
                                    onClicked: {
                                        con.snap()
                                    }
                                }
                                RD.Button {
                                    visible: con.state == "LIVE"
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 10
                                    Layout.fillWidth: true
                                    onClicked: {
                                        con.render()
                                    }
                                    text: "Render"
                                }
                                RD.Button {
                                    visible: con.state == "RENDER"
                                    textcolor: mstyle.background
                                    bgcolor: mstyle.accent
                                    bgopacity: 1
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 10
                                    Layout.fillWidth: true
                                    onClicked: {
                                        con.stop_render()
                                    }
                                    text: "Stop"
                                }
                            }
                            RowLayout {
                                Layout.preferredHeight: 40
                                Layout.fillHeight: false
                                Layout.fillWidth: true
                                spacing: buttonsContainer.mspacing
                                RD.Button {
                                    text: "Save"
                                    Layout.preferredWidth: 10
                                    Layout.fillHeight: true
                                    Layout.fillWidth: true
                                    onClicked: {
                                        saveAsFile.open()
                                    }
                                    FileDialog {
                                        id: saveAsFile
                                        selectExisting: false
                                        title: "Save Project As..."
                                        nameFilters: [ "rdapp project (*.rd)" ]
                                        folder: shortcuts.documents + "/rdapp/projects/rdproject"
                                        onAccepted: {
                                            var path = saveAsFile.fileUrl.toString();
                                            path = path.replace(/^(file:\/{3})/,(Qt.platform.os == "windows" ? "" : "/"));
                                            var cleanPath = decodeURIComponent(path);
                                            console.log(cleanPath)
                                            con.save_as(cleanPath)
                                        }
                                        onRejected: {
                                        }
                                    }
                                }
                                RD.Button {
                                    Layout.fillHeight: true
                                    Layout.preferredWidth: 10
                                    Layout.fillWidth: true
                                    text: "Open"
                                    onClicked: {

                                        loadFile.open()
                                    }
                                    FileDialog {
                                        id: loadFile
                                        // selectExisting: false
                                        folder: shortcuts.documents + "/rdapp/projects/"
                                        title: "Open Project..."
                                        nameFilters: [ "rdapp project (*.rd)" ]
                                        onAccepted: {
                                            var path = loadFile.fileUrl.toString();
                                            path = path.replace(/^(file:\/{3})/,(Qt.platform.os == "windows" ? "" : "/"));
                                            var cleanPath = decodeURIComponent(path);
                                            console.log(cleanPath)
                                            con.load(cleanPath)
                                        }
                                        onRejected: {
                                        }
                                    }
                                }
                                RD.Button {
                                    text: "New"
                                    Layout.preferredWidth: 10
                                    Layout.fillHeight: true
                                    Layout.fillWidth: true
                                    onClicked: {
                                        con.default()
                                    }
                                }
                            }
                        }
                    }      
                }
            }
        }

        Rectangle {
            id: openTimeline
            x: 0
            y: viewport.height - height
            width: viewport.width
            height: 30
            color: style.dark ? "white" : "black"
            opacity: openTimelineMouseAre.containsMouse ? 0.05 : 0
            MouseArea {
                id: openTimelineMouseAre
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    timeline.visible = !timeline.visible
                }
            }
        }
        RD.Icon {
            id: openTimelineIcon
            anchors.fill: openTimeline
            margins: 0
            color: openTimeline.color
            img.anchors.centerIn: openTimelineIcon
            src: "../icons/arrow.png"
            rot: timeline.visible ? 0 : 180
            opacity: openTimeline.opacity * 10
        }
        Rectangle {
            id: openMenu
            x: viewport.width - width
            y: 0
            height: viewport.height
            width: 30
            color: style.dark ? "white" : "black"
            opacity: openMenuMouseAre.containsMouse ? 0.05 : 0
            MouseArea {
                id: openMenuMouseAre
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    menu.visible = !menu.visible
                }
            }
        }
        RD.Icon {
            id: openMenuIcon
            anchors.fill: openMenu
            margins: 0
            color: openMenu.color
            img.anchors.centerIn: openMenuIcon
            src: "../icons/arrow.png"
            rot: !menu.visible ? 90 : 270
            opacity: openMenu.opacity * 10
        }

    
    }

}