import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { ProductionTimeCalculatorComponent } from './production-time-calculator.component';

describe('ProductionTimeCalculatorComponent', () => {
  let fixture: ComponentFixture<ProductionTimeCalculatorComponent>;
  let component: ProductionTimeCalculatorComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [ProductionTimeCalculatorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductionTimeCalculatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });
});
