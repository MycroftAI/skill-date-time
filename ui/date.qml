import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    skillBackgroundSource: Qt.resolvedUrl('bg.png')
    Column {
        id: column
        width: parent.width
        height: parent.height
        spacing: Kirigami.Units.largeSpacing
        
        Item {
            height: Kirigami.Units.largeSpacing * 10
        }
        
        Label {
            id: weekday
            //font.family: Noto Sans
            font.bold: true
            width: parent.width
            height: 150
            fontSizeMode: Text.HorizontalFit
            font.pixelSize: 300
            minimumPixelSize: 10
            color: "white"
            font.capitalization: Font.AllUppercase
            text: sessionData.weekday_string
        }
        Label {
            id: month
            width: parent.width
            height: 120
            fontSizeMode: Text.HorizontalFit
            //font.family: Noto Sans
            font.pixelSize: 300
            minimumPixelSize: 10
            font.capitalization: Font.AllUppercase
            text: sessionData.month_string
            color: "lightblue"
        }
        Text {
            id: year
            width: parent.width
            height: parent.height
            fontSizeMode: Text.HorizontalFit
            //font.family: Noto Sans
            font.pixelSize: 300
            minimumPixelSize: 10
            font.capitalization: Font.AllUppercase
            text: sessionData.year_string
            color: "lightgrey"
        }
    }
}
