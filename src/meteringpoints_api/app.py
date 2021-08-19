from energytt_platform.api import Application

from .endpoints import GetMeteringPointDetails, GetMeteringPointList


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    return Application.create(
        name='MeteringPoints API',
        health_check_path='/health',
        endpoints=(
            ('POST', '/list', GetMeteringPointList()),
            ('GET',  '/details', GetMeteringPointDetails()),
        )
    )
