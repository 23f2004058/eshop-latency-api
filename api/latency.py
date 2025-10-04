from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# ✅ Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow any origin
    allow_methods=["POST"],     # only POST requests are needed
    allow_headers=["*"],        # allow all headers
)

# --- Load telemetry data once ---
with open("telemetry_data.json", "r") as f:
    TELEMETRY_DATA = json.load(f)

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
