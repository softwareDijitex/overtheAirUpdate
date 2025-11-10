from datetime import datetime
from typing import List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.models import customer
from app.models.machine import Machine
from app.models.customer import Customer
from app.utils.auth import verify_token
from app import get_database

machine_bp = APIRouter(tags=["machines"])
security = HTTPBearer()

# ---------- Auth dependencies ----------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# ---------- Schemas ----------
Status = Literal["active", "inactive", "decommissioned"]

class MachineBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = ""
    location: Optional[str] = ""
    status: Optional[Status] = "active"
    mac_address: Optional[str] = ""

class MachineCreate(MachineBase):
    customer_id: str

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[Status] = None
    mac_address: Optional[str] = None

class MachineResponse(MachineBase):
    id: str
    customer_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ---------- Customer-scoped routes ----------
@machine_bp.get("/customer/{customer_id}", response_model=List[MachineResponse])
async def get_customer_machines(customer_id: str, current_user: dict = Depends(get_current_user)):
    # if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
    #     raise HTTPException(status_code=403, detail="Unauthorized access")
    print(f"Customer id : {customer_id}")
    machines = Machine.get_customer_machines(customer_id)
    return [MachineResponse(**m.to_dict()) for m in machines]

# @machine_bp.get("/customer/{customer_id}", response_model=List[MachineResponse])
# async def get_customer_machines(customer_id: str):
#     # if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
#     #     raise HTTPException(status_code=403, detail="Unauthorized access")
#     print(f"Customer id : {customer_id}")
#     machines = Machine.get_customer_machines(customer_id)
#     return [MachineResponse(**m.to_dict()) for m in machines]

