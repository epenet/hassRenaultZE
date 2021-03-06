# Configuration

The component is generic and tries to adapt to all supported models. It is mostly configured via the UI however, due to limitations on the Renault API, some features may need to be configured manually.

## HVAC
On some models (eg. Zoe40), HVAC status always reports as off. On other models (eg. Zoe50) it is not available at all. HVAC control is therefore not available as a standard climate entity, but needs to be controlled via a service call to `renault.ac_start`.

Please note that the service `renault.ac_stop` does not provide errors, but appears to have no effect on some models.
Following MyRenaultApp documentation, HVAC is started between 5 and 50 min.

This is an example script to start HVAC :
```yaml
# Scripts
script:
  start_hvac:
  alias: Start HVAC
  sequence:
  - service: renault.ac_start
      data:
      vin: VF1xxxxxxx
      temperature: 21
  # optional notification to device
  - device_id: xxxxxxxxxxxxx
    domain: mobile_app
    type: notify
    message: Starting HVAC at 21°C
    title: Renault ZOE
  # optional delay to avoid multiple launch 
  - delay:
      seconds: 300
  mode: single
  icon: mdi:snowflake
```

This is an example of a fake switch, whose state will match whether the script is still running (ie. was started less than 300 seconds ago) :
```yaml
# Switches
switch:
  - platform: template
    switches:
      # Start AC now for five minutes (see script)
      zoe_ac_start:
        friendly_name: "A/C"
        icon_template: mdi:fan
        value_template: "{{ is_state('script.start_hvac', 'on') }}"
        turn_on:
          service: homeassistant.turn_on
          data:
            entity_id: script.start_hvac
        turn_off:
          service: homeassistant.turn_off
          data:
            entity_id: script.start_hvac
```
