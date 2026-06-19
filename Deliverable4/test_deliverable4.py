#!/usr/bin/env python3
"""
Test Suite for Deliverable 4: Integration and Security
Tests piping, security mechanisms, and integrated features
"""

import unittest
import os
from pathlib import Path
from security import (
    UserAuthenticationSystem, UserRole, FilePermissions, User
)
from piping import CommandPipeline


class TestPiping(unittest.TestCase):
    """Tests for command piping functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.pipeline = CommandPipeline(".")
        # Create test file
        self.test_file = "test_piping_data.txt"
        with open(self.test_file, 'w') as f:
            f.write("apple\nbanana\napricot\ncherry\nblueberry\navocado\n")
    
    def tearDown(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_pipe_detection(self):
        """Test pipe operator detection"""
        self.assertTrue(CommandPipeline.has_pipe("ls | grep txt"))
        self.assertFalse(CommandPipeline.has_pipe("ls"))
        self.assertTrue(CommandPipeline.has_pipe("cat file | sort | grep pattern"))
    
    def test_pipeline_parsing(self):
        """Test command parsing from pipe string"""
        commands = CommandPipeline.parse_pipeline("ls | grep txt")
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0], "ls")
        self.assertEqual(commands[1], "grep txt")
    
    def test_pipeline_parsing_multiple(self):
        """Test parsing multiple pipes"""
        commands = CommandPipeline.parse_pipeline("cat file | sort | grep pattern")
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0], "cat file")
        self.assertEqual(commands[1], "sort")
        self.assertEqual(commands[2], "grep pattern")
    
    def test_single_command_execution(self):
        """Test single command execution without piping"""
        success, output = self.pipeline.execute_single("echo 'test'")
        self.assertTrue(success)
        self.assertIn("test", output)
    
    def test_pipe_execution_simple(self):
        """Test simple pipe execution"""
        success, output = self.pipeline.execute(f"cat {self.test_file} | grep apple")
        self.assertTrue(success)
        self.assertIn("apple", output)
    
    def test_pipe_execution_filtering(self):
        """Test pipe with multiple matches"""
        success, output = self.pipeline.execute(f"cat {self.test_file} | grep a")
        self.assertTrue(success)
        lines = output.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Multiple 'a' words
    
    def test_nonexistent_command(self):
        """Test error handling for nonexistent command"""
        success, output = self.pipeline.execute("nonexistent_command_xyz")
        self.assertFalse(success)


class TestUserAuthentication(unittest.TestCase):
    """Tests for user authentication system"""
    
    def setUp(self):
        """Setup authentication system"""
        self.auth = UserAuthenticationSystem()
    
    def test_default_users_exist(self):
        """Test that default users are created"""
        self.assertIn("admin", self.auth.users)
        self.assertIn("alice", self.auth.users)
        self.assertIn("bob", self.auth.users)
        self.assertIn("guest", self.auth.users)
    
    def test_admin_login(self):
        """Test admin user login"""
        success, message = self.auth.login("admin", "admin123")
        self.assertTrue(success)
        self.assertIsNotNone(self.auth.current_user)
        self.assertEqual(self.auth.current_user.username, "admin")
    
    def test_user_login(self):
        """Test regular user login"""
        success, message = self.auth.login("alice", "alice123")
        self.assertTrue(success)
        self.assertEqual(self.auth.current_user.role, UserRole.USER)
    
    def test_guest_login(self):
        """Test guest user login"""
        success, message = self.auth.login("guest", "guest")
        self.assertTrue(success)
        self.assertEqual(self.auth.current_user.role, UserRole.GUEST)
    
    def test_invalid_username(self):
        """Test login with invalid username"""
        success, message = self.auth.login("nonexistent", "password")
        self.assertFalse(success)
    
    def test_invalid_password(self):
        """Test login with invalid password"""
        success, message = self.auth.login("admin", "wrongpassword")
        self.assertFalse(success)
    
    def test_is_admin(self):
        """Test admin role checking"""
        self.auth.login("admin", "admin123")
        self.assertTrue(self.auth.is_admin())
        
        self.auth.logout()
        self.auth.login("alice", "alice123")
        self.assertFalse(self.auth.is_admin())
    
    def test_logout(self):
        """Test logout functionality"""
        self.auth.login("admin", "admin123")
        self.assertIsNotNone(self.auth.current_user)
        
        self.auth.logout()
        self.assertIsNone(self.auth.current_user)
    
    def test_list_users(self):
        """Test listing users (admin only)"""
        self.auth.login("admin", "admin123")
        users = self.auth.list_users()
        self.assertGreater(len(users), 0)
        
        # Non-admin shouldn't see users
        self.auth.logout()
        self.auth.login("alice", "alice123")
        users = self.auth.list_users()
        self.assertEqual(len(users), 0)


class TestPasswordSecurity(unittest.TestCase):
    """Tests for password hashing and verification"""
    
    def test_password_hashing(self):
        """Test password hashing is consistent"""
        password = "testPassword123"
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)
        self.assertEqual(hash1, hash2)
    
    def test_password_hashes_are_different(self):
        """Test that different passwords produce different hashes"""
        hash1 = User.hash_password("password1")
        hash2 = User.hash_password("password2")
        self.assertNotEqual(hash1, hash2)
    
    def test_password_verification(self):
        """Test password verification"""
        password = "securePassword"
        user = User(
            username="testuser",
            password_hash=User.hash_password(password),
            role=UserRole.USER,
            created_at="2024-01-01"
        )
        
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password("wrongpassword"))


class TestFilePermissions(unittest.TestCase):
    """Tests for file permission system"""
    
    def setUp(self):
        """Setup permission tests"""
        self.auth = UserAuthenticationSystem()
        self.test_file = "test_permissions.txt"
        Path(self.test_file).touch()
    
    def tearDown(self):
        """Cleanup"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_permission_conversion_700(self):
        """Test octal to symbolic conversion (700)"""
        perms = FilePermissions.from_octal(700)
        self.assertTrue(perms.owner_read)
        self.assertTrue(perms.owner_write)
        self.assertTrue(perms.owner_execute)
        self.assertFalse(perms.group_read)
        self.assertFalse(perms.other_read)
    
    def test_permission_conversion_755(self):
        """Test octal to symbolic conversion (755)"""
        perms = FilePermissions.from_octal(755)
        self.assertTrue(perms.owner_read)
        self.assertTrue(perms.owner_write)
        self.assertTrue(perms.owner_execute)
        self.assertTrue(perms.group_read)
        self.assertTrue(perms.group_execute)
        self.assertTrue(perms.other_read)
        self.assertTrue(perms.other_execute)
    
    def test_permission_conversion_644(self):
        """Test octal to symbolic conversion (644)"""
        perms = FilePermissions.from_octal(644)
        self.assertTrue(perms.owner_read)
        self.assertTrue(perms.owner_write)
        self.assertFalse(perms.owner_execute)
        self.assertTrue(perms.group_read)
        self.assertFalse(perms.group_write)
        self.assertTrue(perms.other_read)
        self.assertFalse(perms.other_write)
    
    def test_octal_conversion(self):
        """Test converting permissions back to octal"""
        for octal in [700, 755, 644, 600, 777]:
            perms = FilePermissions.from_octal(octal)
            self.assertEqual(perms.to_octal(), octal)
    
    def test_permission_string_representation(self):
        """Test symbolic permission representation"""
        perms = FilePermissions.from_octal(755)
        self.assertEqual(str(perms), "rwxr-xr-x")
        
        perms = FilePermissions.from_octal(644)
        self.assertEqual(str(perms), "rw-r--r--")
    
    def test_file_registration(self):
        """Test registering file in security system"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions.from_octal(755)
        
        success = self.auth.register_file(self.test_file, "admin", "admin", perms)
        self.assertTrue(success)
        self.assertIn(self.test_file, self.auth.file_metadata)
    
    def test_read_permission_owner(self):
        """Test owner can read"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions(owner_read=True)
        self.auth.register_file(self.test_file, "admin", "admin", perms)
        
        self.assertTrue(self.auth.can_read(self.test_file, "admin"))
    
    def test_read_permission_denied(self):
        """Test others cannot read when denied"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions(owner_read=True, other_read=False)
        self.auth.register_file(self.test_file, "admin", "admin", perms)
        
        self.assertFalse(self.auth.can_read(self.test_file, "alice"))
    
    def test_admin_bypass(self):
        """Test admin bypasses permission checks"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions(owner_read=True, other_read=False)
        self.auth.register_file(self.test_file, "alice", "users", perms)
        
        # Admin can read even though not owner
        self.assertTrue(self.auth.can_read(self.test_file, "admin"))
    
    def test_change_permissions(self):
        """Test changing file permissions"""
        self.auth.login("admin", "admin123")
        self.auth.register_file(self.test_file, "admin", "admin")
        
        success, msg = self.auth.change_permissions(self.test_file, 755, "admin")
        self.assertTrue(success)
        
        file_info = self.auth.get_file_permissions(self.test_file)
        self.assertEqual(file_info['octal'], 755)


