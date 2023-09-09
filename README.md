# GrowCube Home Assistant Custom Component

This is a very early version of a Home Assistant integration for the Elecrow GrowCube smart plant watering system.

## Warning

This is still at the _works on my machine_ stage while I understand how it all fits together. Probably doesn't comply with Home Assistant best practices so I can't guarantee there won't be any weird behaviour.

Don't rely on it to keep your plants alive!

The integration doesn't store any persistent state or change any other aspects of HA. If you do get into trouble, just remove any GrowCube devices you added and there should be no traces left behind.

# Status

Creates the following sensors for a GrowCube:

- Temperature
- Humidity
- Moisture reading for each plant sensor

Sensors are updated every 5 minutes if anything in Home Assistant is subscribed to them.

It also adds a device entry to link all the sensors together in the Home Assistant UI.

It may work for multiple GrowCubes but I don't have a way of testing that.


## Installation

Easiest way is to use [HACS](https://hacs.xyz/).
In HACS:
 - Got to Integrations
 - Open the menu and choose *Custom Repositories*
 - Add https://github.com/RobotEdward/homeassistant-growcube
 - Install the integration as normal using HACS and restart Home Assistant 

# Usage

- Give your GrowCube a fixed IP address
- Add a GrowCube device to Home Assistant
- Specify the GrowCube's IP address during the configuration UI
