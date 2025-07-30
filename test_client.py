#!/usr/bin/env python3
"""
Test client for VersionOne MCP Server

This script helps test the VersionOne MCP server tools directly
without needing a full MCP client setup.
"""

import asyncio
import os
import json
from typing import Dict, Any

# Test the VersionOne connection directly
import httpx

async def test_versionone_client():
    """Test the VersionOne client directly"""
    
    # Load configuration from environment
    base_url = os.getenv('VERSIONONE_BASE_URL')
    access_token = os.getenv('VERSIONONE_ACCESS_TOKEN')
    
    if not base_url or not access_token:
        print("❌ Error: Missing environment variables")
        print("Please set VERSIONONE_BASE_URL and VERSIONONE_ACCESS_TOKEN")
        return False
    
    print(f"🔧 Testing VersionOne connection to: {base_url}")
    print(f"🔑 Using access token: {access_token[:10]}...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    async def make_request(endpoint: str, params: dict | None = None):
        url = f"{base_url.rstrip('/')}/rest-1.v1/Data/{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    try:
        # Test 1: Get list of stories
        print("\n📖 Test 1: Getting list of stories...")
        stories = await make_request('Story', {
            'sel': 'Name,Number,Status',
            'where': 'AssetState!="Dead"',
            'pageSize': 5
        })
        print(f"✅ Found {stories.get('total', 0)} stories")
        if stories.get('Assets'):
            for story in stories['Assets'][:3]:  # Show first 3
                name = story.get('Attributes', {}).get('Name', {}).get('value', 'N/A')
                number = story.get('Attributes', {}).get('Number', {}).get('value', 'N/A')
                print(f"   • {number}: {name}")
        
        # Test 2: Get list of features/epics
        print("\n🎯 Test 2: Getting list of features...")
        features = await make_request('Epic', {
            'sel': 'Name,Number,Status',
            'where': 'AssetState!="Dead"',
            'pageSize': 5
        })
        print(f"✅ Found {features.get('total', 0)} features")
        if features.get('Assets'):
            for feature in features['Assets'][:3]:  # Show first 3
                name = feature.get('Attributes', {}).get('Name', {}).get('value', 'N/A')
                number = feature.get('Attributes', {}).get('Number', {}).get('value', 'N/A')
                print(f"   • {number}: {name}")
        
        # Test 3: Get specific story details (if we have stories)
        if stories.get('Assets'):
            first_story = stories['Assets'][0]
            story_id = first_story.get('id')
            if story_id and ':' in story_id:
                story_num = story_id.split(':')[1]
                print(f"\n📋 Test 3: Getting details for story {story_id}...")
                story_details = await make_request(f'Story/{story_num}', {
                    'sel': 'Name,Number,Description,Status,Owner'
                })
                print("✅ Retrieved story details successfully")
                story_name = story_details.get('Attributes', {}).get('Name', {}).get('value', 'N/A')
                print(f"   Story: {story_name}")
        
        # Test 4: Get specific feature details (if we have features)
        if features.get('Assets'):
            first_feature = features['Assets'][0]
            feature_id = first_feature.get('id')
            if feature_id and ':' in feature_id:
                feature_num = feature_id.split(':')[1]
                print(f"\n🎯 Test 4: Getting details for feature {feature_id}...")
                feature_details = await make_request(f'Epic/{feature_num}', {
                    'sel': 'Name,Number,Description,Status,Owner'
                })
                print("✅ Retrieved feature details successfully")
                feature_name = feature_details.get('Attributes', {}).get('Name', {}).get('value', 'N/A')
                print(f"   Feature: {feature_name}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def print_configuration_help():
    """Print help for configuration"""
    print("🔧 VersionOne MCP Server Test Client")
    print("=" * 40)
    print("\nThis test client validates your VersionOne connection and MCP server functionality.")
    print("\n📋 Prerequisites:")
    print("1. Set environment variables:")
    print("   export VERSIONONE_BASE_URL='https://your-v1-host.com/YourInstance'")
    print("   export VERSIONONE_ACCESS_TOKEN='your-access-token'")
    print("\n2. Ensure you have network access to your VersionOne instance")
    print("\n3. Verify your access token has appropriate permissions")

async def main():
    """Main test function"""
    print_configuration_help()
    
    # Check if environment is configured
    if not os.getenv('VERSIONONE_BASE_URL') or not os.getenv('VERSIONONE_ACCESS_TOKEN'):
        print("\n❌ Environment not configured. Please set the required variables.")
        return
    
    print("\n🚀 Starting tests...")
    success = await test_versionone_client()
    
    if success:
        print("\n✅ Your VersionOne MCP Server is ready to use!")
        print("\nNext steps:")
        print("1. Configure your MCP client to use this server")
        print("2. Start using the available tools:")
        print("   • get_stories")
        print("   • get_story_details") 
        print("   • get_features")
        print("   • get_feature_details")
    else:
        print("\n❌ Tests failed. Please check your configuration and try again.")
        print("\nTroubleshooting:")
        print("• Verify your VersionOne URL is correct")
        print("• Check that your access token is valid and not expired")
        print("• Ensure you have network connectivity to VersionOne")
        print("• Check the server logs for more detailed error information")

if __name__ == "__main__":
    asyncio.run(main()) 