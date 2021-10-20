from typing import List, Optional
from dataclasses import dataclass, field
from serpyco import number_field

from energytt_platform.api import Endpoint, Context
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import MeteringPointQuery
from meteringpoints_shared.models import \
    MeteringPointFilters, MeteringPointOrdering


class GetMeteringPointList(Endpoint):
    """
    Looks up many Measurements, optionally filtered and ordered.
    """

    @dataclass
    class Request:
        # TODO Validate offset & limit upper/lower bounds:
        offset: int = number_field(default=0, minimum=0)
        limit: int = number_field(default=50, minimum=1, maximum=100)
        filters: Optional[MeteringPointFilters] = field(default=None)
        ordering: Optional[MeteringPointOrdering] = field(default=None)

    @dataclass
    class Response:
        success: bool
        total: int
        meteringpoints: List[MeteringPoint]

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        subject = context.get_subject(required=True)

        query = MeteringPointQuery(session) \
            .is_accessible_by(subject)

        if request.filters:
            query = query.apply_filters(request.filters)

        if request.ordering:
            results = query.apply_ordering(request.ordering)
        else:
            results = query

        results = results \
            .offset(request.offset) \
            .limit(request.limit)

        # if request.ordering:
        #     results = results.apply_ordering(request.ordering)

        return self.Response(
            success=True,
            total=query.count(),
            meteringpoints=results.all(),
        )


class GetMeteringPointDetails(Endpoint):
    """
    Returns details about a single MeteringPoint.
    """

    @dataclass
    class Request:
        gsrn: str

    @dataclass
    class Response:
        success: bool
        meteringpoint: Optional[MeteringPoint]

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        meteringpoint = MeteringPointQuery(session) \
            .is_accessible_by(context.token.subject) \
            .has_gsrn(request.gsrn) \
            .one_or_none()
        # meteringpoint = MeteringPointQuery(session) \
        #     .has_gsrn(request.gsrn) \
        #     .one_or_none()

        return self.Response(
            success=meteringpoint is not None,
            meteringpoint=meteringpoint,
        )
