import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import "rdcontrols" as RD

Rectangle {
    id: timelinePanel
    color: "transparent"
    clip: true
    property variant s: style
    function mapX(x) {
        return ((x-timeline.xIn) / (timeline.xOut-timeline.xIn)) * width
    }
    function unmapX(x) {
        return ((x / width) * (timeline.xOut-timeline.xIn)) + timeline.xIn
    }
    function mapY(y) {
        return ((y-timeline.yIn) / (timeline.yOut-timeline.yIn)) * trackArea.height
    }
    function unmapY(y) {
        return ((y / trackArea.height) * (timeline.yOut-timeline.yIn)) + timeline.yIn
    }
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            height: 20
            Rectangle {
                anchors.fill: parent
                color: (style.dark) ? "white" : "black"
                opacity: 0.05
            }
            TimelineSlider {
                anchors.fill: parent
                opacity: 0.05
            }
            Label {
                color: s.foreground
                text: Math.floor(timeline.xIn * timeline.fps)
                anchors.left: parent.left
                anchors.margins: 5
                font.pointSize: 10
                height: parent.height
                verticalAlignment: Text.AlignVCenter
            }
            Label {
                color: s.foreground
                text: Math.floor(timeline.xOut * timeline.fps)
                anchors.right: parent.right
                anchors.margins: 5
                font.pointSize: 10
                height: parent.height
                verticalAlignment: Text.AlignVCenter
            }
            Rectangle {
                x: mapX(timeline.time)
                y: 0
                width: height
                height: parent.height
                color: style.accent
                Label {
                    color: s.foreground
                    text: Math.floor(timeline.time * timeline.fps)
                    x: 27
                    font.pointSize: 10
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                }
            }
            MouseArea {
                id: mimi
                anchors.fill: parent
                onPressed: {
                    con.tempPause()
                    con.setTime(unmapX(mouseX))
                }
                onReleased: {
                    con.tempPlay()
                }
                onPositionChanged: {
                    con.setTime(unmapX(mouseX))
                }
            }
        }
        Rectangle {
            color: style.dark ? "white" : "black"
            opacity: 0.1
            Layout.fillWidth: true
            height: 2
        }
        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.fillHeight: true
            MouseArea {
                id: navigation
            }
            Track {
                id: trackArea
                anchors.fill: parent
            }
            TimelineGrid {
                anchors.fill: parent
                opacity: 1
            }
            Rectangle {
                x: mapX(timeline.time)
                y: -2
                width: 3
                height: parent.height+2
                color: style.accent
            }
            Label {
                text: con.timelinePropertyName
                color: s.dark ? "white" : "black"
                opacity: 0.4
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 10
            }
        }
    }
}