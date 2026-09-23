import monitor
from fastapi import HTTPException

# Reuse the proven monitor app and background scheduler, but keep operational
# endpoints minimal in production. The manual /check endpoint is intentionally
# not exposed because it can force repeated upstream market-data requests.
app = monitor.app
app.router.routes = [
    route for route in app.router.routes
    if not (getattr(route, "path", None) in {"/check", "/register"})
]


@app.post("/register")
def register(body: monitor.RegisterBody):
    token = body.token.strip()
    if not (20 <= len(token) <= 4096):
        raise HTTPException(400, "invalid token")
    if body.platform != "android":
        raise HTTPException(400, "unsupported platform")
    if body.protocol not in (1, 2):
        raise HTTPException(400, "unsupported protocol")
    return monitor.register(body)
