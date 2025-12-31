"""
Authentication & Authorization System - Demo Implementation

Provides token-based authentication with:
- API key validation (demo scope)
- User identity propagation
- Permission enforcement at data access layer
- Clear security boundaries

DESIGN DECISIONS:
- API keys (not JWT) for simplicity
- Static user mapping (no database)
- Two permission levels: admin, user
- No UI authentication complexity
- Designed for demo scrutiny, not production SaaS

SECURITY MODEL:
- All requests require valid API key
- User ID derived from API key
- Permissions checked at ingestion/query time
- No cross-user data access
"""

import hashlib
import secrets
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class Permission(Enum):
    """Permission types in the system"""
    QUERY = "query"  # Can query knowledge base
    INGEST = "ingest"  # Can ingest new documents
    ADMIN = "admin"  # Can manage users and system settings


@dataclass
class User:
    """User identity with permissions"""
    user_id: str
    username: str
    api_key_hash: str  # SHA-256 hash of API key
    permissions: List[Permission]
    email: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        # Admin has all permissions
        if Permission.ADMIN in self.permissions:
            return True
        return permission in self.permissions


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks required permission"""
    pass


class AuthManager:
    """
    Authentication & Authorization Manager.
    
    DEMO SCOPE DESIGN:
    - Static user database (in-memory)
    - API key authentication (simple, secure for demo)
    - Two-tier permissions: admin vs user
    - No password reset, SSO, or RBAC complexity
    
    SECURITY PROPERTIES:
    - API keys hashed (SHA-256)
    - User isolation enforced
    - Permissions checked at access layer
    - No secrets in logs or errors
    
    PRODUCTION MIGRATION PATH:
    - Replace static users with database
    - Add JWT with refresh tokens
    - Implement RBAC with granular permissions
    - Add SSO integration (SAML/OAuth)
    """
    
    def __init__(self):
        """Initialize auth manager with demo users"""
        self.users: Dict[str, User] = {}
        self._api_key_to_user: Dict[str, str] = {}  # API key hash -> user_id
        
        # Initialize demo users
        self._initialize_demo_users()
    
    def _initialize_demo_users(self) -> None:
        """
        Create demo users for testing.
        
        DEMO USERS:
        - admin: Full access (ingest + query + admin)
        - user1: Query access only
        - user2: Query + ingest access
        """
        demo_users = [
            {
                'user_id': 'usr_admin',
                'username': 'admin',
                'api_key': 'demo_admin_key_12345',  # In real system: env var
                'permissions': [Permission.ADMIN, Permission.QUERY, Permission.INGEST],
                'email': 'admin@demo.com'
            },
            {
                'user_id': 'usr_alice',
                'username': 'alice',
                'api_key': 'demo_user1_key_67890',
                'permissions': [Permission.QUERY],
                'email': 'alice@demo.com'
            },
            {
                'user_id': 'usr_bob',
                'username': 'bob',
                'api_key': 'demo_user2_key_abcde',
                'permissions': [Permission.QUERY, Permission.INGEST],
                'email': 'bob@demo.com'
            }
        ]
        
        for user_data in demo_users:
            api_key = user_data.pop('api_key')
            api_key_hash = self._hash_api_key(api_key)
            
            user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                api_key_hash=api_key_hash,
                permissions=user_data['permissions'],
                email=user_data.get('email')
            )
            
            self.users[user.user_id] = user
            self._api_key_to_user[api_key_hash] = user.user_id
    
    @staticmethod
    def _hash_api_key(api_key: str) -> str:
        """Hash API key using SHA-256"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def authenticate(self, api_key: str) -> User:
        """
        Authenticate user by API key.
        
        Args:
            api_key: API key from request header
            
        Returns:
            User object if authentication succeeds
            
        Raises:
            AuthenticationError: If API key is invalid
        """
        if not api_key:
            raise AuthenticationError("API key required")
        
        api_key_hash = self._hash_api_key(api_key)
        user_id = self._api_key_to_user.get(api_key_hash)
        
        if not user_id:
            raise AuthenticationError("Invalid API key")
        
        user = self.users.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        return user
    
    def authorize(self, user: User, permission: Permission) -> None:
        """
        Check if user has required permission.
        
        Args:
            user: Authenticated user
            permission: Required permission
            
        Raises:
            AuthorizationError: If user lacks permission
        """
        if not user.has_permission(permission):
            raise AuthorizationError(
                f"User {user.username} lacks required permission: {permission.value}"
            )
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def list_users(self, requester: User) -> List[Dict]:
        """
        List all users (admin only).
        
        Args:
            requester: User making the request
            
        Returns:
            List of user info (no sensitive data)
            
        Raises:
            AuthorizationError: If requester is not admin
        """
        self.authorize(requester, Permission.ADMIN)
        
        return [
            {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'permissions': [p.value for p in user.permissions]
            }
            for user in self.users.values()
        ]
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure random API key.
        
        Returns:
            API key string (32 characters)
        """
        return secrets.token_urlsafe(32)


# Global auth manager instance
auth_manager = AuthManager()


def require_auth(api_key: str) -> User:
    """
    Decorator helper: Authenticate request.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Authenticated user
        
    Raises:
        AuthenticationError: If authentication fails
    """
    return auth_manager.authenticate(api_key)


def require_permission(user: User, permission: Permission) -> None:
    """
    Decorator helper: Check permission.
    
    Args:
        user: Authenticated user
        permission: Required permission
        
    Raises:
        AuthorizationError: If user lacks permission
    """
    auth_manager.authorize(user, permission)


# ============================================================================
# INTEGRATION GUIDE
# ============================================================================
"""
How to integrate auth into Flask routes:

