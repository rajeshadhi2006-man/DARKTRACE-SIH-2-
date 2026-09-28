"""
DARKTRACE-X // Forensic Browser Crime Pattern Intelligence Engine
Exhaustive catalog and classification of 80+ desktop, mobile, privacy, open-source,
enterprise, historical, and developer browsers mapped to cybercrime behavioral patterns,
OPSEC failure detection, and threat actor de-anonymization vectors.
"""
from darktrace_x_backend import *  # fallback
# Or direct import from darktrace-x backend
import sys, os
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dtx_backend = os.path.join(base_dir, "darktrace-x", "backend")
if dtx_backend not in sys.path:
    sys.path.insert(0, dtx_backend)
from app.services.browser_crime_pattern_engine import *
