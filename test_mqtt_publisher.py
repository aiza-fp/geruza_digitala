#!/usr/bin/env python3
"""
Simple MQTT publisher to test the Telegraf setup
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

def publish_test_data():
    """Publish test data to MQTT topics"""
    
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            
            # Publish test messages
            test_data = [
                {
                    "topic": "factory/device1/temperature",
                    "payload": {
                        "value": 25.5,
                        "unit": "°C",
                        "quality": "good",
                        "timestamp": datetime.now().isoformat()
                    }
                },
                {
                    "topic": "factory/device1/pressure", 
                    "payload": {
                        "value": 1013.25,
                        "unit": "hPa",
                        "quality": "good",
                        "timestamp": datetime.now().isoformat()
                    }
                },
                {
                    "topic": "plc/plc1/analog",
                    "payload": {
                        "value": 4.2,
                        "unit": "mA",
                        "quality": "good",
                        "timestamp": datetime.now().isoformat()
                    }
                },
                {
                    "topic": "sensors/sensor1/value",
                    "payload": {
                        "value": 78.3,
                        "unit": "%",
                        "quality": "good",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            ]
            
            for data in test_data:
                message = json.dumps(data["payload"])
                client.publish(data["topic"], message)
                print(f"Published to {data['topic']}: {data['payload']['value']}{data['payload']['unit']}")
                time.sleep(0.5)
            
            print("Test messages published successfully!")
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
    print("Publishing test data to MQTT...")
    publish_test_data()
    print("Check Telegraf logs with: docker-compose logs telegraf")
