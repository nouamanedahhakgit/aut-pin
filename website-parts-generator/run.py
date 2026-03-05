#!/usr/bin/env python3
"""Run website-parts-generator API on port 8010."""
import uvicorn
from config import PORT

if __name__ == "__main__":
    uvicorn.run("route:app", host="0.0.0.0", port=PORT, reload=True)
