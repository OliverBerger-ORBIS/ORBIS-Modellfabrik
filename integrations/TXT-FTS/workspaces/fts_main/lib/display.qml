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
  StatusIndicator {
    id: txt_status_indicator22
    color: "#FFFFFF"
    active: false
    x: 96
    y: 130
    width: 50
    height: 44
  }
  StatusIndicator {
    id: txt_status_indicator2
    color: "#FFFFFF"
    active: false
    x: 49
    y: 130
    width: 50
    height: 44
  }
  StatusIndicator {
    id: txt_status_indicator
    color: "#FFFFFF"
    active: false
    x: 2
    y: 130
    width: 50
    height: 44
  }
  TXTLabel {
    id: txt_label2
    text: "DRIVING:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 51
    width: 108
    height: 21
  }
  TXTButton {
    id: btn_reset
    text: "<h2>Reset</h2>"
    font.pixelSize: 25
    font.bold: false
    font.italic: false
    font.underline: false
    enabled: true
    x: 150
    y: 176
    width: 75
    height: 44
  }
  TXTLabel {
    id: label_status
    text: " "
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 177
    width: 136
    height: 20
  }
  TXTLabel {
    id: label_mqtt_info
    text: " "
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 199
    width: 136
    height: 21
  }
  Gauge {
    id: txt_gauge
    minimumValue: 0
    value: 0
    maximumValue: 100
    orientation: Qt.Vertical
    tickmarkStepSize: 25
    minorTickmarkCount: 0
    formatValue: function(value) {
      return value.toFixed(1);
    }
    x: 140
    y: 51
    width: 95
    height: 100
  }
  TXTLabel {
    id: txt_Volt_label
    text: ""
    font.pixelSize: 16
    font.bold: true
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignHCenter
    color: "#FF0000"
    elide: Text.ElideRight
    x: 150
    y: 154
    width: 27
    height: 17
  }
  TXTLabel {
    id: txt_Volt_Header
    text: "V ◼▊▊▊"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignRight
    color: "#ffffff"
    elide: Text.ElideRight
    x: 180
    y: 154
    width: 45
    height: 17
  }
  TXTLabel {
    id: txt_version
    text: "<h3>APS FTS</h3>"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 2
    width: 225
    height: 22
  }
  TXTLabel {
    id: txt_label
    text: "CONNECTED:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 27
    width: 108
    height: 21
  }
  StatusIndicator {
    id: txt_status_driving
    color: "#61996A"
    active: false
    x: 98
    y: 51
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_connected
    color: "#61996A"
    active: false
    x: 98
    y: 26
    width: 20
    height: 21
  }
  TXTLabel {
    id: txt_label22
    text: "ERROR:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 75
    width: 108
    height: 21
  }
  StatusIndicator {
    id: txt_status_error
    color: "#EE8253"
    active: false
    x: 98
    y: 75
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load1_r
    color: "#EE8253"
    active: true
    x: 17
    y: 133
    width: 20
    height: 20
  }
  TXTLabel {
    id: txt_label222
    text: "LOAD:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 10
    y: 104
    width: 123
    height: 21
  }
  StatusIndicator {
    id: txt_status_load1_w
    color: "#E7E2E2"
    active: true
    x: 8
    y: 149
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load1_b
    color: "#6640FF"
    active: true
    x: 26
    y: 149
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load2_r
    color: "#EE8253"
    active: true
    x: 64
    y: 133
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load2_w
    color: "#E7E2E2"
    active: true
    x: 55
    y: 149
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load2_b
    color: "#6640FF"
    active: true
    x: 73
    y: 149
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load3_r
    color: "#EE8253"
    active: true
    x: 111
    y: 133
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load3_w
    color: "#E7E2E2"
    active: true
    x: 102
    y: 149
    width: 20
    height: 20
  }
  StatusIndicator {
    id: txt_status_load3_b
    color: "#6640FF"
    active: true
    x: 120
    y: 149
    width: 20
    height: 20
  }
  TXTLabel {
    id: txt_label_charging
    text: "CHARGING:"
    font.pixelSize: 16
    font.bold: false
    font.italic: false
    font.underline: false
    horizontalAlignment: Text.AlignLeft
    color: "#ffffff"
    elide: Text.ElideRight
    x: 140
    y: 27
    width: 86
    height: 21
  }
  StatusIndicator {
    id: txt_status_loading
    color: "#61996A"
    active: false
    x: 203
    y: 26
    width: 20
    height: 20
  }
}
