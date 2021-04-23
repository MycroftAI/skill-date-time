import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    skillBackgroundColorOverlay: Qt.rgba(0, 0, 0, 1)
    
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        anchors.centerIn: parent

        /* Put the day of the week at the top of the screen */
        Label {
            id: weekday
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: 65
            wrapMode: Text.WordWrap
            renderType: Text.NativeRendering
            font.family: "Noto Sans Display"
            font.styleName: "Black"
            font.capitalization: Font.AllUppercase
            text: sessionData.weekday_string
            color: "white"
        }

        /* Add some spacing between the day of week and the calendar graphic */
        Item {
            height: Kirigami.Units.largeSpacing
        }

        /* Calendar graphic */
        Image {
            id: image
            source: Qt.resolvedUrl("img/date-bg.svg")

            /*  The top part of the calendar graphic containing the month */
            Image {
                id: calendartop
                x: 0
                width: parent.width
                fillMode: Image.PreserveAspectFit
                anchors.top: parent.bottom
                anchors.topMargin: -(parent.height + 1)
                source: Qt.resolvedUrl("img/date-top.svg")
                Label {
                    id: month
                    anchors.centerIn: parent
                    font.pixelSize: 60
                    wrapMode: Text.WordWrap
                    font.family: "Noto Sans Display"
                    font.bold: true
                    text: sessionData.month_string.split(" ")[0]
                    color: "white"
                }
            }

            /* The day of the month goes in the calendar graphic under the month */
            Label {
                id: date
                anchors.centerIn: parent
                anchors.verticalCenterOffset: calendartop.height / 2
                font.pixelSize: 230
                wrapMode: Text.WordWrap
                font.family: "Noto Sans Display"
                font.bold: true
                text: sessionData.month_string.split(" ")[1]
                color: "#2C3E50"
            }
        }
    }
}
