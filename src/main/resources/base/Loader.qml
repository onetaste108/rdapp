import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    id: splashScreen
    modality: Qt.ApplicationModal
    flags: Qt.SplashScreen
	width: 512
	height: 512
    color: "transparent"

	Image {
        source: "icons/splash.png"
    }

    Component.onCompleted: visible = true
}