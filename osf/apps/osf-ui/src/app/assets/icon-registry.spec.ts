import { getIconPath } from './icon-registry';

describe('icon-registry', () => {
  it('resolves CRM business icon without question fallback', () => {
    expect(getIconPath('crm-application')).toBe('assets/svg/business/crm-application.svg');
  });
});

