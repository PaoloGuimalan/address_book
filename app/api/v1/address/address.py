from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, Body, Form
from sqlalchemy.orm import Session

from api.deps import get_db_session
from utils.logging import get_module_logger

from schemas.user.address import (
    AddressListResponse,
    AddressResponse,
    AddressCreate,
    AddressUpdate,
    AddressPatch,
    AddressSearchNearby,
)
from models.user.account import Account
from services.user.address import address_crud
from api.deps import get_current_account
from typing import Annotated

router = APIRouter(
    prefix="/address", tags=["Address"], dependencies=[Depends(get_current_account)]
)

public_router = APIRouter(prefix="/nearby", tags=["Address"])

logger = get_module_logger(__name__)


@router.get("/my-list", response_model=AddressListResponse)
def my_addresses(
    page: int = Query(
        default=1, ge=1, description="The page number to fetch. Starts at 1."
    ),
    limit: int = Query(
        default=20, ge=1, le=100, description="The maximum results to display per page."
    ),
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Fetch an indexed roster list of active addresses inside the network matrix.
    Utilizes skip and limit query adjustments to preserve connection speed profiles.
    """
    logger.info(
        f"address list requested with batch rules -> Skip Index: {page} | Vol Limit: {limit}"
    )

    owner_id = current_user.id

    address_records = address_crud.list(db, account_id=owner_id, page=page, limit=limit)

    batch_count = len(address_records)

    logger.info(
        f"address delivery successful. Packaged {batch_count} records to address stream."
    )

    return {
        "total_records": batch_count,
        "current_page": page,
        "limit": limit,
        "data": address_records,
    }


@router.get("/{address_id}", response_model=AddressResponse)
def get_address_by_id(
    address_id: int = Path(
        ...,
        gte=1,
        description="The unique primary key auto-increment row ID of the target address.",
    ),
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Fetch comprehensive details for an individual address entry using its unique ID.
    Automatically blocks requests if the target address does not belong to the calling account.
    """
    logger.info(
        f"Account ID {current_user.id} requested dynamic details lookup for Address ID {address_id}."
    )

    address = address_crud.get_by_id(db, address_id=address_id)

    if not address:
        logger.warning(
            f"Lookup aborted. Address Entry ID {address_id} does not exist in the database."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address entry with ID {address_id} was not found.",
        )

    if address.account_id != current_user.id:
        logger.warning(
            f"SECURITY BLOCK: Account ID {current_user.id} attempted to unauthorized view "
            f"Address ID {address_id} owned by Account ID {address.account_id}!"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this address entry profile record.",
        )

    logger.info(
        f"Authorized access approved. Address Entry ID {address_id} dispatched to Owner ID {current_user.id}."
    )
    return address


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_address(
    payload: Annotated[AddressCreate, Form()],
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Register a coordinate-validated address entry securely under the authenticated account.
    """
    owner_id = current_user.id

    logger.info(
        f"Account ID {owner_id} attempting to map new location: '{payload.title}'"
    )

    new_address = address_crud.create_with_owner(
        db, obj_in=payload, account_id=owner_id
    )

    logger.info(
        f"Address Entry ID {new_address.id} successfully created for Account ID {owner_id}."
    )

    return {"message": "Address created successfully"}


@router.delete("/{address_id}", status_code=status.HTTP_200_OK)
def delete_address(
    address_id: int = Path(
        ..., gte=1, description="The unique ID of the address to delete."
    ),
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Permanently removes an address record from your address book.
    Enforces strict ownership authorization checks.
    """
    logger.info(
        f"Account ID {current_user.id} requested deletion of Address ID {address_id}."
    )

    address = address_crud.get_by_id(db, address_id=address_id)

    if not address:
        logger.warning(f"Deletion failed. Address ID {address_id} was not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address entry with ID {address_id} was not found.",
        )

    if address.account_id != current_user.id:
        logger.critical(
            f"SECURITY ALERT: Account ID {current_user.id} attempted to delete "
            f"unauthorized Address ID {address_id} belonging to Account ID {address.account_id}!"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this address entry.",
        )

    address_crud.remove(db, address_id=address_id)

    logger.info(
        f"Address Entry ID {address_id} successfully deleted by Owner ID {current_user.id}."
    )

    return {
        "status": "success",
        "message": f"Address entry with ID {address_id} has been completely deleted.",
    }


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    payload: Annotated[AddressUpdate, Form()],
    address_id: int = Path(
        ..., gte=1, description="The unique row ID of the address to overwrite."
    ),
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Completely replaces an existing address entry inside your address book.
    Every field must be filled and passed inside the HTTP Form Request Body.
    """
    logger.info(
        f"Account ID {current_user.id} requested full Form Body PUT overwrite for Address ID {address_id}."
    )

    address = address_crud.get_by_id(db, address_id=address_id)
    if not address:
        logger.warning(f"Update failed. Address ID {address_id} does not exist.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address entry not found."
        )

    if address.account_id != current_user.id:
        logger.critical(
            f"SECURITY BLOCK: Account ID {current_user.id} unauthorized edit attempt on Address ID {address_id}!"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this address entry.",
        )

    updated_address = address_crud.update(db, db_obj=address, obj_in=payload)

    logger.info(
        f"Address Entry ID {address_id} successfully updated via Form Body PUT by Owner ID {current_user.id}."
    )
    return updated_address


@router.patch("/{address_id}", response_model=AddressResponse)
def patch_address(
    address_id: int = Path(
        ..., gte=1, description="The unique row ID of the address to partially update."
    ),
    payload: AddressPatch = Body(...),
    db: Session = Depends(get_db_session),
    current_user: Account = Depends(get_current_account),
):
    """
    Partially updates an address entry inside your address book.
    Only overwrites the specific fields you provide in the request body.
    """
    logger.info(
        f"Account ID {current_user.id} requested partial PATCH update for Address ID {address_id}."
    )

    address = address_crud.get_by_id(db, address_id=address_id)

    if not address:
        logger.warning(f"Patch aborted. Address ID {address_id} was not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address entry with ID {address_id} was not found.",
        )

    if address.account_id != current_user.id:
        logger.critical(
            f"SECURITY ALERT: Account ID {current_user.id} unauthorized patch attempt "
            f"on Address ID {address_id} owned by Account ID {address.account_id}!"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this address entry.",
        )

    updated_address = address_crud.patch(db, db_obj=address, obj_in=payload)

    logger.info(
        f"Address Entry ID {address_id} successfully updated via PATCH by Owner ID {current_user.id}."
    )
    return updated_address


@public_router.get("/", response_model=list[AddressResponse])
def get_global_addresses_nearby(
    search_params: AddressSearchNearby = Depends(),
    db: Session = Depends(get_db_session),
):
    """
    Publicly retrieve addresses within a specific radius.
    Capped automatically by a limit parameter to safeguard backend bandwidth.
    """
    logger.info(
        f"Public global search around ({search_params.latitude}, {search_params.longitude}) "
        f"within {search_params.radius_km}km | Limit: {search_params.limit}"
    )

    nearby_addresses = address_crud.get_nearby_global(
        db=db,
        center_lat=search_params.latitude,
        center_lon=search_params.longitude,
        radius_km=search_params.radius_km,
        limit=search_params.limit,
    )

    logger.info(
        f"Public global radius search returned {len(nearby_addresses)} entries."
    )
    return nearby_addresses
