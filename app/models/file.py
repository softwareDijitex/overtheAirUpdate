from datetime import datetime
from bson.objectid import ObjectId
from app import get_database
import os
from azure.storage.blob import BlobServiceClient
from app.config import Config
from azure.core.exceptions import ResourceExistsError


class File:
    def __init__(self, customer_id, machine_id, filename, file_data, version=None, file_id=None):
        self.customer_id = customer_id
        self.machine_id = machine_id
        self.filename = filename
        self.file_data = file_data
        self.version = version or self.get_next_version(customer_id, machine_id)
        self.file_id = file_id or str(ObjectId())
        self.uploaded_at = datetime.utcnow()
        self.file_size = len(file_data) if file_data else 0

    def get_next_version(self, customer_id, machine_id):
        """Get the next version number for a machine's file"""
        try:
            db = get_database()
            if db is None:
                return "1"
            # Get customer document and check existing files for this machine
            customer = db.customers.find_one({'customer_id': customer_id})
            if customer and 'machines' in customer:
                machine = next(
                    (m for m in customer['machines'] if m['id'] == machine_id), 
                    None
                )
                if machine and 'files' in machine:
                    existing_files = [f for f in machine['files'] if f['filename'] == self.filename]
                    if existing_files:
                        # Try to find the highest numeric version
                        numeric_versions = []
                        for f in existing_files:
                            try:
                                # Try to convert to float for comparison
                                numeric_versions.append(float(f['version']))
                            except (ValueError, TypeError):
                                # If not numeric, skip for auto-increment
                                continue
                        
                        if numeric_versions:
                            return str(max(numeric_versions) + 1)
                        else:
                            # If no numeric versions found, start with 1
                            return "1"
            return "1"
        except Exception:
            return "1"

    def to_dict(self):
        """Convert file object to dictionary"""
        return {
            'file_id': self.file_id,
            'filename': self.filename,
            'version': self.version,
            'uploaded_at': self.uploaded_at,
            'file_size': self.file_size
        }

    # def save(self):
    #     """Save file to Azure Blob Storage and metadata to machine document"""
    #     try:
    #         db = get_database()
    #         if db is None:
    #             raise Exception("MongoDB connection not available")
                
    #         # Check if file with same name AND version already exists for this machine
    #         customer = db.customers.find_one({'customer_id': self.customer_id})
    #         if customer and 'machines' in customer:
    #             machine = next(
    #                 (m for m in customer['machines'] if m['id'] == self.machine_id), 
    #                 None
    #             )
    #             if machine and 'files' in machine:
    #                 existing_file = next(
    #                     (f for f in machine['files'] 
    #                      if f['filename'] == self.filename and f['version'] == self.version), 
    #                     None
    #                 )
                    
    #                 if existing_file:
    #                     # If exact same filename and version exists, ask user to choose different version
    #                     raise Exception(f"File '{self.filename}' with version '{self.version}' already exists for this machine. Please choose a different version.")
                
    #         # For small files (<= 1MB), store directly in machine document
    #         if self.file_size <= 7 * 1024 * 1024:  # 1MB limit
    #             file_data = self.to_dict()
    #             file_data['content'] = self.file_data
    #             file_data['storage_type'] = 'mongodb'
                
    #             # Add file to machine's files array
    #             result = db.customers.update_one(
    #                 {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                 {'$push': {'machines.$.files': file_data}}
    #             )
                
    #             if result.modified_count == 0:
    #                 raise Exception("Customer or machine not found")
                    
    #             return self.file_id
    #         else:
    #             # For larger files, try Azure Blob Storage
    #             try:
    #                 if not Config.AZURE_STORAGE_CONNECTION_STRING or not Config.AZURE_STORAGE_CONTAINER_NAME:
    #                     raise Exception("Azure Storage configuration not available")
                        
    #                 blob_service_client = BlobServiceClient.from_connection_string(
    #                     Config.AZURE_STORAGE_CONNECTION_STRING
    #                 )
    #                 container_client = blob_service_client.get_container_client(
    #                     Config.AZURE_STORAGE_CONTAINER_NAME
    #                 )
                    
    #                 # Create blob name with customer_id, machine_id and version
    #                 blob_name = f"{self.customer_id}/{self.machine_id}/{self.filename}_v{self.version}"
    #                 blob_client = container_client.get_blob_client(blob_name)
                    
    #                 # Upload file data (overwrite if exists)
    #                 blob_client.upload_blob(self.file_data, overwrite=True)
                    
    #                 # Save metadata to machine document
    #                 file_data = self.to_dict()
    #                 file_data['blob_name'] = blob_name
    #                 file_data['storage_type'] = 'azure'
                    
    #                 result = db.customers.update_one(
    #                     {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                     {'$push': {'machines.$.files': file_data}}
    #                 )
                    
    #                 if result.modified_count == 0:
    #                     raise Exception("Customer or machine not found")
                        
    #                 return self.file_id
                    
    #             except Exception as azure_error:
    #                 # If Azure fails, fall back to MongoDB storage
    #                 print(f"Azure Blob Storage failed, falling back to MongoDB: {azure_error}")
    #                 file_data = self.to_dict()
    #                 file_data['content'] = self.file_data
    #                 file_data['storage_type'] = 'mongodb'
                    
    #                 result = db.customers.update_one(
    #                     {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                     {'$push': {'machines.$.files': file_data}}
    #                 )
                    
    #                 if result.modified_count == 0:
    #                     raise Exception("Customer or machine not found")
                        
    #                 return self.file_id
            
    #     except Exception as e:
    #         raise Exception(f"Failed to save file: {str(e)}")
    # def save(self):
    #     """Save file to Azure Blob Storage and metadata to machine document"""
    #     try:
    #         db = get_database()
    #         if db is None:
    #             raise Exception("MongoDB connection not available")

    #         # ⬇️ Enforce global cap again (defense in depth)
    #         if self.file_size > Config.MAX_UPLOAD_BYTES:
    #             raise Exception(f"File too large. Max {Config.MAX_UPLOAD_MB}MB")

    #         # Duplicate (filename + version) check unchanged...
    #         # ...

    #         # Store small files inline in MongoDB; larger go to Azure Blob
    #         if self.file_size <= Config.INLINE_TO_MONGO_BYTES:
    #             # (<= 2MB) inline in MongoDB
    #             file_data = self.to_dict()
    #             file_data['content'] = self.file_data
    #             file_data['storage_type'] = 'mongodb'

    #             result = db.customers.update_one(
    #                 {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                 {'$push': {'machines.$.files': file_data}}
    #             )
    #             if result.modified_count == 0:
    #                 raise Exception("Customer or machine not found")
    #             return self.file_id
    #         else:
    #             # (> 2MB up to 7MB) to Azure Blob
    #             try:
    #                 if not Config.AZURE_STORAGE_CONNECTION_STRING or not Config.AZURE_STORAGE_CONTAINER_NAME:
    #                     raise Exception("Azure Storage configuration not available")

    #                 blob_service_client = BlobServiceClient.from_connection_string(
    #                     Config.AZURE_STORAGE_CONNECTION_STRING
    #                 )
    #                 container_client = blob_service_client.get_container_client(
    #                     Config.AZURE_STORAGE_CONTAINER_NAME
    #                 )

    #                 blob_name = f"{self.customer_id}/{self.machine_id}/{self.filename}_v{self.version}"
    #                 blob_client = container_client.get_blob_client(blob_name)
    #                 blob_client.upload_blob(self.file_data, overwrite=True)

    #                 file_data = self.to_dict()
    #                 file_data['blob_name'] = blob_name
    #                 file_data['storage_type'] = 'azure'

    #                 result = db.customers.update_one(
    #                     {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                     {'$push': {'machines.$.files': file_data}}
    #                 )
    #                 if result.modified_count == 0:
    #                     raise Exception("Customer or machine not found")
    #                 return self.file_id
    #             except Exception as azure_error:
    #                 # Optional: keep your fallback or remove it if you never want big files in Mongo
    #                 print(f"Azure Blob Storage failed, falling back to MongoDB: {azure_error}")
    #                 file_data = self.to_dict()
    #                 file_data['content'] = self.file_data
    #                 file_data['storage_type'] = 'mongodb'
    #                 result = db.customers.update_one(
    #                     {'customer_id': self.customer_id, 'machines.id': self.machine_id},
    #                     {'$push': {'machines.$.files': file_data}}
    #                 )
    #                 if result.modified_count == 0:
    #                     raise Exception("Customer or machine not found")
    #                 return self.file_id
    #     except Exception as e:
    #         raise Exception(f"Failed to save file: {str(e)}")

    def save(self):
        """Save file to Azure Blob Storage and metadata to machine document"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")

            # Defense-in-depth hard cap
            if self.file_size > Config.MAX_UPLOAD_BYTES:
                raise Exception(f"File too large. Max {Config.MAX_UPLOAD_MB}MB")

            # --- Duplicate (filename + version) guard ---
            customer = db.customers.find_one({'customer_id': self.customer_id})
            if customer and 'machines' in customer:
                machine = next((m for m in customer['machines'] if m['id'] == self.machine_id), None)
                if machine and 'files' in machine:
                    existing_file = next(
                        (f for f in machine['files']
                        if f['filename'] == self.filename and f['version'] == self.version),
                        None
                    )
                    if existing_file:
                        raise Exception(
                            f"File '{self.filename}' with version '{self.version}' already exists "
                            f"for this machine. Please choose a different version."
                        )

            # --- Small files (<= INLINE_TO_MONGO_BYTES) → inline in MongoDB ---
            # if self.file_size <= Config.INLINE_TO_MONGO_BYTES:
            #     file_data = self.to_dict()
            #     file_data['content'] = self.file_data
            #     file_data['storage_type'] = 'mongodb'

            #     result = db.customers.update_one(
            #         {'customer_id': self.customer_id, 'machines.id': self.machine_id},
            #         {'$push': {'machines.$.files': file_data}}
            #     )
            #     if result.modified_count == 0:
            #         raise Exception("Customer or machine not found")
            #     return self.file_id

            # --- Large files (> INLINE_TO_MONGO_BYTES) → MUST go to Azure Blob ---
            if not (Config.AZURE_STORAGE_CONNECTION_STRING and Config.AZURE_STORAGE_CONTAINER_NAME):
                raise Exception("Large files require Azure Blob Storage. Azure configuration missing.")

            try:
                blob_service_client = BlobServiceClient.from_connection_string(
                    Config.AZURE_STORAGE_CONNECTION_STRING
                )
                container_client = blob_service_client.get_container_client(
                    Config.AZURE_STORAGE_CONTAINER_NAME
                )
                # Ensure container exists
                try:
                    container_client.create_container()
                except ResourceExistsError:
                    pass

                # Blob name: customer/machine/filename_v{version}
                blob_name = f"{self.customer_id}/{self.machine_id}/{self.filename}_v{self.version}"
                blob_client = container_client.get_blob_client(blob_name)

                # Upload (overwrite if exists)
                blob_client.upload_blob(self.file_data, overwrite=True, timeout=60)

                # Save metadata (no content) to Mongo
                file_data = self.to_dict()
                file_data['blob_name'] = blob_name
                file_data['storage_type'] = 'azure'

                result = db.customers.update_one(
                    {'customer_id': self.customer_id, 'machines.id': self.machine_id},
                    {'$push': {'machines.$.files': file_data}}
                )
                if result.modified_count == 0:
                    raise Exception("Customer or machine not found")
                print(f"File saved to Azure Blob Storage: {self.file_id}")
                return self.file_id

            except Exception as azure_error:
                # No fallback for big files: surface the real reason
                raise Exception(f"Azure upload failed: {azure_error}")

        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")

    @staticmethod
    def get_file(customer_id, machine_id, filename, version):
        """Get file from Azure Blob Storage or machine document"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            # Get customer document
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return None
            
            # Find the specific machine
            machine = next(
                (m for m in customer['machines'] if m['id'] == machine_id), 
                None
            )
            if not machine or 'files' not in machine:
                return None
            
            # Find the specific file
            file_data = None
            for f in machine['files']:
                if f['filename'] == filename and f['version'] == version:
                    file_data = f
                    break
            
            if not file_data:
                return None
            
            # Check storage type
            storage_type = file_data.get('storage_type', 'mongodb')
            
            if storage_type == 'mongodb' or 'content' in file_data:
                # File stored in machine document
                return {
                    'filename': file_data['filename'],
                    'version': file_data['version'],
                    'uploaded_at': file_data['uploaded_at'],
                    'file_size': file_data['file_size'],
                    'content': file_data['content']
                }
            else:
                # File stored in Azure Blob Storage
                try:
                    if not Config.AZURE_STORAGE_CONNECTION_STRING or not Config.AZURE_STORAGE_CONTAINER_NAME:
                        raise Exception("Azure Storage configuration not available")
                        
                    blob_service_client = BlobServiceClient.from_connection_string(
                        Config.AZURE_STORAGE_CONNECTION_STRING
                    )
                    container_client = blob_service_client.get_container_client(
                        Config.AZURE_STORAGE_CONTAINER_NAME
                    )
                    
                    blob_client = container_client.get_blob_client(file_data['blob_name'])
                    file_content = blob_client.download_blob().readall()
                    
                    return {
                        'filename': file_data['filename'],
                        'version': file_data['version'],
                        'uploaded_at': file_data['uploaded_at'],
                        'file_size': file_data['file_size'],
                        'content': file_content
                    }
                    
                except Exception as azure_error:
                    raise Exception(f"Failed to retrieve file from Azure: {azure_error}")
            
        except Exception as e:
            raise Exception(f"Failed to get file: {str(e)}")

    @staticmethod
    def get_all_versions(customer_id, machine_id, filename):
        """Get all versions of a file for a specific machine"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return []
            
            machine = next(
                (m for m in customer['machines'] if m['id'] == machine_id), 
                None
            )
            if not machine or 'files' not in machine:
                return []
            
            # Get all files with the same filename
            versions = []
            for f in machine['files']:
                if f['filename'] == filename:
                    versions.append({
                        'filename': f['filename'],
                        'version': f['version'],
                        'uploaded_at': f['uploaded_at'],
                        'file_size': f['file_size']
                    })
            
            # Sort by version (try numeric sorting first)
            try:
                versions.sort(key=lambda x: float(x['version']))
            except (ValueError, TypeError):
                # If versions are not numeric, sort alphabetically
                versions.sort(key=lambda x: x['version'])
            
            return versions
            
        except Exception as e:
            raise Exception(f"Failed to get file versions: {str(e)}")

    @staticmethod
    def get_machine_files(customer_id, machine_id):
        """Get all files for a specific machine"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return []
            
            machine = next(
                (m for m in customer['machines'] if m['id'] == machine_id), 
                None
            )
            if not machine or 'files' not in machine:
                return []
            
            # Group files by filename and get the latest version of each
            files_dict = {}
            for f in machine['files']:
                filename = f['filename']
                if filename not in files_dict:
                    files_dict[filename] = []
                files_dict[filename].append(f)
            
            # Get the latest version of each file
            latest_files = []
            for filename, versions in files_dict.items():
                # Sort by version (try numeric sorting first)
                try:
                    latest_version = max(versions, key=lambda x: float(x['version']))
                except (ValueError, TypeError):
                    # If versions are not numeric, sort alphabetically
                    latest_version = max(versions, key=lambda x: x['version'])
                
                latest_files.append({
                    'filename': latest_version['filename'],
                    'version': latest_version['version'],
                    'uploaded_at': latest_version['uploaded_at'],
                    'file_size': latest_version['file_size'],
                    'total_versions': len(versions)
                })
            
            # Sort by filename
            latest_files.sort(key=lambda x: x['filename'])
            return latest_files
            
        except Exception as e:
            raise Exception(f"Failed to get machine files: {str(e)}")

    @staticmethod
    def get_customer_files(customer_id):
        """Get all files for a customer across all machines"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return []
            
            all_files = []
            for machine in customer['machines']:
                if 'files' in machine:
                    for f in machine['files']:
                        all_files.append({
                            'machine_id': machine['id'],
                            'machine_name': machine['name'],
                            'filename': f['filename'],
                            'version': f['version'],
                            'uploaded_at': f['uploaded_at'],
                            'file_size': f['file_size']
                        })
            
            return all_files
            
        except Exception as e:
            raise Exception(f"Failed to get customer files: {str(e)}")

    @staticmethod
    def delete_file(customer_id, machine_id, filename, version):
        """Delete a file from a machine"""
        try:
            db = get_database()
            if db is None:
                raise Exception("MongoDB connection not available")
                
            # Get the file data first to check storage type
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                raise Exception("Customer or machine not found")
            
            machine = next(
                (m for m in customer['machines'] if m['id'] == machine_id), 
                None
            )
            if not machine or 'files' not in machine:
                raise Exception("Machine not found or has no files")
            
            file_data = next(
                (f for f in machine['files'] 
                 if f['filename'] == filename and f['version'] == version), 
                None
            )
            
            if not file_data:
                raise Exception("File not found")
            
            # If file is stored in Azure, delete from blob storage
            if file_data.get('storage_type') == 'azure' and 'blob_name' in file_data:
                try:
                    if Config.AZURE_STORAGE_CONNECTION_STRING and Config.AZURE_STORAGE_CONTAINER_NAME:
                        blob_service_client = BlobServiceClient.from_connection_string(
                            Config.AZURE_STORAGE_CONNECTION_STRING
                        )
                        container_client = blob_service_client.get_container_client(
                            Config.AZURE_STORAGE_CONTAINER_NAME
                        )
                        blob_client = container_client.get_blob_client(file_data['blob_name'])
                        blob_client.delete_blob()
                except Exception as azure_error:
                    print(f"Warning: Failed to delete from Azure Blob Storage: {azure_error}")
            
            # Remove file from machine's files array
            result = db.customers.update_one(
                {'customer_id': customer_id, 'machines.id': machine_id},
                {'$pull': {'machines.$.files': {'filename': filename, 'version': version}}}
            )
            
            if result.modified_count == 0:
                raise Exception("File not found")
                
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete file: {str(e)}") 