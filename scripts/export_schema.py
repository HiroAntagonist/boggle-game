
import json
import os
import sys

# Add src to path so imports work
sys.path.append(os.getcwd())

from src.api_server import app

def generate_schema():
    openapi_schema = app.openapi()

    with open('openapi.json', 'w') as f:
        json.dump(openapi_schema, f, indent=2)

    print("✅ Generated openapi.json from local app")

if __name__ == "__main__":
    generate_schema()