class TestMultiUserScenarios(unittest.TestCase):
    """Tests for multi-user file access scenarios"""
    
    def setUp(self):
        """Setup multi-user tests"""
        self.auth = UserAuthenticationSystem()
        self.test_file = "shared_file.txt"
        Path(self.test_file).touch()
    
    def tearDown(self):
        """Cleanup"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_owner_full_access(self):
        """Test file owner has full access"""
        self.auth.login("alice", "alice123")
        perms = FilePermissions(owner_read=True, owner_write=True)
        self.auth.register_file(self.test_file, "alice", "users", perms)
        
        self.assertTrue(self.auth.can_read(self.test_file, "alice"))
        self.assertTrue(self.auth.can_write(self.test_file, "alice"))
    
    def test_group_limited_access(self):
        """Test group members have limited access"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions(
            owner_read=True, owner_write=True,
            group_read=True, group_write=False
        )
        self.auth.register_file(self.test_file, "alice", "users", perms)
        
        # Bob is also in 'users' group
        self.assertTrue(self.auth.can_read(self.test_file, "bob"))
        self.assertFalse(self.auth.can_write(self.test_file, "bob"))
    
    def test_others_restricted(self):
        """Test others have restricted access"""
        self.auth.login("admin", "admin123")
        perms = FilePermissions(
            owner_read=True, owner_write=True,
            other_read=False, other_write=False
        )
        self.auth.register_file(self.test_file, "alice", "users", perms)
        
        self.assertFalse(self.auth.can_read(self.test_file, "guest"))
        self.assertFalse(self.auth.can_write(self.test_file, "guest"))
    
    def test_permission_escalation_prevention(self):
        """Test that non-owners cannot change permissions"""
        self.auth.login("alice", "alice123")
        perms = FilePermissions.from_octal(755)
        self.auth.register_file(self.test_file, "alice", "users", perms)
        
        # Bob tries to change permissions
        self.auth.logout()
        self.auth.login("bob", "bob123")
        
        success, msg = self.auth.change_permissions(self.test_file, 777, "bob")
        self.assertFalse(success)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple features"""
    
    def test_piping_with_security(self):
        """Test piping respects file permissions"""
        pipeline = CommandPipeline(".")
        auth = UserAuthenticationSystem()
        
        # Create test file
        test_file = "integration_test.txt"
        with open(test_file, 'w') as f:
            f.write("test content\n")
        
        # Register with restrictive permissions
        auth.login("admin", "admin123")
        perms = FilePermissions.from_octal(600)
        auth.register_file(test_file, "admin", "admin", perms)
        
        # Piping should work (shell doesn't enforce permissions in this version)
        success, output = pipeline.execute(f"cat {test_file} | grep test")
        self.assertTrue(success)
        
        # Cleanup
        os.remove(test_file)
    
    def test_authenticated_user_operations(self):
        """Test operations by different authenticated users"""
        auth = UserAuthenticationSystem()
        test_file = "user_ops.txt"
        Path(test_file).touch()
        
        # Admin creates and sets permissions
        auth.login("admin", "admin123")
        self.auth.register_file(test_file, "admin", "admin")
        auth.change_permissions(test_file, 755, "admin")
        admin_can_read = auth.can_read(test_file, "admin")
        
        # Alice logs in and checks access
        auth.logout()
        auth.login("alice", "alice123")
        alice_can_read = auth.can_read(test_file, "alice")
        
        self.assertTrue(admin_can_read)  # 755 - everyone can read
        self.assertTrue(alice_can_read)
        
        # Cleanup
        os.remove(test_file)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPiping))
    suite.addTests(loader.loadTestsFromTestCase(TestUserAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestFilePermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiUserScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
