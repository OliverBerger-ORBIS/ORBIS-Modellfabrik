# Example: FTS Spin Before Docking

This example demonstrates a simple modification to the Central Control Unit (CCU) logic. In this change, we make the FTS (Factory Transport System) perform a 360-degree turn before docking to a module.

This serves as a test case to verify that changes in the local development environment are correctly deployed and executed on the physical hardware.

## Concept

To make a visible change without altering complex logic, we inject two 180-degree turn commands (`Direction.BACK`) when the FTS arrives at a target module but before the actual docking sequence begins.

## Code Change

File: `central-control/src/modules/fts/navigation/navigator-service.ts`

```typescript
diff --git a/central-control/src/modules/fts/navigation/navigator-service.ts b/central-control/src/modules/fts/navigation/navigator-service.ts
index 87f8ebe..0a1965f 100644
--- a/central-control/src/modules/fts/navigation/navigator-service.ts
+++ b/central-control/src/modules/fts/navigation/navigator-service.ts
@@ -295,6 +295,31 @@ export class NavigatorService {
       if ('module' in targetNode) {
         console.log('Found a module in path, docking to it');
 
+        // Before docking turn 360° to for a small visible effect
+        nodes.push({
+          id: actionNode.id,
+          linkedEdges,
+          action: {
+            type: FtsCommandType.TURN,
+            id: randomUUID(),
+            metadata: {
+              direction: Direction.BACK,
+            },
+          },
+        });
+        
+        nodes.push({
+          id: actionNode.id,
+          linkedEdges,
+          action: {
+            type: FtsCommandType.TURN,
+            id: randomUUID(),
+            metadata: {
+              direction: Direction.BACK,
+            },
+          },
+        });
+
         // Before docking, we need to check if we face the proper direction
         if (nodeAction.type === FtsCommandType.TURN || nodeAction.type === FtsCommandType.PASS) {
           console.log(`Adding another action before docking: ${nodeAction.type}`);
```
