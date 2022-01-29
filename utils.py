simMutex = None

def publish(mqtt, topic, value):
    if mqtt is not None:
        mqtt.publish(topic, value)

def subscribe(mqtt, topic):
    if mqtt is not None:
        mqtt.subscribe(topic)