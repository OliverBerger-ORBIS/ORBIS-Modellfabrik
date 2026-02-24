import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'ff-debug-output',
  templateUrl: './debug-output.component.html',
  styleUrls: ['./debug-output.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DebugOutputComponent {
  @Input() data: any;
}
