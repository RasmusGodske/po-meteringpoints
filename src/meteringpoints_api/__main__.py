from .app import create_app


create_app().run_debug(
    host='0.0.0.0',
    port=9093,
)
