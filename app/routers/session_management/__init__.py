from . import session_manager, session

session_management_routes = [
    session_manager.router,
    session.router
]