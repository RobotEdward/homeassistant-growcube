# Warning

- Very early version only tested on my GrowCube and HomeAssistant instance.

# Status

Creates the following sensors for a GrowCube:

- Temperature
- Humidity
- Moisture reading for each plant sensor

Sensors are updated every 5 minutes.

It also adds a device entry to link all the sensors together in the Hass UI.

It may work for multiple GrowCubes but I don't have a way of testing that.

# Usage

- Give your GrowCube a fixed IP address
- Add a GrowCube device to Home Assistant
- Specify the GrowCube's IP address during the configuration UI
