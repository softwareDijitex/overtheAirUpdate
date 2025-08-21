#!/usr/bin/env python3
"""
Unit tests for the /register endpoint
Tests various scenarios including successful registration, validation errors, and duplicate email handling
"""

import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from app import create_app
from app.models.customer import Customer


class TestRegisterEndpoint:
    """Test class for the /register endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create a test Flask app instance"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client"""
        return app.test_client()
    
    @pytest.fixture
    def valid_customer_data(self):
        """Valid customer registration data"""
        return {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'address': '123 Main St, City, State 12345',
            'password': 'securepassword123'
        }
    
    @pytest.fixture
    def mock_uuid(self):
        """Mock UUID for consistent testing"""
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-9abc-123456789abc')
            yield mock_uuid
    
    @pytest.fixture
    def mock_bcrypt(self):
        """Mock bcrypt for password hashing"""
        with patch('app.bcrypt.generate_password_hash') as mock_hash:
            mock_hash.return_value = b'hashed_password'
            yield mock_hash
    
    @pytest.fixture
    def mock_generate_token(self):
        """Mock token generation"""
        with patch('app.utils.auth.generate_token') as mock_token:
            mock_token.return_value = 'mock_jwt_token_123'
            yield mock_token
    
    def test_successful_registration(self, client, valid_customer_data, mock_uuid, mock_bcrypt, mock_generate_token):
        """Test successful customer registration"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            with patch('app.models.customer.Customer.save') as mock_save:
                # Mock that no customer exists with this email
                mock_find.return_value = None
                
                # Mock successful save
                mock_save.return_value = 'mock_inserted_id'
                
                response = client.post('/api/customers/register',
                                     data=json.dumps(valid_customer_data),
                                     content_type='application/json')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                
                assert data['message'] == 'Customer registered successfully'
                assert data['customer_id'] == '12345678-1234-5678-9abc-123456789abc'
                assert data['token'] == 'mock_jwt_token_123'
                
                # Verify that find_by_email was called with correct email
                mock_find.assert_called_once_with(valid_customer_data['email'])
                
                # Verify that save was called
                mock_save.assert_called_once()
                
                # Verify that token was generated with correct parameters
                mock_generate_token.assert_called_once_with(
                    '12345678-1234-5678-9abc-123456789abc',
                    valid_customer_data['email']
                )
    
    def test_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
            # Missing phone, address, password
        }
        
        response = client.post('/api/customers/register',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'is required' in data['error']
    
    def test_empty_required_fields(self, client):
        """Test registration with empty required fields"""
        empty_data = {
            'name': '',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'address': '123 Main St',
            'password': 'password123'
        }
        
        response = client.post('/api/customers/register',
                             data=json.dumps(empty_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'name is required' in data['error']
    
    def test_duplicate_email_registration(self, client, valid_customer_data):
        """Test registration with existing email"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            # Mock that a customer already exists with this email
            mock_find.return_value = MagicMock()
            
            response = client.post('/api/customers/register',
                                 data=json.dumps(valid_customer_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Email already registered'
            
            # Verify that find_by_email was called
            mock_find.assert_called_once_with(valid_customer_data['email'])
    
    def test_invalid_json_data(self, client):
        """Test registration with invalid JSON data"""
        response = client.post('/api/customers/register',
                             data='invalid json data',
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_database_error_during_save(self, client, valid_customer_data, mock_uuid, mock_bcrypt):
        """Test registration when database save fails"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            with patch('app.models.customer.Customer.save') as mock_save:
                # Mock that no customer exists with this email
                mock_find.return_value = None
                
                # Mock database error during save
                mock_save.side_effect = Exception("Database connection error")
                
                response = client.post('/api/customers/register',
                                     data=json.dumps(valid_customer_data),
                                     content_type='application/json')
                
                assert response.status_code == 500
                data = json.loads(response.data)
                assert 'error' in data
                assert 'Database connection error' in data['error']
    
    def test_database_error_during_email_check(self, client, valid_customer_data):
        """Test registration when database error occurs during email check"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            # Mock database error during email check
            mock_find.side_effect = Exception("Database connection error")
            
            response = client.post('/api/customers/register',
                                 data=json.dumps(valid_customer_data),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Database connection error' in data['error']
    
    def test_token_generation_error(self, client, valid_customer_data, mock_uuid, mock_bcrypt):
        """Test registration when token generation fails"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            with patch('app.models.customer.Customer.save') as mock_save:
                with patch('app.utils.auth.generate_token') as mock_generate_token:
                    # Mock that no customer exists with this email
                    mock_find.return_value = None
                    
                    # Mock successful save
                    mock_save.return_value = 'mock_inserted_id'
                    
                    # Mock token generation error
                    mock_generate_token.side_effect = Exception("Token generation failed")
                    
                    response = client.post('/api/customers/register',
                                         data=json.dumps(valid_customer_data),
                                         content_type='application/json')
                    
                    assert response.status_code == 500
                    data = json.loads(response.data)
                    assert 'error' in data
                    assert 'Token generation failed' in data['error']
    
    def test_password_hashing(self, client, valid_customer_data, mock_uuid, mock_generate_token):
        """Test that password is properly hashed during registration"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            with patch('app.models.customer.Customer.save') as mock_save:
                # Mock that no customer exists with this email
                mock_find.return_value = None
                
                # Mock successful save
                mock_save.return_value = 'mock_inserted_id'
                
                response = client.post('/api/customers/register',
                                     data=json.dumps(valid_customer_data),
                                     content_type='application/json')
                
                assert response.status_code == 201
                
                # Verify that password was hashed
                from app.bcrypt import generate_password_hash
                generate_password_hash.assert_called_once_with(valid_customer_data['password'])
    
    def test_customer_id_generation(self, client, valid_customer_data, mock_bcrypt, mock_generate_token):
        """Test that a new UUID is generated for customer_id"""
        with patch('app.models.customer.Customer.find_by_email') as mock_find:
            with patch('app.models.customer.Customer.save') as mock_save:
                # Mock that no customer exists with this email
                mock_find.return_value = None
                
                # Mock successful save
                mock_save.return_value = 'mock_inserted_id'
                
                response = client.post('/api/customers/register',
                                     data=json.dumps(valid_customer_data),
                                     content_type='application/json')
                
                assert response.status_code == 201
                data = json.loads(response.data)
                
                # Verify that customer_id is a valid UUID
                import uuid
                try:
                    uuid.UUID(data['customer_id'])
                except ValueError:
                    pytest.fail("customer_id is not a valid UUID")


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 