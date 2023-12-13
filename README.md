# Climate Wrapper


This integration is rather specific and I don't expect many users to find it useful. It was developed out of a personal need and suboptimal circumstances. In essence, this integration will "wrap" another climate entity and convert it into a "dumb" heating switch. This is because temperatur sensor of my climate entity measures nonsense and this way I can overwrite it. It will then set the target temperature to 1 Degree Celcius above/below the measured temperature to turn it on/off.

**This integration will set up the following platforms.**

Platform | Description
-- | --
`climate` | New Climate which wraps your input.
`sensor` | Shows information regarding external changes.

## Installation

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
1. Download _all_ the files from the `custom_components/integration_blueprint/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Climate Wrapper"

### Using HACS
1. Add this repository as a custom repository (type: integration)
1. Search for "Climate Wrapper" in the integratons
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Climate Wrapper"


## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***
