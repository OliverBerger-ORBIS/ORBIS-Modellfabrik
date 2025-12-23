// auto generated content from display configuration
import QtQuick 2.2
import QtQuick.Window 2.0
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Extras 1.4

TXTWindow {
  Rectangle {
    id: rect
    color: "grey"
    anchors.fill: parent
  }
  TXTLabel {
    id: txt_label_message
    text: ""
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 185
    width: 230
    height: 20
  }
  TXTButton {
    id: txt_button_nfc_read
    text: "<b>NFC read</b>"
    font.pixelSize: 22
    font.bold: false
    font.italic: false
    font.underline: false
    enabled: true
    x: 140
    y: 130
    width: 95
    height: 50
  }
  TXTButton {
    id: txt_button_nfc_delete
    text: "<b>NFC delete</b>"
    font.pixelSize: 22
    font.bold: false
    font.italic: false
    font.underline: false
    enabled: true
    x: 5
    y: 130
    width: 95
    height: 50
  }
  TXTLabel {
    id: txt_label_version
    text: "<h3>APS DPS</h3>"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 0
    width: 230
    height: 20
  }
  TXTLabel {
    id: txt_label_message2
    text: ""
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 205
    width: 230
    height: 20
  }
  TXTLabel {
    id: txt_label_connected
    text: "CONNECTED:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 30
    width: 75
    height: 20
  }
  StatusIndicator {
    id: txt_status_connected
    color: "#61996A"
    active: false
    x: 75
    y: 26
    width: 30
    height: 30
  }
  TXTButton {
    id: txt_button_park
    text: "<b>PARK</b>"
    font.pixelSize: 22
    font.bold: false
    font.italic: false
    font.underline: false
    enabled: true
    x: 140
    y: 70
    width: 95
    height: 50
  }
}
