from sqlalchemy.orm import Session
from models.user.address import Address
from schemas.user.address import AddressCreate, AddressUpdate
from services.geocoding.geo import geo_service
from utils.logging import get_module_logger
from geopy.distance import geodesic
from typing import List

logger = get_module_logger(__name__)


class CRUDAddress:

    def list(
        self, db: Session, account_id: str, page: int = 1, limit: int = 100
    ) -> list[Address]:
        """
        Function for generating address list
        """

        return (
            db.query(Address)
            .filter(Address.account_id == account_id)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, obj_in: AddressCreate, account_id: int
    ) -> Address:
        """
        Persists a coordinate-validated location entry securely tied to an Account ID.
        """
        lat, lon = geo_service.resolve_gps_coordinates(
            street_address=obj_in.street_address,
            city=obj_in.city,
            state=obj_in.state,
            postal_code=obj_in.postal_code,
            country=obj_in.country,
        )

        db_obj = Address(
            account_id=account_id,
            title=obj_in.title,
            street_address=obj_in.street_address,
            city=obj_in.city,
            state=obj_in.state,
            postal_code=obj_in.postal_code,
            country=obj_in.country,
            latitude=lat,
            longitude=lon,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, address_id: int) -> Address | None:
        """
        Retrieves a single address record by its primary key ID.
        """
        return db.query(Address).filter(Address.id == address_id).first()

    def remove(self, db: Session, address_id: int) -> None:
        """
        Deletes the target address record completely from the database.
        """
        db_obj = db.query(Address).filter(Address.id == address_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()

    def update(self, db: Session, db_obj: Address, obj_in: AddressUpdate) -> Address:
        """
        Overwrites the parameters of an existing Address model with the incoming fields.
        """
        update_data = obj_in.model_dump()

        if update_data.get("latitude") is None or update_data.get("longitude") is None:
            logger.info(
                "PUT fields missing custom GPS markers. Re-running automated geolocation."
            )
            lat, lon = geo_service.resolve_gps_coordinates(
                street_address=obj_in.street_address,
                city=obj_in.city,
                state=obj_in.state,
                postal_code=obj_in.postal_code,
                country=obj_in.country,
            )
            update_data["latitude"] = lat
            update_data["longitude"] = lon
        else:
            logger.info(
                f"PUT manual coordinates detected. Overriding with user input: ({update_data['latitude']}, {update_data['longitude']})"
            )

        # Overwrite all fields on the active database entity row
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def patch(self, db: Session, db_obj: Address, obj_in: AddressUpdate) -> Address:
        """
        Partially updates an existing Address entry by applying only the fields provided.
        Null or blank fields count as not provided, since every column is non-nullable.
        """
        update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        location_fields = ["street_address", "city", "state", "postal_code", "country"]

        if "latitude" in update_data or "longitude" in update_data:
            logger.info(
                "PATCH custom coordinate pins intercepted. Applying manual update."
            )
            if "latitude" not in update_data:
                update_data["latitude"] = db_obj.latitude
            if "longitude" not in update_data:
                update_data["longitude"] = db_obj.longitude

        elif any(field in update_data for field in location_fields):
            logger.info(
                "PATCH text locations modified without custom markers. Re-running geolocation fallback."
            )
            lat, lon = geo_service.resolve_gps_coordinates(
                street_address=update_data.get("street_address", db_obj.street_address),
                city=update_data.get("city", db_obj.city),
                state=update_data.get("state", db_obj.state),
                postal_code=update_data.get("postal_code", db_obj.postal_code),
                country=update_data.get("country", db_obj.country),
            )
            update_data["latitude"] = lat
            update_data["longitude"] = lon

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_nearby_global(
        self,
        db: Session,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int = 20,
    ) -> List[Address]:
        """
        Retrieves public address entries within a kilometer radius,
        sorted by distance and capped by a maximum count threshold.
        """
        all_addresses = db.query(Address).all()

        center_point = (center_lat, center_lon)
        filtered_addresses = []

        for address in all_addresses:
            address_point = (address.latitude, address.longitude)
            calculated_distance = geodesic(center_point, address_point).kilometers

            if calculated_distance <= radius_km:
                address.distance_from_center = round(calculated_distance, 2)
                filtered_addresses.append(address)

        filtered_addresses.sort(key=lambda x: getattr(x, "distance_from_center", 0))

        return filtered_addresses[:limit]


address_crud = CRUDAddress()
