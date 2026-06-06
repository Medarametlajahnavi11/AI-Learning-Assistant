#!/usr/bin/env python
import subprocess
import sys
import os

if __name__ == "__main__":
    port = os.getenv("PORT", "8000")
    subprocess.run(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", port],
        check=True
    )
