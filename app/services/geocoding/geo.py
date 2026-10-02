import logging
from fastapi import HTTPException, status
from geopy.geocoders import Nominatim
from utils.logging import get_module_logger

logger = get_module_logger(__name__)


class GeocodingService:
    def __init__(self, user_agent: str = "address_book_factory_app"):
        self.geolocator = Nominatim(user_agent=user_agent)

    def resolve_gps_coordinates(
        self, street_address: str, city: str, state: str, postal_code: str, country: str
    ) -> tuple[float, float]:
        """
        Communicates with external mapping APIs to translate address parameters
        into a tuple of float coordinates: (latitude, longitude).
        """
        query_string = f"{street_address}, {city}, {state}, {postal_code}, {country}"

        try:
            location = self.geolocator.geocode(query_string, timeout=5)

            if not location:
                logger.warning(
                    f"Geocoding lookup failed for query string: '{query_string}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The provided address could not be resolved to valid GPS coordinates.",
                )

            logger.info(
                f"Geocoding network success! Resolved to: Lat {location.latitude}, Lon {location.longitude}"
            )
            return location.latitude, location.longitude

        except HTTPException:
            raise
        except Exception as error:
            logger.critical(
                f"External geocoding driver pipeline error connection exception: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="External Geolocation mapping server is temporarily unavailable or timed out.",
            )


geo_service = GeocodingService()
