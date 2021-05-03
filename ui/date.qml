import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0

Mycroft.CardDelegate {
    id: dateRoot
    topInset: Mycroft.Units.gridUnit / 2
    bottomInset: Mycroft.Units.gridUnit / 2

    ColumnLayout {
        id: grid
        anchors.fill: parent
        spacing: 0

        /* Put the day of the week at the top of the screen */
        Item { 
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.fillWidth: true
            Layout.preferredHeight: parent.height / 6
            
            Label {
                id: weekday
                anchors.centerIn: parent
                font.pixelSize: parent.height
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                font.family: "Noto Sans Display"
                font.styleName: "Black"
                font.capitalization: Font.AllUppercase
                text: sessionData.weekday_string
                color: "white"
            }
        }

        /* Add some spacing between the day of week and the calendar graphic */
        Item {
            Layout.preferredHeight: Mycroft.Units.gridUnit / 2
        }
        
        /* Calendar graphic */
        Item {
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.preferredWidth: Mycroft.Units.gridUnit * 25.5
            Layout.preferredHeight: Mycroft.Units.gridUnit * 19.25
            
            /* Use Rectangles Instead of Graphics For Proper Scaling of Graphics Items*/
            Rectangle {
                id: outterRectangle
                anchors.fill: parent
                radius: 30
                Item {
                    id: date
                    anchors.fill: parent
                    anchors.topMargin: Mycroft.Units.gridUnit * 5.5
                    
                    /* The day of the month goes in the calendar graphic under the month */
                    Label {
                        anchors.centerIn: parent
                        font.pixelSize: parent.height
                        wrapMode: Text.WordWrap
                        font.family: "Noto Sans Display"
                        font.styleName: "Bold"
                        text: sessionData.day_string
                        color: "#2C3E50"
                    }
                }
            }
            
            
            Item {
                anchors.fill: outterRectangle
                layer.enabled: true
                layer.effect: OpacityMask {
                    maskSource: outterRectangle
                }            
                Rectangle {
                    id: innerRectangle
                    width: Mycroft.Units.gridUnit * 25.5
                    height: Mycroft.Units.gridUnit * 5.5
                    clip: true
                    color: "#22A7F0"
                    
                    /*  The top part of the calendar graphic containing the month */
                    Label {
                        id: month
                        anchors.centerIn: parent
                        font.pixelSize: parent.height * 0.65
                        wrapMode: Text.WordWrap
                        font.family: "Noto Sans Display"
                        font.styleName: "Bold"
                        text: sessionData.month_string
                        color: "white"
                    }
                }
            }
        }
    }
}
