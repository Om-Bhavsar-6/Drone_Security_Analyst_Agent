from fastapi.testclient import TestClient
from app.main import app, security_alerts

client = TestClient(app)

# Import the indexer and the alert analysis function
from app.indexer import indexer
from app.main import analyze_security_rules

# Trigger a couple of frames manually to have data
import asyncio

async def add_frames():
    frames = [
        {"timestamp":"2026-08-18T00:01:00","lat":18.5204,"lon":73.8567,"alt":15.0,"location":"Main Gate","frame_desc":"A lone individual in a dark hoodie pacing back and forth near the fence line."},
        {"timestamp":"2026-08-18T06:15:00","lat":18.5206,"lon":73.8569,"alt":20.0,"location":"North Perimeter","frame_desc":"Clear field of view, deer grazing near the tree line."}
    ]
    for packet in frames:
        telemetry_ctx = {"timestamp":packet["timestamp"],"lat":packet["lat"],"lon":packet["lon"],"alt":packet["alt"],"location":packet["location"]}
        db_entry = {"id":len(indexer.get_all())+1,"timestamp":packet["timestamp"],"location":packet["location"],"telemetry":telemetry_ctx,"description":packet["frame_desc"]}
        indexer.add_frame(db_entry)
        # Check for alert using the same logic as the background task
        alert = analyze_security_rules(telemetry_ctx, packet["frame_desc"])
        if alert:
            security_alerts.append(alert)

asyncio.run(add_frames())

print("Logs:", client.get('/logs').json())
print("Alerts:", client.get('/alerts').json())
print("Search 'truck':", client.post('/search', json={"query":"truck"}).json())
print("Chat bonus:", client.post('/chat-bonus', json={"query":"Tell me about the truck sightings."}).json())