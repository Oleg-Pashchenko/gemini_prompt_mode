from flask import Flask, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry

app = Flask(__name__)

# Define a counter metric
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])


# Define a custom Flask route decorator to track requests
def track_requests(rule):
    def decorator(f):
        def wrapped(*args, **kwargs):
            REQUEST_COUNT.labels(method=request.method, endpoint=rule).inc()
            return f(*args, **kwargs)

        return app.route(rule)(wrapped)

    return decorator


# Register custom routes
@app.route('/')
def index():
    return 'Hello, World!'


# Register routes using the custom decorator
@app.route('/endpoint1')
@track_requests('/endpoint1')
def endpoint1():
    return 'This is endpoint 1'


@app.route('/endpoint2')
@track_requests('/endpoint2')
def endpoint2():
    return 'This is endpoint 2'


# Endpoint for Prometheus to scrape metrics
@app.route('/metrics')
def metrics():
    registry = CollectorRegistry()
    registry.register(REQUEST_COUNT)
    data = generate_latest(registry)
    return data, 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