from core.auth import require_auth, require_permission, Permission
from core.auth import AuthenticationError, AuthorizationError

@app.route('/api/query', methods=['POST'])
def query():
    try:
        # 1. Extract API key from header
        api_key = request.headers.get('X-API-Key')
        
        # 2. Authenticate user
        user = require_auth(api_key)
        
        # 3. Check permission
        require_permission(user, Permission.QUERY)
        
        # 4. Process request with user context
        result = process_query(user_id=user.user_id, ...)
        
        return jsonify(result), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403


@app.route('/api/ingest', methods=['POST'])
def ingest():
    try:
        api_key = request.headers.get('X-API-Key')
        user = require_auth(api_key)
        require_permission(user, Permission.INGEST)
        
        # User has permission to ingest
        result = ingest_documents(user_id=user.user_id, ...)
        
        return jsonify(result), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
"""

# ============================================================================
# PERMISSION MODEL DOCUMENTATION
# ============================================================================
"""
PERMISSION MODEL:

1. QUERY Permission:
   - Can query the knowledge base
   - Can create conversations
   - Can view own conversation history
   - CANNOT ingest documents
   - CANNOT access other users' conversations

2. INGEST Permission:
   - Can upload documents
   - Can ingest from Slack, Confluence
   - Can rebuild vector indexes
   - Inherits QUERY permissions
   - CANNOT access other users' data

3. ADMIN Permission:
   - Full system access
   - Can manage users
   - Can view system metrics
   - Can access all conversations (for debugging)
   - Inherits all permissions

SECURITY BOUNDARIES:

1. API Layer:
   - All routes require valid API key
   - User identity extracted from API key
   - Permissions checked before processing

2. Data Access Layer:
   - Conversation storage scoped by user_id
   - Vector store shared (documents are public within tenant)
   - Ingestion logs track user who ingested data

3. Demo Scope Limitations:
   - No multi-tenancy (single deployment per organization)
   - No document-level permissions (all documents accessible to all users)
   - No SSO or advanced auth flows
   - API keys in code (not secret manager)

DEMO USER CREDENTIALS:

Admin User:
- API Key: demo_admin_key_12345
- Permissions: Query, Ingest, Admin
- Use for: Testing all features

Query User (Alice):
- API Key: demo_user1_key_67890
- Permissions: Query only
- Use for: Testing permission denials on ingest

Ingest User (Bob):
- API Key: demo_user2_key_abcde
- Permissions: Query, Ingest
- Use for: Testing data ingestion flows
"""