@machine_bp.post("/customer/{customer_id}", response_model=MachineResponse, status_code=201)
async def create_customer_machine(customer_id: str, body: MachineCreate, current_user: dict = Depends(get_current_user)):
    if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Verify customer exists
    cust = Customer.find_by_customer_id(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    # MAC validation (optional but safer)
    if body.mac_address and not Machine.is_valid_mac_address(body.mac_address):
        raise HTTPException(status_code=400, detail="Invalid MAC address format")
    normalized_mac = Machine.normalize_mac_address(body.mac_address or "")
    if normalized_mac and Machine.mac_address_exists(normalized_mac):
        raise HTTPException(status_code=400, detail="MAC address already exists")

    machine = Machine(
        name=body.name,
        customer_id=customer_id,
        description=body.description or "",
        location=body.location or "",
        status=body.status or "active",
        mac_address=normalized_mac,
    )
    machine_id = machine.save()
    if not machine_id:
        raise HTTPException(status_code=500, detail="Failed to create machine")
    return MachineResponse(**machine.to_dict())

@machine_bp.get("/customer/{customer_id}/{machine_id}", response_model=MachineResponse)
async def get_customer_machine(customer_id: str, machine_id: str, current_user: dict = Depends(get_current_user)):
    if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    m = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    return MachineResponse(**m.to_dict())

@machine_bp.put("/customer/{customer_id}/{machine_id}", response_model=MachineResponse)
async def update_customer_machine(customer_id: str, machine_id: str, body: MachineUpdate, current_user: dict = Depends(get_current_user)):
    if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # ensure exists
    m = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.location is not None:
        updates["location"] = body.location
    if body.status is not None:
        updates["status"] = body.status
    if body.mac_address is not None:
        if body.mac_address and not Machine.is_valid_mac_address(body.mac_address):
            raise HTTPException(status_code=400, detail="Invalid MAC address format")
        new_mac = Machine.normalize_mac_address(body.mac_address or "")
        # If changing MAC, ensure global uniqueness
        if new_mac and new_mac != m.mac_address and Machine.mac_address_exists(new_mac):
            raise HTTPException(status_code=400, detail="MAC address already exists")
        updates["mac_address"] = new_mac

    if updates:
        ok = Machine.update_machine_for_customer(customer_id, machine_id, updates)
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to update machine")

    m2 = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
    return MachineResponse(**m2.to_dict())

@machine_bp.delete("/customer/{customer_id}/{machine_id}")
async def delete_customer_machine(customer_id: str, machine_id: str, current_user: dict = Depends(get_current_user)):
    if not (current_user.get("is_admin") or current_user["customer_id"] == customer_id):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    m = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    ok = Machine.delete_machine_for_customer(customer_id, machine_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete machine")
    return {"message": "Machine deleted successfully"}

# ---------- Admin-scoped routes ----------
@machine_bp.post("/admin", response_model=MachineResponse, status_code=201)
async def admin_create_machine(body: MachineCreate, admin_user: dict = Depends(get_admin_user)):
    cust = Customer.find_by_customer_id(admin_user.get("customer_id_override", "") or body.__dict__.get("customer_id", ""))  # optional override if you ever pass it
    # Explicit customer_id is required:
    if not hasattr(body, "customer_id"):
        raise HTTPException(status_code=400, detail="Customer ID is required")
    cust = Customer.find_by_customer_id(getattr(body, "customer_id"))
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    if body.mac_address and not Machine.is_valid_mac_address(body.mac_address):
        raise HTTPException(status_code=400, detail="Invalid MAC address format")
    normalized_mac = Machine.normalize_mac_address(body.mac_address or "")
    if normalized_mac and Machine.mac_address_exists(normalized_mac):
        raise HTTPException(status_code=400, detail="MAC address already exists")

    machine = Machine(
        name=body.name,
        customer_id=getattr(body, "customer_id"),
        description=body.description or "",
        location=body.location or "",
        status=body.status or "active",
        mac_address=normalized_mac,
    )
    mid = machine.save()
    if not mid:
        raise HTTPException(status_code=500, detail="Failed to create machine")
    return MachineResponse(**machine.to_dict())

@machine_bp.get("/admin/customer/{customer_id}", response_model=List[MachineResponse])
async def admin_get_customer_machines(customer_id: str, admin_user: dict = Depends(get_admin_user)):
    machines = Machine.get_customer_machines(customer_id)
    return [MachineResponse(**m.to_dict()) for m in machines]

@machine_bp.get("/admin/{machine_id}", response_model=MachineResponse)
async def admin_get_machine(machine_id: str, admin_user: dict = Depends(get_admin_user)):
    m = Machine.get_machine_by_id(machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    return MachineResponse(**m.to_dict())

@machine_bp.put("/admin/{machine_id}", response_model=MachineResponse)
async def admin_update_machine(machine_id: str, body: MachineUpdate, admin_user: dict = Depends(get_admin_user)):
    m = Machine.get_machine_by_id(machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.location is not None:
        updates["location"] = body.location
    if body.status is not None:
        updates["status"] = body.status
    if body.mac_address is not None:
        if body.mac_address and not Machine.is_valid_mac_address(body.mac_address):
            raise HTTPException(status_code=400, detail="Invalid MAC address format")
        new_mac = Machine.normalize_mac_address(body.mac_address or "")
        if new_mac and new_mac != m.mac_address and Machine.mac_address_exists(new_mac):
            raise HTTPException(status_code=400, detail="MAC address already exists")
        updates["mac_address"] = new_mac

    if updates:
        ok = Machine.update_machine_by_id(machine_id, updates)
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to update machine")

    m2 = Machine.get_machine_by_id(machine_id)
    return MachineResponse(**m2.to_dict())

@machine_bp.delete("/admin/{machine_id}")
async def admin_delete_machine(machine_id: str, admin_user: dict = Depends(get_admin_user)):
    m = Machine.get_machine_by_id(machine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    ok = Machine.delete_machine_by_id(machine_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to delete machine")
    return {"message": "Machine deleted successfully"}

@machine_bp.get("/admin/all", response_model=List[MachineResponse])
async def admin_get_all_machines(admin_user: dict = Depends(get_admin_user)):
    machines = Machine.get_all_machines()
    return [MachineResponse(**m.to_dict()) for m in machines]
