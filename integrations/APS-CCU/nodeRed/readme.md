# NodeRed Files for Docker

This Folder contains the Files to build the Dockerimage containing

* `flows.json` - all existing flows
* `flows_cred.json` - flow credentials
* `package.json` - contains the additional flows and more information
* `settings.js` - settings for all and everything can be modified here
* `factsheets` - folder containing the factsheets for the modules
* `Dockerfile` - the Dockerfile to build the image

## Acces to the flows while running

* http://127.0.0.1:1880/#flow/

This configuration was developed using these [instructions](https://nodered.org/docs/getting-started/docker)

## Safety

until now there are no settings set to prevent acces to the flows and the nodeRed interface. 
This can be changed in the `settings.js` file.

# NodeRed Functionality

## MQTT

The NodeRed connects to the MQTT Broker and subscribe the moduletopics.
The module topics are spezified in the readmes of the modules.

## Flows

Each FLow deals with one module.
The basic structure is always the same and is described [here](https://miro.com/app/board/uXjVME0te50=/?share_link_id=163723106179).

The individual modules are described in the ModuleProjects in a separate readme.

### Flow 1: "NodeRed Globals"

This flow sets all global variables that apply to all modules.
These include:
- MQTT connection data
- MQTT message templates for the modules
- MQTT TOPIC for the NodeRedInstance