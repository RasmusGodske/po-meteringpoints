from energytt_platform.api import Application, ScopedGuard

from meteringpoints_shared.config import TOKEN_SECRET

from .endpoints import (
    GetMeteringPointList,
    GetMeteringPointDetails,
    # OnboardMeteringPointsFromWebAccessCode,
    # OnboardMeteringPointsFromCPR,
    # OnboardMeteringPointsFromCVR,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    return Application.create(
        name='MeteringPoints API',
        secret=TOKEN_SECRET,
        health_check_path='/health',
        endpoints=(
            ('POST', '/list', GetMeteringPointList(), [ScopedGuard('meteringpoints.read')]),
            ('GET',  '/details', GetMeteringPointDetails(), [ScopedGuard('meteringpoints.read')]),
            # ('POST', '/onboard/web-access-code', OnboardMeteringPointsFromWebAccessCode()),
            # ('POST', '/onboard/cpr', OnboardMeteringPointsFromCPR()),
            # ('POST', '/onboard/cvr', OnboardMeteringPointsFromCVR()),
        ),
    )
