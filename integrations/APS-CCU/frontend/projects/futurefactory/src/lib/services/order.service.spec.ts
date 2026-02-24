import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { TypedMqttService } from '../futurefactory.service';
import { OrderService, orderRequest } from './order.service';

describe('OrderService', () => {
  const subscribeMock = jest.fn(() => EMPTY);
  const publishMock = jest.fn();
  let service: OrderService;

  beforeEach(() => {
    jest.useFakeTimers();
    TestBed.configureTestingModule({
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: subscribeMock,
          publish: publishMock,
        }),
      ],
    });
    service = TestBed.inject(OrderService);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it("should call publish in the injected mqtt service", () => {
    service.sendProductionOrder("BLUE");
    expect(publishMock).toHaveBeenCalledWith(orderRequest, {
      "orderType": "PRODUCTION",
      "timestamp": new Date(),
      "type":  "BLUE",
    });
  });
});
