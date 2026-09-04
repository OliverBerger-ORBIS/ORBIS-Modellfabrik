/** V1 UC-01 read contract — parameterized T-SQL (see docs/07-analysis/uc01-tt-persistence-gap-2026-09.md). */

export const LIST_WORKPIECES_SQL = `
SELECT TOP (@limit)
  w.workpiece_id,
  w.type,
  w.current_state,
  w.last_location,
  w.first_seen_at,
  w.last_seen_at
FROM dbo.workpiece w
WHERE (@from_ts IS NULL OR w.last_seen_at >= @from_ts)
  AND (@to_ts IS NULL OR w.first_seen_at <= @to_ts)
ORDER BY w.last_seen_at DESC;
`;

export const LIST_TIMELINE_SQL = `
SELECT TOP (@limit)
  e.id,
  e.ts,
  e.event_type,
  e.topic,
  e.source,
  e.module_type,
  e.module_serial,
  e.order_id,
  e.workpiece_id,
  e.workpiece_type,
  e.action,
  e.action_state,
  o.order_type
FROM dbo.shopfloor_event e
LEFT JOIN dbo.shopfloor_order o ON o.order_id = e.order_id
WHERE e.workpiece_id = @nfc
  AND (@from_ts IS NULL OR e.ts >= @from_ts)
  AND (@to_ts IS NULL OR e.ts <= @to_ts)
  AND (
    e.event_type = N'WORKPIECE_INTAKE'
    OR (
      e.action_state = N'FINISHED'
      AND (e.topic LIKE N'module/%' OR e.topic LIKE N'fts/%')
    )
  )
ORDER BY e.ts ASC, e.id ASC;
`;
