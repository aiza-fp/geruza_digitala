# MQTT Monitoring Web Application

A Django-based web application for monitoring MQTT data stored in TimescaleDB.

## Features

- **Three-tier Authentication**: Admin, Editor, and Viewer roles
- **Host Dashboard**: View all MQTT hosts and their activity
- **Topic Management**: Browse topics for each host
- **Dynamic Field Selection**: Choose which numeric field to visualize for each topic
- **Interactive Charts**: Time-series visualization with Chart.js for any numeric field
- **Data Export**: CSV export functionality for selected fields (Editor/Admin only)
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5

## Quick Start

### Using Docker Compose (Recommended)

The Django web application has automated setup! When you run `docker-compose up`, everything will be configured automatically.

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin (admin/admin123)
   - Grafana: http://localhost:3000 (admin/admin)

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

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create admin user:**
   ```bash
   python manage.py create_admin
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## User Roles

### Admin
- Full access to all features
- User management
- System administration
- Data export capabilities

### Editor
- View all hosts and topics
- Advanced filtering and search
- Data export capabilities
- Chart visualization

### Viewer
- Basic read-only access
- View assigned hosts/topics
- Chart visualization

## API Endpoints

- `GET /` - Dashboard (hosts list)
- `GET /host/<host_id>/` - Host detail (topics list)
- `GET /host/<host_id>/topic/<topic_name>/fields/` - Field selection for topic
- `GET /host/<host_id>/topic/<topic_name>/field/<field_name>/` - Topic chart for specific field
- `GET /api/host/<host_id>/topic/<topic_name>/field/<field_name>/data/` - Chart data API
- `GET /export/host/<host_id>/topic/<topic_name>/field/<field_name>/` - CSV export

## Database Schema

The application connects to the existing `mqtt_consumer` table in TimescaleDB:

```sql
CREATE TABLE mqtt_consumer (
    time TIMESTAMPTZ NOT NULL,
    host TEXT,
    topic TEXT,
    -- Dynamic numeric fields are added automatically by Telegraf
    -- Examples: temperature, pressure, humidity, voltage, current, etc.
);
```

**Key Features:**
- **Dynamic Fields**: Only `time`, `host`, and `topic` are guaranteed fields
- **Field Discovery**: Application automatically discovers available numeric fields for each topic
- **Field Selection**: Users must select a numeric field before viewing charts
- **Flexible Data**: Supports any numeric field that Telegraf creates from incoming MQTT data

## User Workflow

### How to View Data

1. **Access Dashboard**: Navigate to the main dashboard to see all available hosts
2. **Select Host**: Click on a host to see all its topics
3. **Choose Topic**: Click on a topic to see available numeric fields
4. **Select Field**: Choose which numeric field you want to visualize
5. **View Chart**: See the time-series chart for the selected field
6. **Export Data**: Download CSV data for the selected field (Editor/Admin only)

### Field Selection Process

- Only topics with numeric data will show available fields
- Fields are discovered dynamically from the database
- Users must select a field before viewing charts
- Each field can be visualized independently

## Configuration

Environment variables in `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_HOST=timescaledb
DATABASE_NAME=factory
DATABASE_USER=admin
DATABASE_PASSWORD=admin
DATABASE_PORT=5432
```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Production Deployment

The application is configured for production with:
- Gunicorn WSGI server
- Static file serving
- Security best practices
- Docker containerization

## 🧪 Testing the Application

### 1. Generate Test Data
```bash
# Run the MQTT publisher to generate test data
python test_mqtt_publisher.py

# Or run the numeric fields test
python test_numeric_fields.py
```

### 2. View Data in Web App
1. Go to http://localhost:8000
2. Login with admin/admin123
3. You should see hosts listed on the dashboard
4. Click on a host to see its topics
5. Click on a topic to view the interactive chart

### 3. Test Different User Roles
```bash
# Create additional users via Django admin
docker-compose exec webapp python manage.py shell

# In the Python shell:
from users.models import User
User.objects.create_user(username='editor', password='editor123', role='editor')
User.objects.create_user(username='viewer', password='viewer123', role='viewer')
```

## 📊 Data Flow

```
MQTT Sensors → Mosquitto → Telegraf → TimescaleDB → Django Web App
```

1. **MQTT Sensors** publish data to Mosquitto broker
2. **Telegraf** subscribes to MQTT topics and stores data in TimescaleDB
3. **Django Web App** reads from TimescaleDB and displays interactive charts
4. **Users** can view, filter, and export data based on their role

## 🔧 Management Commands

### Create Admin User
```bash
docker-compose exec webapp python manage.py create_admin
```

### View Logs
```bash
# Web app logs
docker-compose logs webapp

# All services logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f webapp
```

### Restart Services
```bash
# Restart webapp only
docker-compose restart webapp

# Restart all services
docker-compose restart
```

## Troubleshooting

### Database Connection Issues
- Ensure TimescaleDB is running: `docker-compose ps`
- Check database credentials in `.env`
- Verify network connectivity between containers

### No Data Displayed
- Check if MQTT data is being received
- Verify Telegraf is running: `docker-compose logs telegraf`
- Check database for data: `docker-compose exec timescaledb psql -U admin -d factory -c "SELECT COUNT(*) FROM mqtt_consumer;"`
- Check if numeric fields exist for topics: `docker-compose exec timescaledb psql -U admin -d factory -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'mqtt_consumer' AND column_name NOT IN ('time', 'host', 'topic');"`

### No Fields Available for Topic
- Ensure the topic has numeric data in the database
- Check if Telegraf is creating numeric fields from the MQTT data
- Verify the MQTT message format includes numeric values

### Permission Errors
- Ensure proper user roles are assigned
- Check if user has required permissions for specific actions

### Web App Not Loading
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs webapp`
- Restart service: `docker-compose restart webapp`

### Complete Restart
```bash
docker-compose down
docker-compose up --build
```

### Fresh Start (Clean Volumes)
```bash
docker-compose down -v
docker-compose up --build
```

## License

This project is part of the MQTT to TimescaleDB monitoring system.
