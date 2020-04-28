from functools import partial

from django.utils.timezone import make_aware

from pytz import UTC

as_utc = partial(make_aware, timezone=UTC)
