# FfFrontend

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 13.3.10.

## Localization

We added additional commands to the `package.json` to help with extracting and updating the localization files.

### Extracting localization strings for beemo components

To extract the localization strings for the beemo components, run the following command:

```bash
npm run i18n:extract
```

This will extract the localization strings from the used beemo components and place them in the `src/assets/i18n/messages.xlf` file.

*NOTE*: Usually this is not required, because beemo provides the localization files within their project. If an update is required, check the [beemo repo](https://review.beemo.eu/plugins/gitiles/ft/angular/lib/+/refs/heads/master/src/locale/) for the latest localization files. Use the available credentials in [Bitwarden](https://warden.shrd2.omm.cloud/#/vault?itemId=a927cb0a-de32-4a48-b34e-85bfa09ac7a1) to access the repo.

### Extracting localization string for the OMM components

To extract the localization strings for the OMM components, run the following command:

```bash
npm run i18n:extract:futurefactory
```

This will extract the localization strings from the used OMM components and place them in the `projects/futurefactory/assets/i18n/messages.{de,en,es.fr,nl,pt,ru}.xlf` files.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
