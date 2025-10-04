from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os, json
from collections import defaultdict

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data correctly
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "../telemetry_data.json")

with open(DATA_PATH, "r") as f:
    raw_data = json.load(f)

TELEMETRY_DATA = defaultdict(list)
for entry in raw_data:
    TELEMETRY_DATA[entry["region"]].append(entry)

@app.post("/api/latency")
async def latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        data = TELEMETRY_DATA.get(region, [])
        if not data:
            continue
        latencies = [d["latency_ms"] for d in data]
        uptimes = [d["uptime_pct"] for d in data]
        breaches = sum(l > threshold_ms for l in latencies)

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 3),
            "breaches": breaches,
        }

    return result
