#!/usr/bin/env python3
"""
Script to fix all remaining async test methods in test_auth_service.py
Following TDD principles - GREEN phase completion
"""

import re

def fix_all_async_tests():
    with open('tests/unit/test_auth_service.py', 'r') as f:
        content = f.read()
    
    # List of all test methods that need to be made async
    async_test_methods = [
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
    
    # Fix each test method
    for method_name in async_test_methods:
        # Add @pytest.mark.asyncio decorator and make method async
        pattern = f'(def {method_name}\(self, [^)]*\):)'
        replacement = f'@pytest.mark.asyncio\n    async def {method_name}(self, \\1'
        content = re.sub(pattern, replacement, content)
        
        # Add await to service method calls
        service_methods = [
            'authenticate_user', 'register_user', 'refresh_token', 'logout_user',
            'verify_email', 'change_password', 'request_password_reset', 'reset_password'
        ]
        
        for service_method in service_methods:
            # Fix method calls in the test
            content = re.sub(
                f'result = auth_service\.{service_method}\(',
                f'result = await auth_service.{service_method}(',
                content
            )
    
    with open('tests/unit/test_auth_service.py', 'w') as f:
        f.write(content)
    
    print("Fixed all async test methods")

if __name__ == "__main__":
    fix_all_async_tests()

