"""Support for light switches controlled via a custom Telnet connection."""
import logging
import telnetlib
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 50505  # Set the default port to 50505

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None) -> None:
    """Set up the Telnet switch platform."""
    devices = config.get("devices", [])
    for device in devices:
        host = device.get(CONF_HOST)
        base_command = device.get("base_command")
        number_of_lights = device.get("number_of_lights")
        lights = [CustomTelnetLight(host, DEFAULT_PORT, i, base_command) for i in range(1, number_of_lights + 1)]
        add_entities(lights)

class CustomTelnetLight(SwitchEntity):
    """Representation of an individual light switch controlled via Telnet."""

    def __init__(self, host, port, light_number, base_command):
        """Initialize the light."""
        self._host = host
        self._port = port
        self._light_number = light_number
        self._base_command = base_command
        self._state = False
        self._name = f"Light {light_number} @ {host}"

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._send_command(1)
        self._state = True

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._send_command(0)
        self._state = False

    def _send_command(self, state):
        """Send command to the light."""
        command = self._generate_command(state)
        try:
            with telnetlib.Telnet(self._host, self._port) as telnet:
                telnet.write(command.encode('ASCII') + b"\r\n")
        except Exception as e:
            _LOGGER.error(f"Failed to send command to {self._name}: {e}")

    def _generate_command(self, state):
        """Generate the command string to send to the device."""
        # Adjust the command generation logic as per your device's requirements
        return self._base_command + (f"{self._light_number}" if state else f"a{self._light_number - 1}")

    def update(self):
        """Fetch new state data for this light."""
        # Implement state update logic if available
