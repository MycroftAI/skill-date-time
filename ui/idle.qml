import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    background: Image {
        source: Qt.resolvedUrl("img/idle-background.png")
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
    }
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        anchors.centerIn: parent
        spacing: 0
        Label {
            id: time
            Layout.alignment: Qt.AlignCenter
            font.capitalization: Font.AllUppercase
            font.family: "Noto Sans Display"
            font.weight: Font.Bold
            font.pixelSize: 140
            color: "white"
            lineHeight: 0.6
            text: sessionData.time_string.replace(":", "꞉")
        }
        Item {
            height: Kirigami.Units.largeSpacing * 5
        }
        Label {
            id: weekday
            Layout.alignment: Qt.AlignCenter
            font.pixelSize: 50
            wrapMode: Text.WordWrap
            font.family: "Noto Sans Display"
            font.bold: true
            lineHeight: 0.6
            text: sessionData.weekday_string
            color: "white"
        }
        Item {
            height: Kirigami.Units.largeSpacing * 3
        }
        Label {
            id: date
            Layout.alignment: Qt.AlignCenter
            font.pixelSize: 50
            wrapMode: Text.WordWrap
            font.family: "Noto Sans Display"
            font.bold: true
            lineHeight: 0.6
            text: sessionData.month_string
            color: "white"
        }
    }
    Label {
        id: buildDate
        visible: sessionData.build_date === "" ? 0 : 1
        enabled: sessionData.build_date === "" ? 0 : 1
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 20
        font.pixelSize: 20
        wrapMode: Text.WordWrap
        font.family: "Noto Sans Display"
        lineHeight: 0.6
        text: sessionData.build_date
        color: "white"
    }

}
