from datetime import datetime
from bson import ObjectId
from app import get_database, hash_password, check_password
import uuid
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
import bcrypt

class Customer:
    def __init__(self, name, email, phone, address, password=None, customer_id=None, created_at=None, updated_at=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        self.customer_id = customer_id or self.generate_customer_id()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def generate_customer_id(self):
        """Generate a unique customer ID"""
        return str(uuid.uuid4())

    def hash_password(self):
        """Hash the password using bcrypt"""
        if self.password:
            self.password = hash_password(self.password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at if isinstance(self.updated_at, datetime) else None,
        }

    def save(self):
        """Save customer to database with proper error handling"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = self.to_dict()
            if self.password:
                customer_data['password'] = self.password
            
            # Add timeout to prevent hanging
            result = db.customers.insert_one(customer_data)
            print(f"Customer saved with ID: {result.inserted_id}")
            return result.inserted_id
            
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB timeout error: {e}")
            raise Exception("Database connection timeout")
        except PyMongoError as e:
            print(f"MongoDB error: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Error saving customer: {e}")
            raise

    @staticmethod
    def find_by_customer_id(customer_id):
        """Find customer by customer_id with proper error handling"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = db.customers.find_one(
                {'customer_id': customer_id},
                max_time_ms=5000  # 5 second timeout
            )
            
            if customer_data:
                return Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data['phone'],
                    address=customer_data['address'],
                    password=customer_data.get('password'),
                    customer_id=customer_data['customer_id'],
                    created_at=customer_data.get('created_at'),
                    updated_at=customer_data.get('updated_at')
                )
            return None
            
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB timeout error: {e}")
            raise Exception("Database connection timeout")
        except PyMongoError as e:
            print(f"MongoDB error: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Error finding customer by ID: {e}")
            raise

    @staticmethod
    def find_by_email(email):
        """Find customer by email with proper error handling"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = db.customers.find_one(
                {'email': email},
                max_time_ms=5000  # 5 second timeout
            )
            
            if customer_data:
                return Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data['phone'],
                    address=customer_data['address'],
                    password=customer_data.get('password'),
                    customer_id=customer_data['customer_id'],
                    created_at=customer_data.get('created_at'),
                    updated_at=customer_data.get('updated_at')
                )
            return None
            
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB timeout error: {e}")
            raise Exception("Database connection timeout")
        except PyMongoError as e:
            print(f"MongoDB error: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Error finding customer by email: {e}")
            raise

    @staticmethod
    def get_all_customers():
        """Get all customers with proper error handling"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            cursor = db.customers.find(
                {}, 
                {'password': 0},
                max_time_ms=10000  # 10 second timeout
            )
            
            customers = []
            for c in cursor:
                customers.append(Customer(
                    name=c['name'],
                    email=c['email'],
                    phone=c['phone'],
                    address=c['address'],
                    customer_id=c['customer_id'],
                    created_at=c.get('created_at'),
                    updated_at=c.get('updated_at')
                ))
            
            return customers
            
        except ServerSelectionTimeoutError as e:
            print(f"MongoDB timeout error: {e}")
            raise Exception("Database connection timeout")
        except PyMongoError as e:
            print(f"MongoDB error: {e}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Error getting all customers: {e}")
            raise