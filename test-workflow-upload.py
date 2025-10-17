#!/usr/bin/env python3
"""
Test script to upload sample requirements and start workflow
"""

import requests
import json

def test_workflow_upload():
    """Test uploading sample requirements and starting workflow"""
    
    # Project ID from our previous creation
    project_id = "ed97970f-304b-496a-baea-c02ccf56a522"
    
    # Sample requirements file path
    requirements_file = "/Users/schwipee/dev/archMesh/archmesh-poc/sample-docs/sample-requirements.txt"
    
    print(f"🚀 Testing workflow upload for project: {project_id}")
    print(f"📄 Using requirements file: {requirements_file}")
    
    # Prepare the multipart form data
    with open(requirements_file, 'rb') as f:
        files = {
            'file': ('sample-requirements.txt', f, 'text/plain')
        }
        
        data = {
            'project_id': project_id,
            'domain': 'cloud-native',
            'project_context': 'E-commerce platform for handmade crafts',
            'llm_provider': 'deepseek'
        }
        
        # Make the request
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/workflows/start',
                files=files,
                data=data,
                headers={'Origin': 'http://localhost:3000'}
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Workflow started successfully!")
                print(f"🆔 Session ID: {result.get('session_id')}")
                print(f"📋 Current Stage: {result.get('current_stage')}")
                print(f"🔄 Is Active: {result.get('is_active')}")
                
                # Return session ID for further testing
                return result.get('session_id')
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

def check_workflow_status(session_id):
    """Check workflow status"""
    if not session_id:
        print("❌ No session ID provided")
        return
    
    print(f"\n🔍 Checking workflow status for session: {session_id}")
    
    try:
        response = requests.get(
            f'http://localhost:8000/api/v1/workflows/{session_id}/status',
            headers={'Origin': 'http://localhost:3000'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Current Stage: {result.get('current_stage')}")
            print(f"🔄 Is Active: {result.get('is_active')}")
            print(f"📊 Stage Progress: {result.get('state_data', {}).get('stage_progress', 0)}")
            print(f"✅ Completed Stages: {result.get('state_data', {}).get('completed_stages', [])}")
            
            if result.get('state_data', {}).get('errors'):
                print(f"❌ Errors: {result.get('state_data', {}).get('errors')}")
        else:
            print(f"❌ Error checking status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception checking status: {e}")

if __name__ == "__main__":
    # Test the workflow upload
    session_id = test_workflow_upload()
    
    if session_id:
        # Wait a moment and check status
        import time
        time.sleep(5)
        check_workflow_status(session_id)
        
        # Check again after more time
        time.sleep(10)
        check_workflow_status(session_id)
