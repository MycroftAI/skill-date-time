import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        Layout.fillHeight: true
        anchors.centerIn: parent
        spacing: 0
        Label {
            id: location
            Layout.alignment: Qt.AlignCenter
            font.capitalization: Font.AllUppercase
            font.family: "Noto Sans"
            font.bold: true
            font.weight: Font.Bold
            font.pixelSize: 50
            color: "white"
            lineHeight: 0.6
            text: sessionData.location
        }
        Item {
            height: Kirigami.Units.smallSpacing
        }
        RowLayout {
            id: clock
            Layout.fillWidth: true
            Layout.fillHeight: true
//            anchors.centerIn: parent
            spacing: 0
            Label {
            id: hour
            Layout.alignment: Qt.AlignRight
            font.capitalization: Font.AllUppercase
            font.family: "Noto Sans"
            font.bold: true
            font.weight: Font.Bold
            font.pixelSize: 200
            color: "white"
            lineHeight: 0.6
            text: sessionData.hours
            }
            Item {
                height: Kirigami.Units.largeSpacing * 5
            }
            Label {
                id: minute
                Layout.alignment: Qt.AlignRight
                font.pixelSize: 200
                wrapMode: Text.WordWrap
                font.family: "Noto Sans"
                font.bold: false
                font.weight: Font.Normal
                lineHeight: 0.6
                font.capitalization: Font.AllUppercase
                text: sessionData.minutes
                color: "#22A7F0"
            }
            Item {
                height: Kirigami.Units.largeSpacing * 5
            }
        }
        Item {
            height: Kirigami.Units.largeSpacing * 15
        }
        Label {
            id: ampm
            Layout.alignment: Qt.AlignRight
            font.capitalization: Font.AllUppercase
            font.family: "Noto Sans"
            font.bold: true
            font.weight: Font.Bold
            font.pixelSize: 50
            color: "white"
            lineHeight: 0.6
            text: sessionData.ampm
        }
    }
}