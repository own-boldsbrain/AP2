"""YSH Viability service application package."""

# The subpackages (events, services, meteo) expose the public API expected by
# the FastAPI application and by the tests.  Keeping this file intentionally
# minimal avoids introducing heavy imports at package initialisation time while
# still enabling ``app.services`` style imports.

__all__ = ["events", "services", "meteo"]
