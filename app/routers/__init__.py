from .health import ping
from .auth import auth_routes
from .library_management import library_management_routes
from .car_race_management import car_race_management_routes
from .session_management import session_management_routes

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
add_routes(library_management_routes, routers, [], False)
add_routes(car_race_management_routes, routers, [], False)
add_routes(session_management_routes, routers, [], False)