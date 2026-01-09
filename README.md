<p align="center">
  <img src="https://refoss.net/cdn/shop/files/refoss_2.png?v=1734414851&width=200" alt="Refoss Logo" width="200">
</p>

# Refoss Integration for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=will-tm&repository=home-assistant-refoss&category=integration)

A custom Home Assistant integration for Refoss energy monitoring devices that uses direct HTTP communication instead of UDP broadcast discovery.

> **Note:** This integration has only been tested on the **EM16** energy monitor. Other devices (EM06, R10) may work but are untested.

## Why This Fork?

The official Refoss integration relies on UDP broadcast discovery, which doesn't work reliably in:
- Multi-VLAN network setups
- Containerized Home Assistant deployments
- Networks with broadcast filtering

This integration eliminates UDP entirely and communicates directly with devices via HTTP.

## Supported Devices

- **EM16** - 16-channel energy monitor (tested)
- **EM06** - 6-channel energy monitor (untested)
- **R10** - Smart plug with energy monitoring (untested)

## Prerequisites

You will need the following information for each device:

| Parameter | Description | Required |
|-----------|-------------|----------|
| **Host IP** | Static IP address of the device | Yes |
| **UUID** | 32-character device identifier | Yes |
| **Port** | HTTP port (default: 80) | No |
| **Device Type** | em16, em06, or r10 | No |
| **Device Name** | Friendly name | No |

### Finding the Device UUID

The UUID is a 32-character hex string that uniquely identifies your device. It is **required** for HTTP communication and must be manually captured since this integration bypasses UDP discovery.

**How to capture the UUID:**

1. **Using Wireshark (Recommended)**
   - Connect a computer to the same network/VLAN as the Refoss device
   - Start Wireshark and filter for UDP port 9989: `udp.port == 9989`
   - The device periodically broadcasts discovery responses containing the UUID
   - Look for JSON data with a `uuid` field in the packet payload

2. **Using tcpdump**
   ```bash
   sudo tcpdump -i any -A port 9989 | grep -i uuid
   ```

3. **From the official Refoss integration logs**
   - Temporarily install the official Refoss integration on the same VLAN
   - Enable debug logging and check for UUID in the logs
   - Then switch to this integration with the captured UUID

**Example UUID:** `1234567890abcdef1234567890abcdef`

> **Important:** The UUID is not the same as the MAC address. It's a unique identifier embedded in the device firmware.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select **Custom repositories**
4. Add the repository URL and select **Integration** as the category
5. Click **Add**
6. Search for "Refoss Energy Monitor" and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the contents to `config/custom_components/refoss/`
3. Restart Home Assistant

## Configuration

### UI Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Refoss**
4. Enter the device details:
   - **Host IP Address**: The static IP of your device
   - **Device UUID**: The 32-character UUID
   - **Port**: HTTP port (default 80)
   - **Device Type**: em16, em06, or r10
   - **Device Name**: A friendly name for the device

### YAML Configuration

Add the following to your `configuration.yaml`:

```yaml
refoss:
  - host: "192.168.1.100"
    uuid: "1234567890abcdef1234567890abcdef"
    device_type: "em16"
    device_name: "Main Panel"
    port: 80
```

For multiple devices:

```yaml
refoss:
  - host: "192.168.1.100"
    uuid: "1234567890abcdef1234567890abcdef"
    device_type: "em16"
    device_name: "Main Panel"
  - host: "192.168.1.101"
    uuid: "abcdef1234567890abcdef1234567890"
    device_type: "em06"
    device_name: "Sub Panel"
```

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `host` | Yes | - | IP address of the device |
| `uuid` | Yes | - | 32-character device UUID |
| `port` | No | 80 | HTTP port |
| `device_type` | No | em16 | Device type (em16, em06, r10) |
| `device_name` | No | em16 | Friendly name for the device |

After adding the YAML configuration, restart Home Assistant. The devices will be automatically imported and appear in the Integrations page.

## Entities

The integration creates the following entities for each channel:

### Sensors
- **Power** (W) - Current power consumption
- **Voltage** (V) - Line voltage
- **Current** (A) - Current draw
- **Power Factor** - Power factor ratio
- **This Month Energy** (kWh) - Energy consumed this month
- **This Month Energy Returned** (kWh) - Energy returned this month

### Switches
- **Channel Toggle** - Turn individual channels on/off (if supported)

## Multiple Devices

You can add multiple Refoss devices by repeating the "Add Integration" process for each device. Each device is identified by its unique UUID.

## Troubleshooting

### Device Not Responding

1. **Verify IP address**: Ensure the device has a static IP and is reachable
   ```bash
   ping 192.168.1.100
   ```

2. **Test HTTP connectivity**:
   ```bash
   curl -X POST http://192.168.1.100/public \
     -H "Content-Type: application/json" \
     -d '{"header":{},"payload":{}}'
   ```

3. **Check UUID**: The UUID must match exactly (case-insensitive)

4. **Check firewall**: Ensure port 80 is open between Home Assistant and the device

### Debug Logging

Enable debug logging by adding to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.refoss: debug
```

## Technical Details

This integration:
- Uses HTTP POST requests to `/public` (or `/config` for R10 devices)
- Authenticates using MD5 message signing
- Polls devices for updates (local polling)
- Does not require cloud connectivity

## License

This project is licensed under the same terms as Home Assistant.

## Credits

Based on the official [refoss-ha](https://pypi.org/project/refoss-ha/) library with modifications for HTTP-only communication.
