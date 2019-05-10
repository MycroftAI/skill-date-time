import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        anchors.centerIn: parent
        spacing: 0
        Label {
            id: hour
            Layout.alignment: Qt.AlignRight
            font.capitalization: Font.AllUppercase
            font.family: "Noto Sans"
            font.bold: true
            font.weight: Font.Bold
            font.pixelSize: 300
            color: "white"
            lineHeight: 0.6
            text: sessionData.time_string.split(":")[0]
        }
        Item {
            height: Kirigami.Units.largeSpacing * 5
        }
        Label {
            id: minute
            Layout.alignment: Qt.AlignRight
            font.pixelSize: 300
            wrapMode: Text.WordWrap
            font.family: "Noto Sans"
            font.bold: false
            font.weight: Font.Normal
            lineHeight: 0.6
            font.capitalization: Font.AllUppercase
            text: sessionData.time_string.split(":")[1]
            color: "#22A7F0"
        }
    }
}
