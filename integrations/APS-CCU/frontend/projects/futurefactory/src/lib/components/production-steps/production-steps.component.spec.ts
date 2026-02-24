import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { ProductionStepsComponent } from './production-steps.component';

describe('ProductionStepsComponent', () => {
  let fixture: ComponentFixture<ProductionStepsComponent>;
  let component: ProductionStepsComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [ProductionStepsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductionStepsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });
});
