import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';

import { FactoryConfigComponent } from './factory-config.component';
import { TypedMqttService } from '../../futurefactory.service';
import { EMPTY } from 'rxjs';

describe('FactoryConfigComponent', () => {
  let component: FactoryConfigComponent;
  let fixture: ComponentFixture<FactoryConfigComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [FactoryConfigComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
      ],
    });
    fixture = TestBed.createComponent(FactoryConfigComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
