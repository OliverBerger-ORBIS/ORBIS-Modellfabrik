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
    id: txt_label2
    text: "FAILED:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 190
    width: 72
    height: 18
  }
  TXTLabel {
    id: txt_label
    text: "PASSED:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 70
    y: 190
    width: 72
    height: 18
  }
  TXTLabel {
    id: img_label
    text: ""
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 28
    y: 41
    width: 185
    height: 139
  }
  StatusIndicator {
    id: green
    color: "#39E755"
    active: false
    x: 116
    y: 190
    width: 20
    height: 20
  }
  StatusIndicator {
    id: red
    color: "#E71313"
    active: false
    x: 45
    y: 191
    width: 20
    height: 20
  }
  TXTLabel {
    id: version_label
    text: "<small>APS AI</small>"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 1
    width: 230
    height: 15
  }
  TXTLabel {
    id: part_pass_fail
    text: ""
    font.pixelSize: 14
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 157
    y: 17
    width: 73
    height: 20
  }
  TXTButton {
    id: txt_button
    text: "<h2>ANALYZE</h2>"
    font.pixelSize: 20
    font.bold: false
    font.italic: false
    font.underline: false
    enabled: true
    x: 144
    y: 192
    width: 90
    height: 35
  }
  TXTLabel {
    id: label_mqtt_status
    text: "connecting to mqtt broker ..."
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 5
    y: 210
    width: 137
    height: 16
  }
  TXTLabel {
    id: txt_label22
    text: "CONNECTED:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 4
    y: 19
    width: 72
    height: 18
  }
  StatusIndicator {
    id: mqtt_green
    color: "#39E755"
    active: false
    x: 75
    y: 19
    width: 20
    height: 20
  }
}
