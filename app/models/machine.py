from datetime import datetime
import uuid
import re
from typing import List, Optional, Dict, Any

from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from app import get_database


class Machine:
    """
    Stored as subdocuments in customers collection:
      {
        customer_id: "...",
        ...,
        machines: [
          {
            id, name, customer_id, description, location, status, mac_address,
            created_at, updated_at
          }
        ]
      }
    """

    def __init__(
        self,
        name: str,
        customer_id: str,
        description: str = "",
        location: str = "",
        status: str = "active",
        mac_address: str = "",
        _id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = _id or str(uuid.uuid4())
        self.name = name
        self.customer_id = customer_id
        self.description = description
        self.location = location
        self.status = status
        self.mac_address = self.normalize_mac_address(mac_address)
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "customer_id": self.customer_id,
            "description": self.description,
            "location": self.location,
            "status": self.status,
            "mac_address": self.mac_address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Machine":
        return Machine(
            name=data["name"],
            customer_id=data["customer_id"],
            description=data.get("description", ""),
            location=data.get("location", ""),
            status=data.get("status", "active"),
            mac_address=data.get("mac_address", ""),
            _id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # ---------- Validation helpers ----------
    @staticmethod
    def is_valid_mac_address(mac_address: str) -> bool:
        if not mac_address:
            return True
        clean = re.sub(r"[:-]", "", mac_address.upper())
        if len(clean) != 12:
            return False
        try:
            int(clean, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def normalize_mac_address(mac_address: str) -> str:
        if not mac_address:
            return ""
        clean = re.sub(r"[^0-9A-Fa-f]", "", mac_address.upper())
        if len(clean) != 12:
            return mac_address  # leave as-is if malformed; validator will catch
        return ":".join([clean[i : i + 2] for i in range(0, 12, 2)])

    @staticmethod
    def mac_address_exists(mac_address: str) -> bool:
        try:
            if not mac_address:
                return False
            db = get_database()
            normalized = Machine.normalize_mac_address(mac_address)
            return (
                db.customers.count_documents({"machines.mac_address": normalized}, limit=1)
                > 0
            )
        except Exception:
            return False

    # ---------- CRUD (as subdocuments) ----------
    def save(self) -> Optional[str]:
        """Push into the correct customer's `machines` array."""
        try:
            db = get_database()
            result = db.customers.update_one(
                {"customer_id": self.customer_id},
                {"$push": {"machines": self.to_dict()}},
            )
            return self.id if result.modified_count > 0 else None
        except (ServerSelectionTimeoutError, PyMongoError) as e:
            print(f"Mongo error saving machine: {e}")
            return None
        except Exception as e:
            print(f"Error saving machine: {e}")
            return None

    @staticmethod
    def get_customer_machines(customer_id: str) -> List["Machine"]:
        try:
            db = get_database()
            doc = db.customers.find_one(
                {"customer_id": customer_id}, {"machines": 1}, max_time_ms=5000
            )
            machines = doc.get("machines", []) if doc else []
            return [Machine.from_dict(m) for m in machines]
        except Exception as e:
            print(f"Error get_customer_machines: {e}")
            return []

    # @staticmethod
    # def find_by_machine_id_for_customer(customer_id: str, machine_id: str) -> Optional["Machine"]:
    #     """Find a machine by id under a specific customer."""
    #     try:
    #         db = get_database()
    #         doc = db.customers.find_one(
    #             {"customer_id": customer_id, "machines.id": machine_id},
    #             {"machines.$": 1},
    #             max_time_ms=5000,
    #         )
    #         if not doc or "machines" not in doc or not doc["machines"]:
    #             return None
    #         return Machine.from_dict(doc["machines"][0])
    #     except Exception as e:
    #         print(f"Error find_by_machine_id_for_customer: {e}")
    #         return None

    @staticmethod
    def find_by_machine_id_for_customer(customer_id: str, machine_id: str) -> Optional["Machine"]:
        """Find a machine by id under a specific customer."""
        try:
            db = get_database()
            doc = db.customers.find_one(
                {"customer_id": customer_id, "machines.id": machine_id},
                {"machines": {"$elemMatch": {"id": machine_id}}},
                max_time_ms=5000,
            )
            if not doc or "machines" not in doc or not doc["machines"]:
                return None
            return Machine.from_dict(doc["machines"][0])
        except Exception as e:
            print(f"Error find_by_machine_id_for_customer: {e}")
            return None


    # @staticmethod
    # def get_machine_by_id(machine_id: str) -> Optional["Machine"]:
    #     """Admin: find any machine by global id across customers."""
    #     try:
    #         db = get_database()
    #         doc = db.customers.find_one(
    #             {"machines.id": machine_id}, {"machines.$": 1}, max_time_ms=5000
    #         )
    #         if not doc or "machines" not in doc or not doc["machines"]:
    #             return None
    #         return Machine.from_dict(doc["machines"][0])
    #     except Exception as e:
    #         print(f"Error get_machine_by_id: {e}")
    #         return None

    @staticmethod
    def get_machine_by_id(machine_id: str) -> Optional["Machine"]:
        """Admin: find any machine by global id across customers."""
        try:
            db = get_database()
            doc = db.customers.find_one(
                {"machines.id": machine_id},
                {"machines": {"$elemMatch": {"id": machine_id}}},
                max_time_ms=5000,
            )
            if not doc or "machines" not in doc or not doc["machines"]:
                return None
            return Machine.from_dict(doc["machines"][0])
        except Exception as e:
            print(f"Error get_machine_by_id: {e}")
            return None


    @staticmethod
    def update_machine_for_customer(customer_id: str, machine_id: str, updates: Dict[str, Any]) -> bool:
        """Customer-scoped update using positional operator."""
        try:
            updates = {f"machines.$.{k}": v for k, v in updates.items()}
            updates["machines.$.updated_at"] = datetime.utcnow()
            db = get_database()
            res = db.customers.update_one(
                {"customer_id": customer_id, "machines.id": machine_id},
                {"$set": updates},
            )
            return res.modified_count > 0
        except Exception as e:
            print(f"Error update_machine_for_customer: {e}")
            return False

    @staticmethod
    def update_machine_by_id(machine_id: str, updates: Dict[str, Any]) -> bool:
        """Admin-scoped update by global machine id (no customer_id needed)."""
        try:
            updates = {f"machines.$.{k}": v for k, v in updates.items()}
            updates["machines.$.updated_at"] = datetime.utcnow()
            db = get_database()
            res = db.customers.update_one({"machines.id": machine_id}, {"$set": updates})
            return res.modified_count > 0
        except Exception as e:
            print(f"Error update_machine_by_id: {e}")
            return False

    @staticmethod
    def delete_machine_for_customer(customer_id: str, machine_id: str) -> bool:
        try:
            db = get_database()
            res = db.customers.update_one(
                {"customer_id": customer_id},
                {"$pull": {"machines": {"id": machine_id}}},
            )
            return res.modified_count > 0
        except Exception as e:
            print(f"Error delete_machine_for_customer: {e}")
            return False

    @staticmethod
    def delete_machine_by_id(machine_id: str) -> bool:
        """Admin: remove any machine by global id."""
        try:
            db = get_database()
            res = db.customers.update_one(
                {"machines.id": machine_id},
                {"$pull": {"machines": {"id": machine_id}}},
            )
            return res.modified_count > 0
        except Exception as e:
            print(f"Error delete_machine_by_id: {e}")
            return False

    @staticmethod
    def get_all_machines() -> List["Machine"]:
        """Admin: flatten all machines across customers."""
        try:
            db = get_database()
            cursor = db.customers.find(
                {"machines": {"$exists": True, "$ne": []}}, {"machines": 1}, max_time_ms=10000
            )
            out: List[Machine] = []
            for doc in cursor:
                for m in doc.get("machines", []):
                    out.append(Machine.from_dict(m))
            return out
        except Exception as e:
            print(f"Error get_all_machines: {e}")
            return []
