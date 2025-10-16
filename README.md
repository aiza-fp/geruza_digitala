# MQTT to TimescaleDB Bridge

This project uses Telegraf to subscribe to MQTT messages from a Mosquitto broker and store the data into a TimescaleDB database. It's designed to work with your Node-RED PLC data simulation setup.

## 🚀 Telegraf Solution

- **Production-Ready**: Battle-tested by thousands of organizations
- **High Performance**: Optimized for high-throughput data collection
- **Built-in Reliability**: Automatic retries, buffering, and error handling
- **Rich Plugin Ecosystem**: 300+ input/output plugins
- **Minimal Configuration**: Simple configuration file, no coding required

## Features

- **MQTT Subscription**: Connects to Mosquitto broker and subscribes to configurable topics
- **Data Filtering**: Filter data by topic, device, sensor type, and value ranges
- **TimescaleDB Storage**: Automatically creates optimized time-series tables
- **JSON Support**: Handles both JSON and plain text MQTT messages
- **Configurable**: Easy configuration via YAML file
- **Logging**: Comprehensive logging to file and console
- **Graceful Shutdown**: Handles shutdown signals properly

## Prerequisites

- Python 3.7 or higher (for test scripts only)
- Docker and Docker Compose (for running Mosquitto, TimescaleDB, and Telegraf)
- Node-RED running locally (for data generation)

## Setup

### 1. Start Docker Services

```bash
docker-compose up -d
```

This will start:
- Mosquitto MQTT broker on port 1883
- TimescaleDB on port 5432
- Telegraf (automatically configured)
- Grafana on port 3000

### 2. Install Python Dependencies (for testing)

```bash
pip install -r requirements.txt
```

## Configuration

### Telegraf Configuration

The Telegraf configuration (`telegraf.conf`) includes:

- **MQTT Input**: Subscribes to multiple topic patterns
- **Data Processing**: JSON parsing and field extraction
- **TimescaleDB Output**: Automatic table creation and data insertion
- **Health Monitoring**: Built-in health check endpoint

Key features:
- Automatic hypertable creation for optimal time-series performance
- JSON data parsing with field mapping
- Device and sensor type extraction from MQTT topics
- Built-in retry logic and error handling

### MQTT Topics

Telegraf uses MQTT topic patterns to subscribe to multiple topics:

- `factory/+/+` - Matches `factory/device1/temperature`, `factory/device2/pressure`, etc.
- `plc/+/+` - Matches `plc/plc1/analog`, `plc/plc2/digital`, etc.
- `sensors/+/+` - Matches `sensors/sensor1/value`, `sensors/sensor2/status`, etc.

### Data Processing

Telegraf automatically:
- Parses JSON messages and extracts values
- Creates timestamps for all received data
- Stores topic information as tags
- Handles connection failures and retries

## Database Schema

Telegraf automatically creates a `mqtt_consumer` table with the following structure:

```sql
CREATE TABLE mqtt_consumer (
    time TIMESTAMPTZ NOT NULL,
    host TEXT,
    topic TEXT,
    timestamp DOUBLE PRECISION,
    value DOUBLE PRECISION
);
```

The table is optimized for time-series data and can be converted to a TimescaleDB hypertable for better performance.

## Data Format

### JSON Messages

The bridge expects JSON messages in this format:

```json
{
  "value": 25.5,
  "unit": "°C",
  "quality": "good",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Plain Text Messages

Plain text messages are stored as-is in the `value` field.

## Monitoring

### View Stored Data

```bash
python view_telegraf_data.py
python view_telegraf_data.py --stats    # Show statistics
python view_telegraf_data.py --device device1  # Filter by device
python view_telegraf_data.py --sensor temperature  # Filter by sensor type
```

### Monitoring

**Telegraf Health Check:**
```bash
curl http://localhost:8080/metrics
```

**View Telegraf Logs:**
```bash
docker-compose logs telegraf
docker-compose logs -f telegraf  # Follow logs in real-time
```

**Check Container Status:**
```bash
docker-compose ps
```

### Grafana Dashboard

Access Grafana at `http://localhost:3000` (admin/admin) to create dashboards for your data.

### Logs

**Telegraf:** Check Docker logs: `docker-compose logs telegraf`

## Example Node-RED Flow

Here's an example Node-RED flow that publishes data to MQTT:

```json
[
  {
    "id": "inject1",
    "type": "inject",
    "name": "Generate PLC Data",
    "props": [
      {
        "p": "payload"
      }
    ],
    "repeat": "5",
    "crontab": "",
    "once": false,
    "onceDelay": 0.1,
    "topic": "",
    "payload": "{\"value\": 25.5, \"unit\": \"°C\", \"quality\": \"good\"}",
    "payloadType": "json",
    "x": 150,
    "y": 100,
    "wires": [
      [
        "mqtt_out"
      ]
    ]
  },
  {
    "id": "mqtt_out",
    "type": "mqtt out",
    "name": "Publish to MQTT",
    "topic": "factory/device1/temperature",
    "qos": "0",
    "retain": "false",
    "broker": "broker1",
    "x": 400,
    "y": 100,
    "wires": []
  }
]
```

## Troubleshooting

### Telegraf Issues

1. **Telegraf Not Starting**: 
   ```bash
   docker-compose logs telegraf
   docker-compose restart telegraf
   ```

2. **No Data Being Stored**:
   - Check MQTT connection: `docker-compose logs telegraf | grep mqtt`
   - Verify topic patterns in `telegraf.conf`

3. **Database Connection Issues**:
   ```bash
   # Check if TimescaleDB is accessible
   docker-compose exec telegraf ping timescaledb
   ```

### Data Processing Issues

1. **No Data Being Stored**: Check if MQTT messages are being received
2. **Database Connection Failed**: Check if TimescaleDB is running and accessible
3. **Permission Denied**: Ensure the database user has proper permissions

### Data Not Stored

1. **Check Filters**: Verify your data matches the configured filters
2. **Check Topics**: Ensure the MQTT topics match your subscription patterns
3. **Check Logs**: Look for error messages in the log file or Docker logs

### Performance Issues

1. **Database Indexes**: Both solutions create indexes automatically
2. **Telegraf Performance**: Adjust `metric_batch_size` and `flush_interval` in `telegraf.conf`
3. **Data Retention**: Set up data retention policies in TimescaleDB

### Common Solutions

1. **Restart Services**:
   ```bash
   docker-compose restart
   ```

2. **Check All Services**:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

## License

This project is open source and available under the MIT License.
