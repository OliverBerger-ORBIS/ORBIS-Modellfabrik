import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { firstValueFrom } from 'rxjs';
import { VERSION } from '../../../environments/version';
import { getAssetPath } from '../../assets/detail-asset-map';
import { ShopfloorLayoutService } from '../shopfloor-layout.service';
import { ShopfloorMappingService } from '../shopfloor-mapping.service';
import type { ShopfloorLayoutConfig } from '../../components/shopfloor-preview/shopfloor-layout.types';

describe('ShopfloorLayoutService', () => {
  let httpMock: HttpTestingController;
  let mapping: { initializeLayout: jest.Mock };

  const layoutUrl = `${getAssetPath('shopfloor/shopfloor_layout.json')}?v=${encodeURIComponent(VERSION.full)}`;
  const config = {
    cells: [],
    parsed_roads: [],
    modules_by_serial: {},
    intersection_map: {},
  } as unknown as ShopfloorLayoutConfig;

  beforeEach(() => {
    mapping = { initializeLayout: jest.fn() };
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        ShopfloorLayoutService,
        { provide: ShopfloorMappingService, useValue: mapping },
      ],
    });
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('loads layout, initializes mapping, and exposes config$', async () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => undefined);
    const service = TestBed.inject(ShopfloorLayoutService);
    const req = httpMock.expectOne(layoutUrl);
    req.flush(config);

    const snapshot = await firstValueFrom(service.snapshot$);
    const exposed = await firstValueFrom(service.config$);

    expect(snapshot.url).toBe(layoutUrl);
    expect(snapshot.config).toEqual(config);
    expect(exposed).toEqual(config);
    expect(mapping.initializeLayout).toHaveBeenCalledWith(config);
    warn.mockRestore();
  });

  it('returns a null snapshot when the layout request fails', async () => {
    const warn = jest.spyOn(console, 'warn').mockImplementation(() => undefined);
    const service = TestBed.inject(ShopfloorLayoutService);
    const req = httpMock.expectOne(layoutUrl);
    req.flush('missing', { status: 404, statusText: 'Not Found' });

    const snapshot = await firstValueFrom(service.snapshot$);
    expect(snapshot.config).toBeNull();
    expect(snapshot.hash).toBeNull();
    expect(snapshot.url).toBe(layoutUrl);
    expect(mapping.initializeLayout).not.toHaveBeenCalled();
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });
});
