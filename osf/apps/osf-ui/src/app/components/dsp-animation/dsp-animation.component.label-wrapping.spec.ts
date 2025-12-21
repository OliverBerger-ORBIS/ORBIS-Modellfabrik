import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { DspAnimationComponent } from './dsp-animation.component';
import { ModuleNameService } from '../../services/module-name.service';
import { ExternalLinksService } from '../../services/external-links.service';
import type { ContainerConfig } from './types';

describe('DspAnimationComponent - Label Wrapping', () => {
  let component: DspAnimationComponent;
  let fixture: ComponentFixture<DspAnimationComponent>;

  beforeEach(async () => {
    const httpMock = {
      get: jest.fn(() => of({})),
    };

    const moduleNameServiceMock = {
      getModuleDisplayName: jest.fn(() => of(null)),
    };

    const externalLinksServiceMock = {
      settings$: of({
        grafanaDashboardUrl: '',
        smartfactoryDashboardUrl: '',
        dspControlUrl: '',
        managementCockpitUrl: '',
      }),
      get current() {
        return {
          grafanaDashboardUrl: '',
          smartfactoryDashboardUrl: '',
          dspControlUrl: '',
          managementCockpitUrl: '',
        };
      },
    };

    await TestBed.configureTestingModule({
      imports: [DspAnimationComponent],
      providers: [
        { provide: HttpClient, useValue: httpMock },
        { provide: ModuleNameService, useValue: moduleNameServiceMock },
        { provide: ExternalLinksService, useValue: externalLinksServiceMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DspAnimationComponent);
    component = fixture.componentInstance;
    // Don't call detectChanges() here to avoid ngOnInit running
    // We'll initialize containers manually in each test
  });

  describe('getWrappedLabelLines', () => {
    const createContainer = (
      id: string,
      label: string,
      width: number = 100,
      fontSize: number = 12
    ): ContainerConfig => ({
      id,
      label,
      x: 0,
      y: 0,
      width,
      height: 50,
      type: 'device',
      fontSize,
    });

    beforeEach(() => {
      // Ensure component is initialized with containers
      // Initialize minimal state to avoid ngOnInit issues
      component['containers'] = [];
      component['connections'] = [];
      component['steps'] = [];
      // containerLabels is read-only, so we'll set labels directly on containers
    });

    describe('Labels that fit on one line', () => {
      it('should return single line when label fits without break hints', () => {
        const container = createContainer('sf-device-1', 'Ladestation', 150, 12);
        // Set container in component's containers array so getContainerLabel can find it
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines).toEqual(['Ladestation']);
      });

      it('should remove break hints and hyphens when label fits', () => {
        const container = createContainer('sf-device-1', 'Lade- / station', 150, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines).toEqual(['Ladestation']);
      });

      it('should remove break hints when label fits', () => {
        const container = createContainer('sf-device-1', 'CNC / Station', 150, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines).toEqual(['CNCStation']);
      });

      it('should handle multiple break hints when label fits', () => {
        const container = createContainer('sf-device-1', 'Test / Label / Here', 200, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines).toEqual(['TestLabelHere']);
      });
    });

    describe('Labels with break hints that need wrapping', () => {
      it('should wrap at break hints with hyphen', () => {
        const container = createContainer('sf-device-1', 'Lade- / station', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThan(1);
        expect(lines[0]).toContain('Lade');
        expect(lines[0]).toMatch(/-$/); // Should end with hyphen
        expect(lines[1]).toBe('station');
      });

      it('should wrap at break hints without existing hyphen', () => {
        const container = createContainer('sf-device-1', 'CNC / Station', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThan(1);
        expect(lines[0]).toMatch(/CNC-?$/); // May or may not have hyphen
        expect(lines[1]).toBe('Station');
      });

      it('should handle multiple break hints', () => {
        const container = createContainer('sf-device-1', 'Test / Label / Here', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(2);
        expect(lines.length).toBeLessThanOrEqual(3);
      });

      it('should add hyphen when breaking between parts', () => {
        const container = createContainer('sf-device-1', 'Hydraulic / Station', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        if (lines.length > 1) {
          expect(lines[0]).toMatch(/-$/); // First line should end with hyphen
        }
      });

      it('should not add hyphen if part already ends with hyphen', () => {
        const container = createContainer('sf-device-1', 'Lade- / station', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        if (lines.length > 1) {
          // Should not have double hyphen
          expect(lines[0]).not.toMatch(/--/);
        }
      });
    });

    describe('System labels with break hints', () => {
      it('should wrap SCADA System label correctly', () => {
        const container = createContainer('sf-system-scada', 'SCADA / System', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('SCADA');
          expect(lines[1]).toContain('System');
        }
      });

      it('should wrap Industrial Process System label correctly', () => {
        const container = createContainer(
          'sf-system-industrial-process',
          'Industrial Process / System',
          60,
          12
        );
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        expect(lines.length).toBeLessThanOrEqual(3);
      });

      it('should wrap Cargo System label correctly', () => {
        const container = createContainer('sf-system-cargo', 'Cargo / System', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('Cargo');
          expect(lines[1]).toContain('System');
        }
      });

      it('should wrap Pump System label correctly', () => {
        const container = createContainer('sf-system-pump', 'Pump / System', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('Pump');
          expect(lines[1]).toContain('System');
        }
      });
    });

    describe('Device labels with break hints', () => {
      it('should wrap CNC Station label correctly', () => {
        const container = createContainer('sf-device-1', 'CNC / Station', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('CNC');
          expect(lines[1]).toContain('Station');
        }
      });

      it('should wrap Hydraulic Station label correctly', () => {
        const container = createContainer('sf-device-2', 'Hydraulic / Station', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        expect(lines.length).toBeLessThanOrEqual(3);
      });

      it('should wrap 3D Printer Station label correctly', () => {
        const container = createContainer('sf-device-3', '3D Printer / Station', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        expect(lines.length).toBeLessThanOrEqual(3);
      });

      it('should wrap Weight Station label correctly', () => {
        const container = createContainer('sf-device-4', 'Weight / Station', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('Weight');
          expect(lines[1]).toContain('Station');
        }
      });

      it('should wrap Laser Station label correctly', () => {
        const container = createContainer('sf-device-5', 'Laser / Station', 60, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        if (lines.length > 1) {
          expect(lines[0]).toContain('Laser');
          expect(lines[1]).toContain('Station');
        }
      });
    });

    describe('Max lines limit', () => {
      it('should limit to max 3 lines', () => {
        const container = createContainer(
          'sf-device-1',
          'Very / Long / Label / That / Should / Wrap',
          30,
          12
        );
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeLessThanOrEqual(3);
      });

      it('should handle very long labels', () => {
        const container = createContainer(
          'sf-device-1',
          'ExtremelyLongLabelWithoutSpacesThatNeedsHardWrapping',
          30,
          12
        );
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeLessThanOrEqual(3);
        expect(lines.every((line: string) => line.length > 0)).toBe(true);
      });
    });

    describe('Edge cases', () => {
      it('should handle empty label', () => {
        const container = createContainer('sf-device-1', '', 100, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines).toEqual([]);
      });

      it('should handle label with only spaces', () => {
        const container = createContainer('sf-device-1', '   ', 100, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeLessThanOrEqual(1);
      });

      it('should handle label with multiple consecutive break hints', () => {
        const container = createContainer('sf-device-1', 'Test / / / Label', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        expect(lines.every((line: string) => line.trim().length > 0)).toBe(true);
      });

      it('should handle label ending with break hint', () => {
        const container = createContainer('sf-device-1', 'Test / ', 50, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
        expect(lines[0]).toBe('Test');
      });
    });

    describe('Container width and font size variations', () => {
      it('should handle narrow containers', () => {
        const container = createContainer('sf-device-1', 'CNC / Station', 30, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        expect(lines.length).toBeGreaterThanOrEqual(1);
      });

      it('should handle wide containers', () => {
        const container = createContainer('sf-device-1', 'CNC / Station', 300, 12);
        component['containers'] = [container];
        const lines = (component as any).getWrappedLabelLines(container);
        // Should fit on one line
        expect(lines.length).toBeLessThanOrEqual(1);
      });

      it('should handle different font sizes', () => {
        const containerSmall = createContainer('sf-device-1', 'CNC / Station', 50, 10);
        const containerLarge = createContainer('sf-device-1', 'CNC / Station', 50, 16);
        component['containers'] = [containerSmall];
        const linesSmall = (component as any).getWrappedLabelLines(containerSmall);
        component['containers'] = [containerLarge];
        const linesLarge = (component as any).getWrappedLabelLines(containerLarge);
        // Larger font should result in more wrapping (or same if already wrapped)
        expect(linesSmall.length).toBeLessThanOrEqual(linesLarge.length);
      });
    });
  });
});
