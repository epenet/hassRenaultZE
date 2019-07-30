# hassRenaultZE
A custom component for [Home Assistant](http://home-assistant.io/) to add battery status from the MyRenault services.

This is based on work by [jamesremuscat](https://github.com/jamesremuscat/pyze)

## What's Available?
The custom component will create a sensor with the battery charge level (in %), together with the following attributes:

* plugged: false
* remaining_range: 151
* last_update: 2019-01-07T07:33:48
* charging: false

A few point to note. The `remaining_range` is in Kilometres, and the `charge_level` is in %.

Regarding the updates, the sensor will attempt to run a "deep" update (ie. send a request for the car to update it's status on the server) every 20 minutes. This is based on both an internal flag and the last_update.
Attempts to update within 20 minutes will be logged as warnings in the home assistant log. The warning message will be: "Send SMS Error" (sic)

## Getting started
Initially, you'll need to make a note of your vehicule VIN, and register with MyRenault application. You will need to add the vin, the language code for your country, the username and the password to your configuration file.

To install the component, you will need to copy the four py files to you local configuration folder:
```
 - .homeassistant
 | - custom_components
 | | - renaultze
 | | | - __init__.py
 | | | - manifest.json
 | | | - sensor.py
 | | | - myrenaultservice
 | | | | - __init__.py
 | | | | - MyRenaultService.py
```

In your configuration.yaml, you will need to add a sensor:
```
sensor:
  - platform: renaultze
    name: MyCarBattery
    username: myemail@address.com
    password: !secret renaultze_password
    vin: XXXXXXXX
    android_lng: fr_FR
```

## Converting attributes to sensors
Template sensors can be added to your configuration.yaml to display the attributes as sensors.
```
sensor:
  - platform: template
    sensors:
      mycar_plugged:
        value_template: "{{ {{ state_attr('sensor.mycarbattery' , 'plugged') }}"
        friendly_name: "Plugged"
  - platform: template
    sensors:
      mycar_charging:
        value_template: "{{ state_attr('sensor.mycarbattery' , 'charging') }}"
        friendly_name: "Charging"
  - platform: template
    sensors:
      mycar_remaining_range:
        value_template: "{{ state_attr('sensor.mycarbattery' , 'remaining_range') }}"
        friendly_name: "Range"
        unit_of_measurement: "km"
```

## Logging
If you are having issues with the component, please enable debug logging in your configuration.yaml, for example:
```
logger:
  default: warn
  logs:
    custom_components.sensor.renaultze: debug
```
