import { TestBed } from '@angular/core/testing';
import { firstValueFrom } from 'rxjs';
import { CorrelationInfoService } from '../correlation-info.service';
import { MessageMonitorService } from '../message-monitor.service';
import { MessageValidationService } from '../message-validation.service';
import { MessagePersistenceService } from '../message-persistence.service';

const CORRELATION_TOPIC = 'dsp/correlation/info';

describe('CorrelationInfoService', () => {
  let service: CorrelationInfoService;
  let messageMonitor: MessageMonitorService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        CorrelationInfoService,
        MessageMonitorService,
        MessageValidationService,
        MessagePersistenceService,
      ],
    });
    service = TestBed.inject(CorrelationInfoService);
    messageMonitor = TestBed.inject(MessageMonitorService);
  });

  afterEach(() => {
    messageMonitor.clearAll();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return null when no correlation info for orderId', async () => {
    const info = await firstValueFrom(service.getCorrelationInfo$('ORD-001'));
    expect(info).toBeNull();
    expect(service.getCorrelationInfo('ORD-001')).toBeNull();
  });

  it('should store and emit correlation info when dsp/correlation/info arrives', async () => {
    const payload = {
      ccuOrderId: 'ORD-001',
      requestId: 'REQ-123',
      orderType: 'CUSTOMER',
      customerOrderId: 'CO-4711',
      customerId: 'CUST-001',
      orderDate: '2026-02-24T08:00:00.000Z',
      orderAmount: 1,
      plannedDeliveryDate: '2026-03-01T12:00:00.000Z',
    };
    messageMonitor.addMessage(CORRELATION_TOPIC, payload);

    const info = await firstValueFrom(service.getCorrelationInfo$('ORD-001'));
    expect(info).not.toBeNull();
    expect(info?.ccuOrderId).toBe('ORD-001');
    expect(info?.customerOrderId).toBe('CO-4711');
    expect(info?.customerId).toBe('CUST-001');
    expect(service.getCorrelationInfo('ORD-001')).toEqual(info);
  });

  it('should index by requestId when ccuOrderId is missing', async () => {
    const payload = {
      requestId: 'REQ-456',
      orderType: 'CUSTOMER',
      customerOrderId: 'CO-4712',
    };
    messageMonitor.addMessage(CORRELATION_TOPIC, payload);

    const info = await firstValueFrom(service.getCorrelationInfo$('REQ-456'));
    expect(info?.requestId).toBe('REQ-456');
    expect(info?.customerOrderId).toBe('CO-4712');
  });

  it('should process PURCHASE order type', async () => {
    const payload = {
      ccuOrderId: 'ORD-STO-001',
      orderType: 'PURCHASE',
      purchaseOrderId: 'PO-123',
      supplierId: 'SUP-001',
      orderAmount: 2,
    };
    messageMonitor.addMessage(CORRELATION_TOPIC, payload);

    const info = await firstValueFrom(service.getCorrelationInfo$('ORD-STO-001'));
    expect(info?.orderType).toBe('PURCHASE');
    expect(info?.purchaseOrderId).toBe('PO-123');
    expect(info?.supplierId).toBe('SUP-001');
  });

  it('should process history on init', async () => {
    const payload = {
      ccuOrderId: 'ORD-HIST',
      requestId: 'REQ-HIST',
      orderType: 'CUSTOMER',
      customerOrderId: 'CO-HIST',
    };
    messageMonitor.addMessage(CORRELATION_TOPIC, payload);

    const newService = new CorrelationInfoService(messageMonitor);
    const info = await firstValueFrom(newService.getCorrelationInfo$('ORD-HIST'));
    expect(info?.ccuOrderId).toBe('ORD-HIST');
    newService.ngOnDestroy();
  });
});
