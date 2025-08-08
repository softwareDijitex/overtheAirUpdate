from datetime import datetime
from bson import ObjectId
from app import get_database, hash_password, check_password

class Customer:
    def __init__(self, name, email, phone, address, password=None, customer_id=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = password
        self.customer_id = customer_id or self.generate_customer_id()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def generate_customer_id(self):
        """Generate a unique customer ID"""
        import uuid
        return str(uuid.uuid4())

    def hash_password(self):
        """Hash the password using bcrypt"""
        if self.password:
            self.password = hash_password(self.password)

    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        return check_password(password, self.password)

    def to_dict(self):
        """Convert customer object to dictionary"""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        """Save customer to database"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = self.to_dict()
            if self.password:
                customer_data['password'] = self.password
            
            result = db.customers.insert_one(customer_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error saving customer: {e}")
            raise

    @staticmethod
    def find_by_customer_id(customer_id):
        """Find customer by customer_id"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = db.customers.find_one({'customer_id': customer_id})
            if customer_data:
                return Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data['phone'],
                    address=customer_data['address'],
                    customer_id=customer_data['customer_id']
                )
            return None
        except Exception as e:
            print(f"Error finding customer by ID: {e}")
            raise

    @staticmethod
    def find_by_email(email):
        """Find customer by email"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer_data = db.customers.find_one({'email': email})
            if customer_data:
                return Customer(
                    name=customer_data['name'],
                    email=customer_data['email'],
                    phone=customer_data['phone'],
                    address=customer_data['address'],
                    password=customer_data.get('password'),
                    customer_id=customer_data['customer_id']
                )
            return None
        except Exception as e:
            print(f"Error finding customer by email: {e}")
            raise

    @staticmethod
    def get_all_customers():
        """Get all customers"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customers = db.customers.find({}, {'password': 0})
            return [Customer(
                name=c['name'],
                email=c['email'],
                phone=c['phone'],
                address=c['address'],
                customer_id=c['customer_id']
            ) for c in customers]
        except Exception as e:
            print(f"Error getting all customers: {e}")
            raise 