#!/usr/bin/env python3
"""
Demonstration Script for Deliverable 4: Integration and Security
Shows piping, security mechanisms, and integrated features
"""

import os
import sys
from pathlib import Path
from security import UserAuthenticationSystem, FilePermissions
from piping import CommandPipeline


def demo_piping():
    """Demonstrate command piping"""
    print("\n" + "="*70)
    print("DEMO 1: COMMAND PIPING")
    print("="*70)
    
    pipeline = CommandPipeline(".")
    
    # Create test data
    test_file = "demo_data.txt"
    with open(test_file, 'w') as f:
        f.write("apple\nbanana\napricot\ncherry\nblueberry\navocado\n")
    
    print("\nTest File Content:")
    with open(test_file, 'r') as f:
        print(f.read())
    
    # Demo piping
    print("\nPipe Example 1: cat + grep")
    print("Command: cat demo_data.txt | grep a")
    success, output = pipeline.execute("cat demo_data.txt | grep a")
    if success:
        print("Output:")
        print(output)
    
    print("\nPipe Example 2: echo + grep")
    print("Command: echo 'hello world' | grep world")
    success, output = pipeline.execute("echo 'hello world' | grep world")
    if success:
        print("Output:")
        print(output if output else "(no match)")
    
    # Cleanup
    os.remove(test_file)
    print("✓ Piping demo completed")


def demo_security():
    """Demonstrate security mechanisms"""
    print("\n" + "="*70)
    print("DEMO 2: SECURITY MECHANISMS")
    print("="*70)
    
    auth_system = UserAuthenticationSystem()
    
    # Demo 1: User Authentication
    print("\n--- User Authentication ---")
    print("Attempting login...")
    
    success, message = auth_system.login("admin", "admin123")
    print(f"Admin login: {message}")
    
    admin_user = auth_system.get_current_user()
    if admin_user:
        print(f"Current user: {admin_user.username}")
        print(f"Role: {admin_user.role.value}")
        print(f"Is Admin: {auth_system.is_admin()}")
    
    # Demo 2: List Users
    print("\n--- User Management ---")
    users = auth_system.list_users()
    print("All System Users:")
    for user in users:
        print(f"  - {user['username']:<10} ({user['role']:<10})")
    
    # Demo 3: File Permissions
    print("\n--- File Permissions ---")
    
    # Register files with different permissions
    test_file = "secure_data.txt"
    Path(test_file).touch()
    
    # Register with restrictive permissions (700 = rwx------)
    perms_700 = FilePermissions.from_octal(700)
    auth_system.register_file(test_file, "admin", "admin", perms_700)
    
    print(f"File: {test_file}")
    print(f"Permissions: {perms_700} (octal: {perms_700.to_octal()})")
    
    # Check access
    print("\nAccess Control Checks:")
    print(f"Admin can read: {auth_system.can_read(test_file, 'admin')}")
    print(f"Admin can write: {auth_system.can_write(test_file, 'admin')}")
    print(f"Admin can execute: {auth_system.can_execute(test_file, 'admin')}")
    
    print(f"\nAlice can read: {auth_system.can_read(test_file, 'alice')}")
    print(f"Alice can write: {auth_system.can_write(test_file, 'alice')}")
    
    # Demo permission change
    print("\n--- Changing Permissions ---")
    perms_755 = FilePermissions.from_octal(755)
    success, msg = auth_system.change_permissions(test_file, 755, "admin")
    print(f"Changed to 755: {msg}")
    
    file_info = auth_system.get_file_permissions(test_file)
    print(f"New permissions: {file_info['permissions']} (octal: {file_info['octal']})")
    
    # Cleanup
    os.remove(test_file)
    print("\n✓ Security demo completed")


