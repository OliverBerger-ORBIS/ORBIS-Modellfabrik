# OSF-UI: Browser console debug (`osf.debug`)

Opt-in verbose logging in the Angular app (development). **Default:** quiet console (no fixture spam, no DPS/AIQS detail logs).

**Source of truth (code):** `osf/apps/osf-ui/src/app/utils/osf-console-debug.ts`

---

## Enable (DevTools)

1. Open **DevTools** → **Console**.
2. Run:

```js
localStorage.setItem('osf.debug', '1');
location.reload();
```

## Disable

```js
localStorage.removeItem('osf.debug');
location.reload();
```

---

## What you get when `osf.debug` is `1`

| Area | Behaviour |
|------|-----------|
| **testing-fixtures** | `resolvePath` logs resolved fixture paths (e.g. orders log path). |
| **mock-dashboard** | Logs when MessageMonitor forwarding is set up, tab fixture preset name, live MQTT client mode. |
| **MessageValidation** | Logs fallback mode (schemas not loaded). |
| **MessageMonitor** | Logs summary after loading persisted topics from `localStorage`. |
| **Shopfloor module tab** | DPS/AIQS **summary** logs (orderId, timestamps, flags) — **not** full state objects (those can contain huge base64 camera frames and confuse DevTools). |

**Note:** Full DPS/AIQS payloads are **not** logged on purpose — logging large `data:image/...` strings can make Chrome show `net::ERR_INVALID_URL` in the console even when the app is fine.

---

## Related

- Message Monitor duplicate topics (Sprint 18): [message-monitor-duplicate-topics-2026-03.md](../07-analysis/message-monitor-duplicate-topics-2026-03.md)
