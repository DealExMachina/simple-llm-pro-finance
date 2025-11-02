#!/usr/bin/env python3
"""
Test script to verify access to DragonLLM models using Hugging Face Hub.

This script tests:
1. Token detection and authentication
2. Model repository access
3. Model information retrieval
4. Token permissions

Note: You can also use the HF MCP server if available:
  - Uses huggingface_hub library directly
  - Compatible with MCP server setup

Run with: python scripts/test_model_access.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from huggingface_hub import login, whoami, HfApi, model_info, get_token
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("❌ Error: huggingface_hub not installed")
    print("   Install it with: pip install huggingface-hub")
    sys.exit(1)

# Model to test access to
MODEL_NAME = "DragonLLM/qwen3-8b-fin-v1.0"


def get_hf_token():
    """Get Hugging Face token from environment variables or HF CLI cache"""
    # First try environment variables (priority for HF Spaces)
    token = (
        os.getenv("HF_TOKEN_LC2") or 
        os.getenv("HF_TOKEN_LC") or 
        os.getenv("HF_TOKEN") or
        os.getenv("HUGGING_FACE_HUB_TOKEN")
    )
    
    if token:
        # Determine source
        if os.getenv("HF_TOKEN_LC2"):
            source = "HF_TOKEN_LC2 (env)"
        elif os.getenv("HF_TOKEN_LC"):
            source = "HF_TOKEN_LC (env)"
        elif os.getenv("HF_TOKEN"):
            source = "HF_TOKEN (env)"
        else:
            source = "HUGGING_FACE_HUB_TOKEN (env)"
        return token, source
    
    # Fall back to HF CLI cached token (if available)
    try:
        cached_token = get_token()
        if cached_token:
            return cached_token, "HF CLI cache"
    except Exception:
        pass
    
    return None, None


def test_token_detection():
    """Test 1: Check if token is found in environment"""
    print("\n" + "="*70)
    print("TEST 1: Token Detection")
    print("="*70)
    
    token, source = get_hf_token()
    
    if token:
        print(f"✅ Token found: {source}")
        print(f"   Token length: {len(token)} characters")
        print(f"   Token preview: {token[:10]}...{token[-4:]}")
        return True, token, source
    else:
        print("❌ No token found in environment!")
        print("\n   Checked environment variables:")
        print("   - HF_TOKEN_LC2 (recommended for DragonLLM)")
        print("   - HF_TOKEN_LC")
        print("   - HF_TOKEN")
        print("   - HUGGING_FACE_HUB_TOKEN")
        print("\n   To set a token:")
        print("   export HF_TOKEN_LC2='your_token_here'")
        print("   Or use: huggingface-cli login")
        return False, None, None


def test_authentication(token):
    """Test 2: Authenticate with Hugging Face Hub"""
    print("\n" + "="*70)
    print("TEST 2: Hugging Face Hub Authentication")
    print("="*70)
    
    try:
        # Login with token
        login(token=token, add_to_git_credential=False)
        print("✅ Successfully authenticated with Hugging Face Hub")
        
        # Get user info
        try:
            user_info = whoami()
            print(f"✅ Logged in as: {user_info.get('name', 'Unknown')}")
            if 'type' in user_info:
                print(f"   Account type: {user_info['type']}")
            return True
        except Exception as e:
            print(f"⚠️  Authenticated but couldn't get user info: {e}")
            return True  # Still authenticated even if we can't get user info
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n   Possible causes:")
        print("   1. Invalid token")
        print("   2. Token expired")
        print("   3. Network connectivity issues")
        return False


def test_model_access(model_name):
    """Test 3: Check if we can access the model repository"""
    print("\n" + "="*70)
    print("TEST 3: Model Repository Access")
    print("="*70)
    print(f"Model: {model_name}")
    
    try:
        # Try to get model info
        print(f"   Attempting to access model repository...")
        info = model_info(model_name, token=True)
        
        print(f"✅ Successfully accessed model repository!")
        print(f"   Model ID: {info.id}")
        print(f"   Model tags: {', '.join(info.tags) if info.tags else 'None'}")
        
        # Check if model is gated
        if hasattr(info, 'gated') and info.gated:
            print(f"   ⚠️  Model is GATED - requires accepting terms")
        
        # Check available files
        if hasattr(info, 'siblings'):
            file_count = len(info.siblings) if info.siblings else 0
            print(f"   Files in repository: {file_count}")
            if file_count > 0 and info.siblings:
                print(f"   Sample files:")
                for sibling in info.siblings[:5]:
                    print(f"     - {sibling.rfilename} ({sibling.size / (1024**2):.1f} MB)")
                if file_count > 5:
                    print(f"     ... and {file_count - 5} more files")
        
        return True
        
    except HfHubHTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ Unauthorized (401): Token doesn't have access to this model")
            print("\n   Possible causes:")
            print("   1. You haven't accepted the model's terms of use")
            print(f"   2. Visit: https://huggingface.co/{model_name}")
            print("   3. Click 'Agree and access repository'")
            print("   4. Token doesn't have proper permissions")
            return False
        elif e.response.status_code == 403:
            print(f"❌ Forbidden (403): Access denied to this model")
            print("\n   This model may be private or require special access")
            return False
        elif e.response.status_code == 404:
            print(f"❌ Not Found (404): Model doesn't exist")
            return False
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e}")
            return False
    except Exception as e:
        print(f"❌ Error accessing model: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


def test_model_files(model_name):
    """Test 4: Check if we can list model files"""
    print("\n" + "="*70)
    print("TEST 4: Model Files Access")
    print("="*70)
    
    try:
        api = HfApi()
        files = api.list_repo_files(
            repo_id=model_name,
            repo_type="model",
            token=True
        )
        
        if files:
            print(f"✅ Found {len(files)} files in model repository")
            print(f"   Key files:")
            
            # Show important files
            important_files = [
                f for f in files if any(
                    ext in f.lower() 
                    for ext in ['.safetensors', '.bin', 'config.json', 'tokenizer', 'model']
                )
            ]
            
            for file in important_files[:10]:
                print(f"     - {file}")
            if len(files) > 10:
                print(f"     ... and {len(files) - 10} more files")
            
            return True
        else:
            print("⚠️  No files found in repository")
            return False
            
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return False


def test_token_permissions(token):
    """Test 5: Check token permissions"""
    print("\n" + "="*70)
    print("TEST 5: Token Permissions")
    print("="*70)
    
    try:
        api = HfApi()
        user_info = api.whoami(token=token)
        
        print(f"✅ Token has valid permissions")
        print(f"   User: {user_info.get('name', 'Unknown')}")
        print(f"   Type: {user_info.get('type', 'Unknown')}")
        
        # Check if user has read access
        if 'canRead' in user_info:
            print(f"   Can read repositories: {user_info['canRead']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# DragonLLM Model Access Test")
    print("#"*70)
    print(f"Testing access to: {MODEL_NAME}")
    
    results = {}
    
    # Test 1: Token detection
    success, token, source = test_token_detection()
    results['token_detection'] = success
    
    if not success:
        print("\n" + "="*70)
        print("❌ Cannot proceed without a token")
        print("="*70)
        return
    
    # Test 2: Authentication
    results['authentication'] = test_authentication(token)
    
    if not results['authentication']:
        print("\n" + "="*70)
        print("❌ Authentication failed - cannot proceed")
        print("="*70)
        return
    
    # Test 3: Model access
    results['model_access'] = test_model_access(MODEL_NAME)
    
    # Test 4: Model files (only if model access succeeded)
    if results['model_access']:
        results['model_files'] = test_model_files(MODEL_NAME)
    else:
        results['model_files'] = False
    
    # Test 5: Token permissions
    results['token_permissions'] = test_token_permissions(token)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"{status} - {test_display}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You have full access to the DragonLLM model.")
        print("   The model can be loaded in your application.")
    elif results.get('token_detection') and results.get('authentication'):
        print("\n⚠️  Authentication works but model access failed.")
        print("   This usually means:")
        print("   1. You need to accept the model's terms of use")
        print(f"   2. Visit: https://huggingface.co/{MODEL_NAME}")
        print("   3. Click 'Agree and access repository'")
    else:
        print("\n❌ Some tests failed. Check the errors above for details.")


if __name__ == "__main__":
    main()

