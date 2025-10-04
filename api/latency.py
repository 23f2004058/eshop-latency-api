from fastapi import FastAPI, Request, Response
import json
import os
import numpy as np
from collections import defaultdict

app = FastAPI()

# Load telemetry data
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "../telemetry_data.json")

with open(DATA_PATH, "r") as f:
    raw_data = json.load(f)

TELEMETRY_DATA = defaultdict(list)
for entry in raw_data:
    TELEMETRY_DATA[entry["region"]].append(entry)

# Handle POST and OPTIONS explicitly
@app.api_route("/api/latency", methods=["POST", "OPTIONS"])
async def latency(request: Request):
    # ✅ Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

    # Process POST request
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

    # ✅ Add CORS headers to the response
    return Response(
        content=json.dumps(result),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
