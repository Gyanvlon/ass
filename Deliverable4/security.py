#!/usr/bin/env python3
"""
Security Module for Advanced Shell Simulation
Implements user authentication and file permissions

This module simulates operating system security features:
- User authentication system with login
- Multiple user roles (admin, standard user)
- File permission handling (rwx for owner, group, others)
- Access control based on permissions
"""

import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class UserRole(Enum):
    """Enum for user roles"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class FilePermissions:
    """Represents file permissions (Unix-like)"""
    owner_read: bool = True
    owner_write: bool = True
    owner_execute: bool = False
    
    group_read: bool = False
    group_write: bool = False
    group_execute: bool = False
    
    other_read: bool = False
    other_write: bool = False
    other_execute: bool = False
    
    def to_octal(self) -> int:
        """Convert permissions to octal notation (e.g., 755)"""
        owner = (self.owner_read * 4) + (self.owner_write * 2) + (self.owner_execute * 1)
        group = (self.group_read * 4) + (self.group_write * 2) + (self.group_execute * 1)
        other = (self.other_read * 4) + (self.other_write * 2) + (self.other_execute * 1)
        return int(f"{owner}{group}{other}")
    
    def __str__(self) -> str:
        """String representation (Unix-style: rwxrwxrwx)"""
        s = ""
        s += "r" if self.owner_read else "-"
        s += "w" if self.owner_write else "-"
        s += "x" if self.owner_execute else "-"
        s += "r" if self.group_read else "-"
        s += "w" if self.group_write else "-"
        s += "x" if self.group_execute else "-"
        s += "r" if self.other_read else "-"
        s += "w" if self.other_write else "-"
        s += "x" if self.other_execute else "-"
        return s
    
    @staticmethod
    def from_octal(octal: int) -> 'FilePermissions':
        """Create permissions from octal notation"""
        octal_str = str(octal).zfill(3)
        
        owner = int(octal_str[0])
        group = int(octal_str[1])
        other = int(octal_str[2])
        
        perms = FilePermissions()
        
        # Owner permissions
        perms.owner_read = bool(owner & 4)
        perms.owner_write = bool(owner & 2)
        perms.owner_execute = bool(owner & 1)
        
        # Group permissions
        perms.group_read = bool(group & 4)
        perms.group_write = bool(group & 2)
        perms.group_execute = bool(group & 1)
        
        # Other permissions
        perms.other_read = bool(other & 4)
        perms.other_write = bool(other & 2)
        perms.other_execute = bool(other & 1)
        
        return perms


@dataclass
class User:
    """Represents a user account"""
    username: str
    password_hash: str  # SHA256 hash of password
    role: UserRole
    created_at: str
    last_login: Optional[str] = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return self.password_hash == User.hash_password(password)


@dataclass
class FileInfo:
    """Metadata for a file in the system"""
    path: str
    owner: str  # username of file owner
    group: str  # group name
    permissions: FilePermissions
    created_at: str
    modified_at: str
    size: int


class UserAuthenticationSystem:
    """Manages user authentication and session"""
    
    def __init__(self):
        """Initialize with default users"""
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.file_metadata: Dict[str, FileInfo] = {}
        self.groups: Dict[str, List[str]] = {}  # group name -> list of usernames
        
        # Initialize default users
        self._init_default_users()
    
    def _init_default_users(self) -> None:
        """Initialize default user accounts"""
        now = datetime.now().isoformat()
        
        # Admin user
        admin = User(
            username="admin",
            password_hash=User.hash_password("admin123"),
            role=UserRole.ADMIN,
            created_at=now
        )
        self.users["admin"] = admin
        
        # Standard user
        user1 = User(
            username="alice",
            password_hash=User.hash_password("alice123"),
            role=UserRole.USER,
            created_at=now
        )
        self.users["alice"] = user1
        
        # Another standard user
        user2 = User(
            username="bob",
            password_hash=User.hash_password("bob123"),
            role=UserRole.USER,
            created_at=now
        )
        self.users["bob"] = user2
        
        # Guest user (read-only)
        guest = User(
            username="guest",
            password_hash=User.hash_password("guest"),
            role=UserRole.GUEST,
            created_at=now
        )
        self.users["guest"] = guest
        
        # Initialize default groups
        self.groups["admin"] = ["admin"]
        self.groups["users"] = ["alice", "bob"]
        self.groups["wheel"] = ["admin"]
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user login
        Returns: (success: bool, message: str)
        """
        if username not in self.users:
            return False, f"User '{username}' not found"
        
        user = self.users[username]
        if not user.verify_password(password):
            return False, "Invalid password"
        
        self.current_user = user
        self.current_user.last_login = datetime.now().isoformat()
        return True, f"Login successful. Welcome, {username}!"
    
    def logout(self) -> None:
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Get currently logged-in user"""
        return self.current_user
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        if not self.current_user:
            return False
        return self.current_user.role == UserRole.ADMIN
    
    def is_authenticated(self) -> bool:
        """Check if a user is authenticated"""
        return self.current_user is not None
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            "username": user.username,
            "role": user.role.value,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
    
    def list_users(self) -> List[Dict]:
        """List all users (admin only)"""
        if not self.is_admin():
            return []
        
        return [
            {
                "username": user.username,
                "role": user.role.value,
                "last_login": user.last_login or "Never",
            }
            for user in self.users.values()
        ]
    
    def create_user(self, username: str, password: str, role: str) -> Tuple[bool, str]:
        """Create new user (admin only)"""
        if not self.is_admin():
            return False, "Permission denied: only admins can create users"
        
        if username in self.users:
            return False, f"User '{username}' already exists"
        
        try:
            user_role = UserRole[role.upper()]
        except KeyError:
            return False, f"Invalid role. Must be one of: {[r.value for r in UserRole]}"
        
        now = datetime.now().isoformat()
        user = User(
            username=username,
            password_hash=User.hash_password(password),
            role=user_role,
            created_at=now
        )
        self.users[username] = user
        
        if user_role != UserRole.ADMIN:
            if "users" not in self.groups:
                self.groups["users"] = []
            self.groups["users"].append(username)
        
        return True, f"User '{username}' created successfully with role '{role}'"
    
    # File Permission Management
    
    def register_file(self, path: str, owner: str, group: str = "users",
                      permissions: Optional[FilePermissions] = None) -> bool:
        """Register a file in the system with permissions"""
        if permissions is None:
            permissions = FilePermissions(owner_read=True, owner_write=True)
        
        now = datetime.now().isoformat()
        
        try:
            size = os.path.getsize(path) if os.path.exists(path) else 0
        except:
            size = 0
        
        file_info = FileInfo(
            path=path,
            owner=owner,
            group=group,
            permissions=permissions,
            created_at=now,
            modified_at=now,
            size=size
        )
        
        self.file_metadata[path] = file_info
        return True
    
    def can_read(self, path: str, user: str) -> bool:
        """Check if user can read a file"""
        if path not in self.file_metadata:
            # File not registered, allow access (backward compatibility)
            return True
        
        file_info = self.file_metadata[path]
        perms = file_info.permissions
        
        # Admin can always read
        if self._is_admin_user(user):
            return True
        
        # Owner
        if file_info.owner == user:
            return perms.owner_read
        
        # Group
        if self._is_user_in_group(user, file_info.group):
            return perms.group_read
        
        # Others
        return perms.other_read
    
    def can_write(self, path: str, user: str) -> bool:
        """Check if user can write to a file"""
        if path not in self.file_metadata:
            return True  # Backward compatibility
        
        file_info = self.file_metadata[path]
        perms = file_info.permissions
        
        # Admin can always write
        if self._is_admin_user(user):
            return True
        
        # Owner
        if file_info.owner == user:
            return perms.owner_write
        
        # Group
        if self._is_user_in_group(user, file_info.group):
            return perms.group_write
        
        # Others
        return perms.other_write
    
    def can_execute(self, path: str, user: str) -> bool:
        """Check if user can execute a file"""
        if path not in self.file_metadata:
            return True  # Backward compatibility
        
        file_info = self.file_metadata[path]
        perms = file_info.permissions
        
        # Admin can always execute
        if self._is_admin_user(user):
            return True
        
        # Owner
        if file_info.owner == user:
            return perms.owner_execute
        
        # Group
        if self._is_user_in_group(user, file_info.group):
            return perms.group_execute
        
        # Others
        return perms.other_execute
    
    def change_permissions(self, path: str, octal: int, user: str) -> Tuple[bool, str]:
        """Change file permissions (owner or admin only)"""
        if path not in self.file_metadata:
            return False, f"File '{path}' not registered"
        
        file_info = self.file_metadata[path]
        
        # Only owner or admin can change permissions
        if file_info.owner != user and not self._is_admin_user(user):
            return False, "Permission denied: only owner or admin can change permissions"
        
        try:
            new_perms = FilePermissions.from_octal(octal)
            file_info.permissions = new_perms
            file_info.modified_at = datetime.now().isoformat()
            return True, f"Permissions changed to {octal}"
        except Exception as e:
            return False, f"Invalid permissions: {e}"
    
    def get_file_permissions(self, path: str) -> Optional[Dict]:
        """Get file permission information"""
        if path not in self.file_metadata:
            return None
        
        file_info = self.file_metadata[path]
        return {
            "path": file_info.path,
            "owner": file_info.owner,
            "group": file_info.group,
            "permissions": str(file_info.permissions),
            "octal": file_info.permissions.to_octal(),
            "created_at": file_info.created_at,
            "modified_at": file_info.modified_at,
            "size": file_info.size,
        }
    
    def _is_admin_user(self, username: str) -> bool:
        """Check if user is admin"""
        if username not in self.users:
            return False
        return self.users[username].role == UserRole.ADMIN
    
    def _is_user_in_group(self, username: str, group: str) -> bool:
        """Check if user is in a group"""
        if group not in self.groups:
            return False
        return username in self.groups[group]
    
    def get_default_credentials(self) -> Dict[str, str]:
        """Get default test credentials"""
        return {
            "admin": "admin123",
            "alice": "alice123",
            "bob": "bob123",
            "guest": "guest",
        }
