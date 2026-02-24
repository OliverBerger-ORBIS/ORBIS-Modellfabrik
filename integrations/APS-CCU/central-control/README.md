# CCU

## Topics the CCU will cover

### CCU Topics

#### order a new workpiece
Request to produce a new workpiece or to store a workpiece in the high bay storage.   
Topic: `ccu/order/request`   
Example Message:   
```json
{
  "type": "WHITE",
  "timestamp": "2023-02-02T11:46:19Z",
  "orderType": "PRODUCTION"
}
```
currently `type` can be `WHITE`, `BLUE` or `RED`
`orderType` can be `PRODUCTION` or `STORAGE`

This will produce a response on:  
topic: `ccu/order/response`   
example message:   
```json
{
  "type": "WHITE",
  "timestamp": "2023-02-02T11:46:19Z",
  "orderId": "6c155e43-92d4-4a11-98ef-091ca8e4863d",
  "productionSteps": [
    {
      "id": "c6beb657-5c54-40bf-b123-15be5ce6c8b0",
      "type": "NAVIGATION",
      "source": "START",
      "target": "MILL"
    },
    {
      "id": "77ea3571-ef11-43b3-a28e-44034d159ccd",
      "type": "MILL",
      "command": "PICK",
      "dependentActionId": "c6beb657-5c54-40bf-b123-15be5ce6c8b0"
    },
    {
      "id": "7c592aa0-0b91-40ac-83bb-6ee456cb3a33",
      "type": "MILL",
      "command": "MILL",
      "dependentActionId": "77ea3571-ef11-43b3-a28e-44034d159ccd"
    },
    {
      "id": "bf0190fa-0788-42d9-a1b3-e8284c138069",
      "type": "MILL",
      "command": "DROP",
      "dependentActionId": "7c592aa0-0b91-40ac-83bb-6ee456cb3a33"
    },
    {
      "id": "4ad9be57-12e1-4cab-a413-4fdd04ad8239",
      "type": "NAVIGATION",
      "dependentActionId": "bf0190fa-0788-42d9-a1b3-e8284c138069",
      "source": "MILL",
      "target": "DRILL"
    },
    {
      "id": "77345cd2-de77-4a80-9c48-b350fe2b4de5",
      "type": "DRILL",
      "command": "PICK",
      "dependentActionId": "4ad9be57-12e1-4cab-a413-4fdd04ad8239"
    },
    {
      "id": "43cd56b3-8e2f-4747-981b-da26915cc529",
      "type": "DRILL",
      "command": "DRILL",
      "dependentActionId": "77345cd2-de77-4a80-9c48-b350fe2b4de5"
    },
    {
      "id": "ea571366-19ff-4971-bd63-215e9a65ef74",
      "type": "DRILL",
      "command": "DROP",
      "dependentActionId": "43cd56b3-8e2f-4747-981b-da26915cc529"
    },
    {
      "id": "cc107717-f8cf-4b09-aa3d-15118e7b5a23",
      "type": "NAVIGATION",
      "dependentActionId": "ea571366-19ff-4971-bd63-215e9a65ef74",
      "source": "DRILL",
      "target": "DPS"
    }
  ]
}
```

#### All active orders

The CCU will publish a list of all active orders on the topic `ccu/order/active`. 
The messages will be sent with the option `retain = true` and  only updated once a new order is 
placed or there is a status update for the order which is currently in process.   
Topic: `ccu/order/active`
Example message:   
```json
[
  {
    "type": "WHITE",
    "timestamp": "2023-02-02T11:46:19Z",
    "orderId": "6c155e43-92d4-4a11-98ef-091ca8e4863d",
    "productionSteps": [
      {
        "id": "c6beb657-5c54-40bf-b123-15be5ce6c8b0",
        "type": "NAVIGATION",
        "source": "START",
        "target": "MILL"
      },
      {
        "id": "77345cd2-de77-4a80-9c48-b350fe2b4de5",
        "type": "MILL",
        "command": "PICK",
        "dependentActionId": "c6beb657-5c54-40bf-b123-15be5ce6c8b0"
      },
      {
        "id": "7c592aa0-0b91-40ac-83bb-6ee456cb3a33",
        "type": "MILL",
        "command": "MILL",
        "dependentActionId": "77345cd2-de77-4a80-9c48-b350fe2b4de5"
      },
      {
        "id": "bf0190fa-0788-42d9-a1b3-e8284c138069",
        "type": "MILL",
        "command": "DROP",
        "dependentActionId": "7c592aa0-0b91-40ac-83bb-6ee456cb3a33"
      },
      {
        "id": "4ad9be57-12e1-4cab-a413-4fdd04ad8239",
        "type": "NAVIGATION",
        "dependentActionId": "bf0190fa-0788-42d9-a1b3-e8284c138069",
        "source": "MILL",
        "target": "DRILL"
      },
      {
        "id": "d861b18e-6b76-41a7-9f63-c3ce6699cd45",
        "type": "DRILL",
        "command": "PICK",
        "dependentActionId": "4ad9be57-12e1-4cab-a413-4fdd04ad8239"
      },
      {
        "id": "43cd56b3-8e2f-4747-981b-da26915cc529",
        "type": "DRILL",
        "command": "DRILL",
        "dependentActionId": "d861b18e-6b76-41a7-9f63-c3ce6699cd45"
      },
      {
        "id": "ea571366-19ff-4971-bd63-215e9a65ef74",
        "type": "DRILL",
        "command": "DROP",
        "dependentActionId": "43cd56b3-8e2f-4747-981b-da26915cc529"
      },
      {
        "id": "cc107717-f8cf-4b09-aa3d-15118e7b5a23",
        "type": "NAVIGATION",
        "dependentActionId": "ea571366-19ff-4971-bd63-215e9a65ef74",
        "source": "DRILL",
        "target": "DPS"
      }
    ]
  }
]
```

## Detection of readiness of Modules

class: `ModuleState`  
The states are mutually exclusive, with `READY` having the lowest priority and `BLOCKED` the highest. Meaning if a module is `BLOCKED` it will not be set to `BUSY` or `READY` even if the conditions for those states are met. The same goes for `BUSY` and `READY`.

### BLOCKED

* If the module state containes an entry in the list `errors` of `errorLevel === FATAL`
* or if no `FATAL` error exists and no `actionState` is present

### BUSY

* if `actionState.state` is not `FINISHED` for any command

### READY

* the module state contains load information 
  * if the command of the `actionState` is either `DROP`
  * if the command of the `actionState` is `PICK` and the module type is `HBW`
  * any command has the state `FINISHED` :warning: this is a special case. Here the module will be set to ready but only for the same orderId. This means if a second order should be sent to it, the module will be handled as busy for the new orderId
* the module state does not contain any load information
  * the module will be set to `READY` for any order

## Detection of readiness of FTS

class: `FtsState`

### BLOCKED

* If the module state contains an entry in the list `errors` of `errorLevel === FATAL`
* property `pauses` is set to `true`

The last module serial number will not be set. The FTS has to be reset manually.

### BUSY

* property `driving` is set to `true`
* property `waitingForLoadHandling` this indicates that the FTS has successfully docked at the module and is waiting that either the module loads or unloads a workpiece. To clear this an instant action has to be send. The action will be triggered on a successful `PICK/DROP` command of the module

In case of `waitingForLoadHandling === true` the last module serial number will be set, based on the target of the navigation command.

### READY

only possible if property `driving` is set to `false`

* `waitingForLoadHandling` is set to `false` load information is present and the command is successful
* no load information is present

The last module serial number will be set, based on the target of the navigation command.