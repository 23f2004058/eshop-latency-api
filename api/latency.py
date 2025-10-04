from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
with open(os.path.join(os.path.dirname(__file__), "../telemetry_data.json")) as f:
    TELEMETRY_DATA = json.load(f)

@app.post("/api/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    result = {}

    for region in regions:
        data = TELEMETRY_DATA.get(region, [])
        if not data:
            continue

        latencies = [d["latency_ms"] for d in data]
        uptimes = [d["uptime_pct"] for d in data]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 3),
            "p95_latency": round(float(np.percentile(latencies, 95)), 3),
            "avg_uptime": round(float(np.mean(uptimes)), 3),
            "breaches": int(sum(l > threshold for l in latencies))
        }

    return result
