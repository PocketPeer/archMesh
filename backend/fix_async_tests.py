#!/usr/bin/env python3
"""
Script to fix async test methods in test_auth_service.py
"""

import re

def fix_async_tests():
    with open('tests/unit/test_auth_service.py', 'r') as f:
        content = f.read()
    
    # Add @pytest.mark.asyncio to all test methods that call async methods
    async_test_methods = [
        'test_authenticate_user_invalid_password',
        'test_authenticate_user_inactive_account',
        'test_authenticate_user_unverified_account',
        'test_register_user_success',
        'test_register_user_email_already_exists',
        'test_register_user_weak_password',
        'test_refresh_token_success',
        'test_refresh_token_invalid_token',
        'test_logout_user_success',
        'test_verify_email_success',
        'test_verify_email_invalid_token',
        'test_verify_email_already_verified',
        'test_change_password_success',
        'test_change_password_invalid_old_password',
        'test_change_password_weak_new_password',
        'test_reset_password_request_success',
        'test_reset_password_request_user_not_found',
        'test_reset_password_success',
        'test_reset_password_invalid_token',
        'test_reset_password_weak_password'
    ]
    
    for method_name in async_test_methods:
        # Add @pytest.mark.asyncio decorator
        pattern = f'(def {method_name}\(self, [^)]*\):)'
        replacement = f'@pytest.mark.asyncio\n    async def {method_name}(self, \\1'
        content = re.sub(pattern, replacement, content)
        
        # Add await to method calls
        content = re.sub(
            f'result = auth_service\.{method_name.replace("test_", "").replace("_", "_")}\(',
            f'result = await auth_service.{method_name.replace("test_", "").replace("_", "_")}(',
            content
        )
    
    # Fix specific method calls
    method_mappings = {
        'test_authenticate_user_invalid_password': 'authenticate_user',
        'test_authenticate_user_inactive_account': 'authenticate_user',
        'test_authenticate_user_unverified_account': 'authenticate_user',
        'test_register_user_success': 'register_user',
        'test_register_user_email_already_exists': 'register_user',
        'test_register_user_weak_password': 'register_user',
        'test_refresh_token_success': 'refresh_token',
        'test_refresh_token_invalid_token': 'refresh_token',
        'test_logout_user_success': 'logout_user',
        'test_verify_email_success': 'verify_email',
        'test_verify_email_invalid_token': 'verify_email',
        'test_verify_email_already_verified': 'verify_email',
        'test_change_password_success': 'change_password',
        'test_change_password_invalid_old_password': 'change_password',
        'test_change_password_weak_new_password': 'change_password',
        'test_reset_password_request_success': 'request_password_reset',
        'test_reset_password_request_user_not_found': 'request_password_reset',
        'test_reset_password_success': 'reset_password',
        'test_reset_password_invalid_token': 'reset_password',
        'test_reset_password_weak_password': 'reset_password'
    }
    
    for test_method, service_method in method_mappings.items():
        # Fix the method calls
        content = re.sub(
            f'result = auth_service\.{service_method}\(',
            f'result = await auth_service.{service_method}(',
            content
        )
    
    with open('tests/unit/test_auth_service.py', 'w') as f:
        f.write(content)
    
    print("Fixed async test methods")

if __name__ == "__main__":
    fix_async_tests()

