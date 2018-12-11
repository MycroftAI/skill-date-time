import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    skillBackgroundSource: sessionData.background
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        width: parent.width
        spacing: Kirigami.Units.largeSpacing
        
        Item {
            height: Kirigami.Units.largeSpacing * 10
        }
        
        Label {
            id: weekday
            Layout.alignment: Qt.AlignHCenter
            Layout.columnSpan: 2
            font.capitalization: Font.AllUppercase
            font.bold: true
            font.pixelSize: 120
            color: "white"
            text: sessionData.weekday_string
        }
        Label {
            id: month
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: 80
            Layout.columnSpan: 2
            wrapMode: Text.WordWrap
            font.capitalization: Font.AllUppercase
            text: sessionData.month_string
            color: "lightblue"
        }
        Label {
            id: year
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: 180
            Layout.columnSpan: 2
            wrapMode: Text.WordWrap
            font.capitalization: Font.AllUppercase
            text: sessionData.year_string
            color: "lightgrey"
        }
    }
}
