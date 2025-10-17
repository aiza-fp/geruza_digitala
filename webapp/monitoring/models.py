from django.db import models, connection
from django.core.exceptions import FieldError


class MqttData(models.Model):
    """Model representing the mqtt_consumer table from TimescaleDB."""
    
    time = models.DateTimeField(db_column='time', primary_key=True)
    host = models.TextField(db_column='host')
    topic = models.TextField(db_column='topic')
    
    class Meta:
        managed = False  # This is a read-only model for existing table
        db_table = 'mqtt_consumer'
        ordering = ['-time']
    
    def __str__(self):
        return f"{self.host} - {self.topic} - {self.time}"
    
    @classmethod
    def get_distinct_hosts(cls):
        """Get all distinct hosts with their last activity time."""
        return cls.objects.values('host').distinct().annotate(
            last_seen=models.Max('time')
        ).order_by('-last_seen')
    
    @classmethod
    def get_topics_for_host(cls, host_id):
        """Get all distinct topics for a specific host."""
        return cls.objects.filter(host=host_id).values('topic').distinct().order_by('topic')
    
    @classmethod
    def get_time_series_data(cls, host_id, topic_name, start_time=None, end_time=None):
        """Get time series data for a specific host and topic."""
        queryset = cls.objects.filter(host=host_id, topic=topic_name)
        
        if start_time:
            queryset = queryset.filter(time__gte=start_time)
        if end_time:
            queryset = queryset.filter(time__lte=end_time)
            
        return queryset.order_by('time')
    
    @classmethod
    def get_numeric_columns(cls):
        """Get all numeric columns from the mqtt_consumer table."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'mqtt_consumer' 
                AND column_name NOT IN ('time', 'host', 'topic')
                AND data_type IN ('real', 'double precision', 'numeric', 'integer', 'bigint', 'smallint')
                ORDER BY column_name
            """)
            return [{'name': row[0], 'type': row[1]} for row in cursor.fetchall()]
    
    @classmethod
    def get_numeric_columns_for_topic(cls, host_id, topic_name):
        """Get numeric columns that have non-null values for a specific topic."""
        with connection.cursor() as cursor:
            # First get all numeric columns
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'mqtt_consumer' 
                AND column_name NOT IN ('time', 'host', 'topic')
                AND data_type IN ('real', 'double precision', 'numeric', 'integer', 'bigint', 'smallint')
                ORDER BY column_name
            """)
            columns = cursor.fetchall()
            
            # Check which columns have data for this specific topic
            available_columns = []
            for column_name, data_type in columns:
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM mqtt_consumer 
                        WHERE host = %s AND topic = %s AND {column_name} IS NOT NULL
                        LIMIT 1
                    """, [host_id, topic_name])
                    count = cursor.fetchone()[0]
                    if count > 0:
                        available_columns.append({'name': column_name, 'type': data_type})
                except Exception:
                    # Skip columns that cause errors (e.g., if they don't exist)
                    continue
            
            return available_columns
    
    @classmethod
    def get_time_series_data_with_field(cls, host_id, topic_name, field_name, start_time=None, end_time=None):
        """Get time series data for a specific host, topic, and field."""
        queryset = cls.objects.filter(host=host_id, topic=topic_name)
        
        if start_time:
            queryset = queryset.filter(time__gte=start_time)
        if end_time:
            queryset = queryset.filter(time__lte=end_time)
            
        # Use raw SQL to access the dynamic field
        with connection.cursor() as cursor:
            sql = f"""
                SELECT time, {field_name}
                FROM mqtt_consumer 
                WHERE host = %s AND topic = %s
            """
            params = [host_id, topic_name]
            
            if start_time:
                sql += " AND time >= %s"
                params.append(start_time)
            if end_time:
                sql += " AND time <= %s"
                params.append(end_time)
                
            sql += " ORDER BY time"
            
            cursor.execute(sql, params)
            return cursor.fetchall()