def demo_password_hashing():
    """Demonstrate password hashing"""
    print("\n" + "="*70)
    print("DEMO 3: PASSWORD SECURITY")
    print("="*70)
    
    from security import User
    
    password = "mySecurePassword123"
    
    print(f"\nOriginal Password: {password}")
    
    # Hash password
    hashed = User.hash_password(password)
    print(f"Hashed (SHA256): {hashed[:32]}...")
    
    # Verify
    user = User(
        username="testuser",
        password_hash=hashed,
        role=None,
        created_at="2024-01-01"
    )
    
    print(f"\nPassword Verification:")
    print(f"Correct password: {user.verify_password(password)}")
    print(f"Wrong password: {user.verify_password('wrongpassword')}")
    
    print("\n✓ Password security demo completed")


def demo_file_permissions_octal():
    """Demonstrate octal permission conversions"""
    print("\n" + "="*70)
    print("DEMO 4: OCTAL PERMISSION SYSTEM")
    print("="*70)
    
    permission_examples = [
        (700, "rwx------", "Owner full access only"),
        (755, "rwxr-xr-x", "Owner full, group/others read+execute"),
        (644, "rw-r--r--", "Owner read+write, others read only"),
        (600, "rw-------", "Owner read+write only (secure)"),
        (777, "rwxrwxrwx", "Everyone full access (not recommended)"),
    ]
    
    print("\nCommon Permission Patterns:")
    print("─" * 70)
    print(f"{'Octal':<8} {'Symbolic':<15} {'Description':<30}")
    print("─" * 70)
    
    for octal, symbolic, description in permission_examples:
        print(f"{octal:<8} {symbolic:<15} {description:<30}")
    
    print("\nTesting Conversion:")
    for octal, expected_symbolic, _ in permission_examples:
        perms = FilePermissions.from_octal(octal)
        print(f"  {octal} -> {str(perms):<15} {'✓' if str(perms) == expected_symbolic else '✗'}")
    
    print("\n✓ Permission system demo completed")


def demo_multi_user_scenario():
    """Demonstrate multi-user scenario"""
    print("\n" + "="*70)
    print("DEMO 5: MULTI-USER SCENARIO")
    print("="*70)
    
    auth_system = UserAuthenticationSystem()
    
    # Create a shared file
    shared_file = "shared_document.txt"
    Path(shared_file).touch()
    with open(shared_file, 'w') as f:
        f.write("This is a shared document\n")
    
    # Register with specific permissions
    perms = FilePermissions(
        owner_read=True, owner_write=True, owner_execute=False,
        group_read=True, group_write=False, group_execute=False,
        other_read=False, other_write=False, other_execute=False
    )
    
    auth_system.register_file(shared_file, "alice", "users", perms)
    
    print(f"\nFile: {shared_file}")
    print(f"Owner: alice")
    print(f"Group: users")
    print(f"Permissions: {perms} ({perms.to_octal()})")
    
    print("\n--- User Access Check ---")
    
    users_to_check = ["alice", "bob", "guest"]
    
    for user in users_to_check:
        can_read = auth_system.can_read(shared_file, user)
        can_write = auth_system.can_write(shared_file, user)
        access_status = f"R:{can_read}, W:{can_write}"
        print(f"{user:<10} : {access_status}")
    
    # Cleanup
    os.remove(shared_file)
    print("\n✓ Multi-user scenario demo completed")


def main():
    """Run all demos"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "DELIVERABLE 4 DEMONSTRATION" + " "*26 + "║")
    print("║" + " "*10 + "Piping, Security, and Integrated Features" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        demo_piping()
        demo_security()
        demo_password_hashing()
        demo_file_permissions_octal()
        demo_multi_user_scenario()
        
        print("\n" + "="*70)
        print("✓ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nKey Features Demonstrated:")
        print("  1. Command Piping - chaining commands with pipes")
        print("  2. User Authentication - login with multiple users")
        print("  3. Role-Based Access - admin, user, guest roles")
        print("  4. File Permissions - Unix-style permission system")
        print("  5. Password Security - SHA256 hashing and verification")
        print("  6. Multi-User Scenarios - file access by different users")
        print("\n" + "="*70 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
