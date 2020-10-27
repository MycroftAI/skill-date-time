import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtQuick.Window 2.3
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: timeRoot
    
    property bool horizontalMode: timeRoot.width > timeRoot.height ? 1 : 0
    
    GridLayout {
        id: grid
        anchors.fill: parent
        anchors.margins: parent.height * 0.10
        columns: horizontalMode ? 3 : 1

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
                font.pixelSize: horizontalMode ? parent.width : parent.height
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: sessionData.time_string.split(":")[0]
                color: "white"
                renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)
            }
        }
        
        Item {
            Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
            Layout.preferredWidth: parent.width / 6
            Layout.fillHeight: true
            Layout.margins: Kirigami.Units.smallSpacing
            visible: horizontalMode ? 1 : 0
            enabled: horizontalMode ? 1 : 0
            
            Label {
                id: dots
                width: parent.width
                height: parent.height
                font.capitalization: Font.AllUppercase
                font.family: "Noto Sans"
                font.bold: true
                font.weight: Font.Normal
                font.pixelSize: width
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: ":"
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
                font.pixelSize: horizontalMode ? parent.width : parent.height
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                text: sessionData.time_string.split(":")[1]
                color: "#22A7F0"
                renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)
            }
        }
    }
}
