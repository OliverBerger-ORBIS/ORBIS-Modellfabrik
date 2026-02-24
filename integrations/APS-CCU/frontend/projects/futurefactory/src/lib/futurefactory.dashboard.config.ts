import { DashboardConfig, WindowType } from '@fischertechnik/ft-window';

export const FUTURE_FACTORY_DASHBOARD: DashboardConfig = {
  history: true,
  identifier: 'ff',
  dialog: {
    treeNodes: [
      {
        title: 'Customer view',
        i18n: 'dashboardCustomerView',
        type: WindowType.TypeEnum.Customer,
      },
      {
        title: 'Supplier view',
        i18n: 'dashboardSupplierView',
        type: WindowType.TypeEnum.OrderRawMaterial,
      },
      {
        title: 'Production view',
        i18n: 'dashboardProductionvView',
        children: [
          {
            title: 'Stock',
            i18n: 'dashboardStock',
            type: WindowType.TypeEnum.Stock,
          },
          {
            title: 'NFC Reader',
            i18n: 'dashboardNfcReader',
            type: WindowType.TypeEnum.Nfc,
          },
        ],
      },
      {
        title: 'Monitoring',
        i18n: 'dashboardMonitoring',
        children: [
          {
            title: 'Temperature',
            i18n: 'dashboardChartTemperature',
            type: WindowType.TypeEnum.TemperatureValue,
          },
          {
            title: 'Air humidity',
            i18n: 'dashboardChartAirHumidity',
            type: WindowType.TypeEnum.AirHumidityValue,
          },
          {
            title: 'Air pressure',
            i18n: 'dashboardChartAirPressure',
            type: WindowType.TypeEnum.AirPressureValue,
          },
          {
            title: 'Air quality',
            i18n: 'dashboardChartAirQuality',
            type: WindowType.TypeEnum.AirQualityValue,
          },
          {
            title: 'Brightnes',
            i18n: 'dashboardChartBrightness',
            type: WindowType.TypeEnum.BrightnesValue,
          },
          {
            title: 'Camera',
            i18n: 'dashboardCamera',
            type: WindowType.TypeEnum.Camera,
          },
          {
            title: 'Camera control',
            i18n: 'dashboardCameraControl',
            type: WindowType.TypeEnum.Ptu,
          },
        ],
      },
    ],
  },
};

export const FUTURE_FACTORY_DASHBOARD_NO_HISTORY_CONFIG: DashboardConfig = {
  ...FUTURE_FACTORY_DASHBOARD,
  history: false,
};
