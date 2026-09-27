"""IndexAlert probability release runtime.

Loads the equity-only constituent guard before importing the full v17
production stack so all scheduled and on-demand stock probability screening
uses the guarded history loader.
"""
import stock_recommendations_guard  # noqa: F401
from production_v17 import app
