#!/bin/bash

# Django entrypoint script for automated setup
set -e

echo "🚀 Starting Django setup..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database to be ready..."
    while ! pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER"; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "✅ Database is ready!"
}

# Function to configure database timezone
configure_db_timezone() {
    echo "🌍 Configuring database timezone to UTC..."
    PGPASSWORD="$DATABASE_PASSWORD" psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "ALTER DATABASE $DATABASE_NAME SET timezone = 'UTC';" || echo "⚠️  Could not set database timezone (might already be set)"
}

# Function to run Django setup
setup_django() {
    echo "🔧 Setting up Django..."
    
    # Wait for database
    wait_for_db
    
    # Configure database timezone
    configure_db_timezone
    
    # Run migrations
    echo "📦 Running database migrations..."
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    echo "👤 Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('✅ Superuser already exists')
"
    
    # Collect static files
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput
    
    echo "✅ Django setup completed!"
}

# Run setup
setup_django

# Start the application
echo "🚀 Starting Django application..."
exec "$@"
