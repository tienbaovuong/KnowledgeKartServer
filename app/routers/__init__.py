from .health import ping
from .auth import auth_routes

def add_routes(routes, routers, tags, internal: bool = False):
    if internal:
        prefix = '/internal_api/v1'
    else:
        prefix = '/api/v1'
    for route in routes:
        routers.append({
            'router': route,
            'tags': tags,
            'prefix': prefix
        })

routers = []

routers.append({
    'router': ping.router
})
add_routes(auth_routes, routers, [], False)