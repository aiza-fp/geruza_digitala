# Industrial IoT Monitoring System

A complete industrial IoT monitoring solution that collects MQTT data from PLCs and sensors, stores it in TimescaleDB, and provides a web-based dashboard for monitoring and visualization. Features automated setup with Docker Compose and proper timezone handling for global deployments.

## 🚀 System Architecture

- **MQTT Broker**: Eclipse Mosquitto for reliable message queuing
- **Data Collection**: Telegraf for high-performance data ingestion
- **Time-Series Database**: TimescaleDB for optimized time-series storage
- **Web Dashboard**: Django-based monitoring interface
- **Visualization**: Grafana for advanced analytics and dashboards
- **Automated Setup**: Zero-configuration deployment with Docker Compose

## ✨ Key Features

- **Automated Setup**: One-command deployment with automatic database setup
- **Timezone Aware**: Proper UTC storage with local timezone display
- **Real-time Monitoring**: Live data collection and visualization
- **Production Ready**: Docker-based deployment with health checks
- **Scalable**: TimescaleDB hypertables for high-performance time-series data
- **Multi-Protocol**: Support for JSON and plain text MQTT messages
- **Web Interface**: Modern Django-based dashboard for data monitoring
- **Admin Panel**: Built-in user management and system administration

## Prerequisites

- Docker and Docker Compose
- Python 3.7+ (for test scripts only)
- Node-RED (optional, for data generation)

## 🚀 Quick Start

### Automated Setup (Recommended)

Your Django application has automated setup! When you run `docker-compose up`, everything will be configured automatically.

```bash
# Clone and start everything with one command
git clone <repository-url>
cd geruza_digitala
docker-compose up --build
```

#### ✨ What Gets Automated

The entrypoint script automatically handles:
1. **Database Connection**: Waits for TimescaleDB to be ready
2. **Database Timezone**: Sets database to UTC timezone
3. **Migrations**: Runs Django database migrations
4. **Superuser Creation**: Creates admin user (admin/admin123)
5. **Static Files**: Collects static files for production
6. **Application Start**: Starts the Django application

#### 🎯 Usage

**First Time Setup:**
```bash
# Clean start (removes all containers and volumes)
docker-compose down -v
docker-compose up --build
```

**Regular Usage:**
```bash
# Start everything
docker-compose up

# Start in background
docker-compose up -d
```

#### 🔧 What Happens During Startup

1. **TimescaleDB** starts and becomes healthy
2. **Webapp** waits for database to be ready
3. **Database timezone** is set to UTC
4. **Django migrations** are applied
5. **Superuser** is created (if it doesn't exist)
6. **Static files** are collected
7. **Django application** starts

### Access Your Applications

- **Web Dashboard**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (admin/admin123)
- **Grafana**: http://localhost:3000 (admin/admin)

### Manual Setup (if needed)

```bash
# Install Python dependencies for testing
pip install -r requirements.txt
```

## Configuration

### System Components

#### Telegraf (Data Collection)
- **MQTT Input**: Subscribes to multiple topic patterns
- **Data Processing**: JSON parsing and field extraction
- **TimescaleDB Output**: Automatic table creation and data insertion
- **Timezone Handling**: UTC storage for consistency

#### Django Web Application
- **Automated Setup**: Database migrations and user creation
- **Timezone Aware**: Displays data in local timezone (Europe/Madrid)
- **Admin Interface**: Built-in user management
- **Real-time Monitoring**: Live data visualization

#### TimescaleDB
- **Hypertables**: Optimized time-series performance
- **UTC Storage**: Consistent timezone handling
- **Automatic Indexing**: Performance optimization

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
    -- Dynamic fields are added automatically based on incoming data
    -- Examples: temperature, pressure, humidity, voltage, current, etc.
);
```

**Key Features:**
- **Hypertable**: Automatically converted for optimal time-series performance
- **UTC Storage**: All timestamps stored in UTC for consistency
- **Automatic Indexing**: Optimized for time-based queries
- **Dynamic Fields**: Only `time`, `host`, and `topic` are guaranteed; other numeric fields are created dynamically by Telegraf as data arrives
- **Field Selection**: Web interface allows users to select which numeric field to visualize

## Data Format

### JSON Messages

The system expects JSON messages in this format:

```json
{
  "value": 25.5,
  "unit": "°C",
  "quality": "good",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Node-RED Integration

For Node-RED, use this simple format:

```javascript
msg.payload = {
    pressure: Number((1 + Math.random() * 0.2).toFixed(2)),
    timestamp: Date.now()
};
```

### Timezone Handling

- **Storage**: All data is stored in UTC for consistency
- **Display**: Automatically converted to local timezone (Europe/Madrid)
- **Node-RED**: Can send any timestamp format - Telegraf uses its own timestamp

## Monitoring & Management

### Web Dashboard

Access the Django web interface at http://localhost:8000 for:
- Real-time data monitoring with dynamic field selection
- Device and sensor management
- Historical data visualization for any numeric field
- Field-based chart visualization
- User administration

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin) for:
- Advanced analytics and dashboards
- Custom time-series visualizations
- Alerting and notifications
- Data export capabilities

