#!/usr/bin/env python3
"""
Test script to verify numeric field handling in Telegraf
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

def publish_numeric_test_data():
    """Publish test data with various numeric fields"""
    
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            
            # Test data with different numeric field names
            test_messages = [
                {
                    "topic": "factory/sensor1/temperature",
                    "payload": {
                        "temperature": 23.5,
                        "unit": "°C",
                        "quality": "good",
                        "humidity": 65.2
                    }
                },
                {
                    "topic": "factory/sensor2/pressure", 
                    "payload": {
                        "pressure": 1013.25,
                        "unit": "hPa",
                        "quality": "good",
                        "voltage": 12.6
                    }
                },
                {
                    "topic": "plc/motor1/speed",
                    "payload": {
                        "speed": 1450.0,
                        "unit": "rpm",
                        "current": 2.3,
                        "power": 450.5
                    }
                },
                {
                    "topic": "sensors/flow1/rate",
                    "payload": {
                        "flow": 125.7,
                        "unit": "L/min",
                        "level": 78.3,
                        "count": 1250
                    }
                }
            ]
            
            for data in test_messages:
                message = json.dumps(data["payload"])
                client.publish(data["topic"], message)
                print(f"Published to {data['topic']}: {data['payload']}")
                time.sleep(0.5)
            
            print("Numeric field test messages published!")
            client.disconnect()
        else:
            print(f"Failed to connect. Return code: {rc}")
    
    client.on_connect = on_connect
    
    try:
        client.connect("localhost", 1883, 60)
        client.loop_start()
        time.sleep(3)
        client.loop_stop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Publishing numeric field test data...")
    publish_numeric_test_data()
    print("Check Telegraf logs and database for proper numeric field storage")
