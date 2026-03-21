/**
 * Opt-in verbose browser console output (fixtures, mock dashboard, optional services).
 *
 * **Documentation:** `docs/04-howto/osf-ui-console-debug.md`
 *
 * Enable in DevTools Console:
 *   localStorage.setItem('osf.debug', '1');
 *   location.reload();
 *
 * Disable:
 *   localStorage.removeItem('osf.debug');
 *   location.reload();
 */
export const OSF_CONSOLE_DEBUG_KEY = 'osf.debug';
export const OSF_CONSOLE_DEBUG_VALUE = '1';

export function isOsfConsoleDebugEnabled(): boolean {
  try {
    return typeof localStorage !== 'undefined' && localStorage.getItem(OSF_CONSOLE_DEBUG_KEY) === OSF_CONSOLE_DEBUG_VALUE;
  } catch {
    return false;
  }
}
