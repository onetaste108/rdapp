import QtQml 2.15
import QtQuick 2.15

Item {
    Loader {
        id: mainWindowLoader
        active: false
        // active: true
        source: "MainWindow.qml"
        objectName: "mainWindowLoader"

        // asynchronous: true
        onLoaded: {
            item.visible = true;
            splashScreenLoader.item.visible = false;
            splashScreenLoader.source = "";
        }
    }

    Loader {
        id: splashScreenLoader
        source: "Loader.qml"
        onLoaded: {
            mainWindowLoader.active = true;
        }
    }
}