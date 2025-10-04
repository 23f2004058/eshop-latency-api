from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os

# Load telemetry data from JSON
with open(os.path.join(os.path.dirname(__file__), "../telemetry_data.json")) as f:
    telemetry_data = json.load(f)

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

class LatencyRequest(BaseModel):
    regions: list
    threshold_ms: float

@app.post("/api/latency")
def get_latency_metrics(req: LatencyRequest):
    response = {}
    for region in req.regions:
        region_data = [r for r in telemetry_data if r["region"] == region]
        if not region_data:
            response[region] = {}
            continue
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        breaches = sum(1 for l in latencies if l > req.threshold_ms)
        response[region] = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes), 3),
            "breaches": breaches
        }
    return response
