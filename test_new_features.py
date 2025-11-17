#!/usr/bin/env python3
"""Test script for new features: health check, stats, rate limiting."""

import sys
import time
import httpx
from typing import Dict, Any


API_URL = "http://localhost:8080"


async def test_health_endpoint(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test health endpoint with model readiness check."""
    print("Testing /health endpoint...")
    try:
        response = await client.get(f"{API_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check required fields
        assert "status" in data, "Missing 'status' field"
        assert "model_ready" in data, "Missing 'model_ready' field"
        assert "service" in data, "Missing 'service' field"
        
        print(f"  ✓ Status: {data['status']}")
        print(f"  ✓ Model ready: {data['model_ready']}")
        print(f"  ✓ Service: {data['service']}")
        
        return {"success": True, "data": data}
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return {"success": False, "error": str(e)}


async def test_stats_endpoint(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test stats endpoint."""
    print("\nTesting /v1/stats endpoint...")
    try:
        response = await client.get(f"{API_URL}/v1/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check required fields
        required_fields = [
            "uptime_seconds", "total_requests", "total_tokens",
            "average_total_tokens", "requests_per_hour", "tokens_per_hour"
        ]
        for field in required_fields:
            assert field in data, f"Missing '{field}' field"
        
        print(f"  ✓ Uptime: {data['uptime_seconds']}s ({data.get('uptime_hours', 0):.2f}h)")
        print(f"  ✓ Total requests: {data['total_requests']}")
        print(f"  ✓ Total tokens: {data['total_tokens']}")
        print(f"  ✓ Average tokens: {data['average_total_tokens']:.2f}")
        print(f"  ✓ Requests/hour: {data['requests_per_hour']:.2f}")
        print(f"  ✓ Tokens/hour: {data['tokens_per_hour']:.2f}")
        
        if data.get('requests_by_model'):
            print(f"  ✓ Models used: {list(data['requests_by_model'].keys())}")
        
        if data.get('finish_reasons'):
            print(f"  ✓ Finish reasons: {data['finish_reasons']}")
        
        return {"success": True, "data": data}
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return {"success": False, "error": str(e)}


async def test_rate_limiting(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test rate limiting (should allow requests, check headers)."""
    print("\nTesting rate limiting...")
    try:
        # Make a request to check rate limit headers
        response = await client.get(f"{API_URL}/v1/models")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check for rate limit headers
        headers = response.headers
        rate_limit_headers = [
            "X-RateLimit-Limit-Minute",
            "X-RateLimit-Limit-Hour",
            "X-RateLimit-Remaining-Minute",
            "X-RateLimit-Remaining-Hour"
        ]
        
        found_headers = []
        for header in rate_limit_headers:
            if header in headers:
                found_headers.append(header)
                print(f"  ✓ {header}: {headers[header]}")
        
        if len(found_headers) == len(rate_limit_headers):
            print("  ✓ All rate limit headers present")
            return {"success": True, "headers": {h: headers[h] for h in rate_limit_headers}}
        else:
            missing = set(rate_limit_headers) - set(found_headers)
            print(f"  ⚠ Missing headers: {missing}")
            return {"success": False, "error": f"Missing headers: {missing}"}
            
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return {"success": False, "error": str(e)}


async def test_error_sanitization(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test that error messages are sanitized."""
    print("\nTesting error sanitization...")
    try:
        # Make an invalid request
        response = await client.post(
            f"{API_URL}/v1/chat/completions",
            json={
                "model": "test",
                "messages": [],  # Empty messages should fail
            }
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        
        # Check error structure
        assert "error" in data, "Missing 'error' field"
        assert "message" in data["error"], "Missing 'message' in error"
        assert "type" in data["error"], "Missing 'type' in error"
        
        error_msg = data["error"]["message"]
        # Should not contain internal details like file paths, stack traces, etc.
        internal_indicators = ["Traceback", "File", "line", ".py", "Exception:"]
        for indicator in internal_indicators:
            assert indicator.lower() not in error_msg.lower(), f"Error message contains internal details: {indicator}"
        
        print(f"  ✓ Error properly formatted: {error_msg[:100]}")
        print(f"  ✓ Error type: {data['error']['type']}")
        
        return {"success": True, "error": data["error"]}
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return {"success": False, "error": str(e)}


async def test_root_endpoint(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Test root endpoint."""
    print("\nTesting / endpoint...")
    try:
        response = await client.get(f"{API_URL}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "status" in data, "Missing 'status' field"
        print(f"  ✓ Status: {data['status']}")
        print(f"  ✓ Service: {data.get('service', 'N/A')}")
        
        return {"success": True, "data": data}
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return {"success": False, "error": str(e)}


async def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing New Features")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print()
    
    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        results = []
        
        # Test root endpoint
        results.append(await test_root_endpoint(client))
        
        # Test health endpoint
        results.append(await test_health_endpoint(client))
        
        # Test stats endpoint (before any requests)
        results.append(await test_stats_endpoint(client))
        
        # Test rate limiting
        results.append(await test_rate_limiting(client))
        
        # Test error sanitization
        results.append(await test_error_sanitization(client))
        
        # Test stats endpoint again (after requests)
        print("\nTesting /v1/stats endpoint (after requests)...")
        results.append(await test_stats_endpoint(client))
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        for i, r in enumerate(results, 1):
            if not r["success"]:
                print(f"  Test {i}: {r.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))

