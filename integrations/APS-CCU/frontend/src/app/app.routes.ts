/**
 * This enum is used to define the routes of the application.
 * It is used in the app.routing.ts and app.component.ts.
 */
export enum RoutePaths {
  // The root path of this application.
  LOGS='factory/logs',
  LAYOUT='factory/layout',
  FLOWS='factory/flows',
  ORDERS='factory/orders',
  ROOT = '',
  // The path to the (beemo) dashboard view
  DASHBOARD = 'dashboard',
  // The path to the factory view
  FACTORY = 'factory',
  // The path, that matches every other path.
  WILDCARD = '**',
}