### System Monitoring

**Container Status:**
```bash
docker-compose ps
```

**View Logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs webapp
docker-compose logs telegraf
docker-compose logs timescaledb

# Follow logs in real-time
docker-compose logs -f webapp
```

**Database Access:**
```bash
# Connect to TimescaleDB
docker-compose exec timescaledb psql -U admin -d factory

# View recent data
SELECT time, host, topic, * 
FROM mqtt_consumer 
ORDER BY time DESC 
LIMIT 10;

# View available numeric fields for a topic
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'mqtt_consumer' 
AND column_name NOT IN ('time', 'host', 'topic')
AND data_type IN ('real', 'double precision', 'numeric', 'integer', 'bigint', 'smallint')
ORDER BY column_name;
```

### Testing Data Collection

```bash
# Send test data
python test_mqtt_publisher.py

# View collected data
docker-compose exec timescaledb psql -U admin -d factory -c "
SELECT time, timezone('UTC', time) as utc_time, timezone('Europe/Madrid', time) as madrid_time 
FROM mqtt_consumer 
ORDER BY time DESC 
LIMIT 5;"
```

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

### Automated Setup Issues

1. **Webapp Not Starting**:
   ```bash
   # Check webapp logs
   docker-compose logs webapp
   
   # Restart webapp
   docker-compose restart webapp
   ```

2. **Database Migration Failures**:
   ```bash
   # Run migrations manually
   docker-compose exec webapp python manage.py migrate
   
   # Create superuser manually
   docker-compose exec webapp python manage.py createsuperuser
   ```

3. **Complete Restart**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

4. **Fresh Start (Clean Volumes)**:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

5. **Check All Services**:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

### Data Collection Issues

1. **No Data Being Stored**:
   ```bash
   # Check Telegraf logs
   docker-compose logs telegraf
   
   # Check MQTT connection
   docker-compose logs telegraf | grep mqtt
   ```

2. **Database Connection Issues**:
   ```bash
   # Check TimescaleDB health
   docker-compose exec timescaledb pg_isready -U admin
   
   # Test database connection
   docker-compose exec webapp python manage.py dbshell
   ```

### Timezone Issues

1. **Incorrect Timestamps**:
   ```bash
   # Check database timezone
   docker-compose exec timescaledb psql -U admin -d factory -c "SHOW timezone;"
   
   # Set timezone manually if needed
   docker-compose exec timescaledb psql -U admin -d factory -c "ALTER DATABASE factory SET timezone = 'UTC';"
   ```

### Performance Issues

1. **Slow Queries**:
   ```bash
   # Check database performance
   docker-compose exec timescaledb psql -U admin -d factory -c "SELECT * FROM pg_stat_activity;"
   ```

2. **High Memory Usage**:
   ```bash
   # Monitor container resources
   docker stats
   ```

### Common Solutions

1. **Complete Restart**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Fresh Start (Clean Volumes)**:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

3. **Check All Services**:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

## 🚀 Automated Setup Features

This system includes a comprehensive automated setup that handles:

### Django Application
- **Automatic Database Setup**: Creates tables and applies migrations
- **User Management**: Creates admin user automatically
- **Static Files**: Collects and serves static files
- **Timezone Configuration**: Sets up proper UTC storage with local display
- **Health Checks**: Monitors application health

### Database Configuration
- **TimescaleDB Setup**: Configures time-series optimizations
- **Timezone Handling**: Sets UTC timezone for consistency
- **Hypertable Creation**: Optimizes for time-series queries
- **Index Management**: Creates proper indexes automatically

### Container Orchestration
- **Service Dependencies**: Ensures proper startup order
- **Health Checks**: Monitors service availability
- **Automatic Restart**: Handles service failures gracefully
- **Volume Management**: Persistent data storage

### Development vs Production
- **Development**: Includes debug tools and test scripts
- **Production**: Optimized for performance and security
- **Environment Variables**: Configurable for different deployments
- **Docker Compose**: Easy deployment and scaling

## 📁 Project Structure

```
geruza_digitala/
├── docker-compose.yaml          # Container orchestration
├── telegraf.conf               # Data collection configuration
├── mosquitto.conf              # MQTT broker configuration
├── test_mqtt_publisher.py      # Test data generator
├── requirements.txt            # Python dependencies
├── webapp/                     # Django web application
│   ├── Dockerfile             # Webapp container definition
│   ├── entrypoint.sh          # Automated setup script
│   ├── manage.py              # Django management
│   ├── requirements.txt       # Python dependencies
│   ├── webapp/                # Django project settings
│   ├── monitoring/            # Data monitoring app
│   ├── users/                 # User management app
│   └── templates/             # HTML templates
└── README.md                   # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the automated setup
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Industrial IoT Monitoring**
