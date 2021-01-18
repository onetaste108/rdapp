import QtQuick 2.15
import QtQuick.Controls 2.15

/*
* The MouseArea + interactive: false + maximumFlickVelocity are required
* to fix scrolling for desktop systems where we don't want flicking behaviour.
*
* See also:
* ScrollView.qml in qtquickcontrols
* qquickwheelarea.cpp in qtquickcontrols
*/
MouseArea {
    id: root
    propagateComposedEvents: true
    acceptedButtons: Qt.NoButton

    property Flickable flickable

    //Place the mouse area under the flickable
    z: -1
    onFlickableChanged: {
        flickable.interactive = false
        flickable.maximumFlickVelocity = 100000
        flickable.boundsBehavior = Flickable.StopAtBounds
        root.parent = flickable
    }

    function scrollByPixelDeltaY(flickableItem, pixelDelta) {
        if (!pixelDelta) {
            return flickableItem.contentY;
        }

        var minYExtent = flickableItem.originY + flickableItem.topMargin;
        var maxYExtent = (flickableItem.contentHeight + flickableItem.bottomMargin + flickableItem.originY) - flickableItem.height;

        if (typeof(flickableItem.headerItem) !== "undefined" && flickableItem.headerItem) {
            minYExtent += flickableItem.headerItem.height
        }

        //Avoid overscrolling
        return Math.max(minYExtent, Math.min(maxYExtent, flickableItem.contentY - pixelDelta));
    }

    function scrollByPixelDeltaX(flickableItem, pixelDelta) {
        if (!pixelDelta) {
            return flickableItem.contentX;
        }

        var minXExtent = flickableItem.originX + flickableItem.leftMargin;
        var maxXExtent = (flickableItem.contentWidth + flickableItem.rightMargin + flickableItem.originX) - flickableItem.width;

        if (typeof(flickableItem.headerItem) !== "undefined" && flickableItem.headerItem) {
            minXExtent += flickableItem.headerItem.width
            console.log("DDD")
        }

        //Avoid overscrolling
        return Math.max(minXExtent, Math.min(maxXExtent, flickableItem.contentX - pixelDelta));
    }

    function calculateNewPositionY(flickableItem, wheel) {
        //Nothing to scroll
        if (flickableItem.contentHeight < flickableItem.height) {
            return flickableItem.contentY;
        }
        //Ignore 0 events (happens at least with Christians trackpad)
        if (wheel.pixelDelta.y == 0 && wheel.angleDelta.y == 0) {
            return flickableItem.contentY;
        }
        //pixelDelta seems to be the same as angleDelta/8
        var pixelDelta = 0
        //The pixelDelta is a smaller number if both are provided, so pixelDelta can be 0 while angleDelta is still something. So we check the angleDelta
        if (wheel.angleDelta.y) {
            var wheelScrollLines = 3 //Default value of QApplication wheelScrollLines property
            var pixelPerLine = 20 //Default value in Qt, originally comes from QTextEdit
            var ticks = (wheel.angleDelta.y / 8) / 15.0 //Divide by 8 gives us pixels typically come in 15pixel steps.
            pixelDelta =  ticks * pixelPerLine * wheelScrollLines
        } else {
            pixelDelta = wheel.pixelDelta.y
        }

        return scrollByPixelDeltaY(flickableItem, pixelDelta);
    }

    function calculateNewPositionX(flickableItem, wheel) {
        //Nothing to scroll
        if (flickableItem.contentWidth < flickableItem.width) {
            return flickableItem.contentX;
        }
        //Ignore 0 events (happens at least with Christians trackpad)
        if (wheel.pixelDelta.x == 0 && wheel.angleDelta.x == 0) {
            return flickableItem.contentX;
        }
        //pixelDelta seems to be the same as angleDelta/8
        var pixelDelta = 0
        //The pixelDelta is a smaller number if both are provided, so pixelDelta can be 0 while angleDelta is still something. So we check the angleDelta
        if (wheel.angleDelta.x) {
            var wheelScrollLines = 3 //Default value of QApplication wheelScrollLines property
            var pixelPerLine = 20 //Default value in Qt, originally comes from QTextEdit
            var ticks = (wheel.angleDelta.x / 8) / 15.0 //Divide by 8 gives us pixels typically come in 15pixel steps.
            pixelDelta =  ticks * pixelPerLine * wheelScrollLines
        } else {
            pixelDelta = wheel.pixelDelta.x
        }

        return scrollByPixelDeltaX(flickableItem, pixelDelta);
    }

    function scrollDownY() {
        flickable.flick(0, 0);
        flickable.contentY = scrollByPixelDeltaY(flickable, -60); //3 lines * 20 pixels
    }

    function scrollUpY() {
        flickable.flick(0, 0);
        flickable.contentY = scrollByPixelDeltaY(flickable, 60); //3 lines * 20 pixels
    }

    function scrollDownX() {
        flickable.flick(0, 0);
        flickable.contentX = scrollByPixelDeltaX(flickable, -60); //3 lines * 20 pixels
    }

    function scrollUpX() {
        flickable.flick(0, 0);
        flickable.contentX = scrollByPixelDeltaX(flickable, 60); //3 lines * 20 pixels
    }

    onWheel: {
        var newPosY = calculateNewPositionY(flickable, wheel);
        var newPosX = calculateNewPositionX(flickable, wheel);
        // console.warn("Delta: ", wheel.pixelDelta.y);
        // console.warn("Old position: ", flickable.contentY);
        // console.warn("New position: ", newPos);

        // Show the scrollbars
        flickable.flick(0, 0);
        flickable.contentY = newPosY;
        flickable.contentX = newPosX;
        cancelFlickStateTimer.start()
    }


    Timer {
        id: cancelFlickStateTimer
        //How long the scrollbar will remain visible
        interval: 500
        // Hide the scrollbars
        onTriggered: flickable.cancelFlick();
    }
}