import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: timeRoot
    
    ColumnLayout {
        id: grid
        anchors.fill: parent
        spacing: Kirigami.Units.largeSpacing

        Item {
            Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Kirigami.Units.smallSpacing
            
            Label {
                id: hour
                width: parent.width
                height: parent.height
                font.capitalization: Font.AllUppercase
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Bold
                font.pixelSize: height
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: sessionData.time_string.split(":")[0]
                color: "white"
                renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)
            }
        }
        
        Item {
            Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Kirigami.Units.smallSpacing
            
            Label {
                id: minute
                width: parent.width
                height: parent.height
                font.capitalization: Font.AllUppercase
                font.family: "Noto Sans"
                font.bold: false
                font.weight: Font.Normal
                font.pixelSize: height
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: sessionData.time_string.split(":")[1]
                color: "#22A7F0"
                renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)
            }
        }
    }
}
