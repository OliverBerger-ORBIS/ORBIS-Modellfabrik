import { Component } from '@angular/core';

@Component({
  selector: 'ff-layout-editor',
  templateUrl: './layout-editor.component.html',
  styleUrls: ['./layout-editor.component.scss'],
})
export class FutureFactoryLayoutEditorComponent {
  // Strings in html file, should later be translated
  readonly htmlStrings = {
    configurationHeader: 'Fabrikkonfiguration',
  };

}
