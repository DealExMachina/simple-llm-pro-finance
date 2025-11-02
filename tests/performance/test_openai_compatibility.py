"""
OpenAI API compatibility tests
Run with: pytest tests/performance/test_openai_compatibility.py -v -s
"""
import pytest
import httpx
from openai import OpenAI
import os

# Test configuration
BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"
# BASE_URL = "http://localhost:7860"  # For local testing

@pytest.fixture
def httpx_client():
    return httpx.AsyncClient(timeout=60.0)

@pytest.fixture
def openai_client():
    """Test using official OpenAI client library"""
    return OpenAI(
        base_url=f"{BASE_URL}/v1",
        api_key="dummy-key"  # Service may not require auth
    )


class TestEndpointCompatibility:
    """Test that all OpenAI endpoints are available and compatible"""
    
    @pytest.mark.asyncio
    async def test_list_models_endpoint(self, httpx_client):
        """Test GET /v1/models endpoint"""
        response = await httpx_client.get(f"{BASE_URL}/v1/models")
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"\n=== Models Endpoint ===")
        print(f"Response structure: {data.keys()}")
        
        # Check OpenAI-compatible structure
        assert "object" in data
        assert data["object"] == "list"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        
        # Check model object structure
        model = data["data"][0]
        assert "id" in model
        assert "object" in model
        assert model["object"] == "model"
        
        print(f"Available models: {[m['id'] for m in data['data']]}")
    
    
    @pytest.mark.asyncio
    async def test_chat_completions_endpoint(self, httpx_client):
        """Test POST /v1/chat/completions endpoint"""
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [
                {"role": "user", "content": "Say hello"}
            ]
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"\n=== Chat Completions Endpoint ===")
        print(f"Response structure: {data.keys()}")
        
        # Check OpenAI-compatible structure
        assert "id" in data
        assert "object" in data
        assert data["object"] == "chat.completion"
        assert "created" in data
        assert "model" in data
        assert "choices" in data
        assert "usage" in data
        
        # Check choices structure
        assert len(data["choices"]) > 0
        choice = data["choices"][0]
        assert "index" in choice
        assert "message" in choice
        assert "role" in choice["message"]
        assert "content" in choice["message"]
        assert "finish_reason" in choice
        
        # Check usage structure
        usage = data["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        
        print(f"Response: {choice['message']['content'][:100]}...")


class TestOpenAIClientLibrary:
    """Test compatibility with official OpenAI Python client"""
    
    def test_chat_completion_with_openai_client(self, openai_client):
        """Test chat completion using official OpenAI client"""
        try:
            response = openai_client.chat.completions.create(
                model="DragonLLM/qwen3-8b-fin-v1.0",
                messages=[
                    {"role": "user", "content": "What is 2+2?"}
                ],
                max_tokens=50
            )
            
            print(f"\n=== OpenAI Client Compatibility ===")
            print(f"Response type: {type(response)}")
            print(f"Model: {response.model}")
            print(f"Content: {response.choices[0].message.content}")
            print(f"Usage: {response.usage}")
            
            assert response.choices[0].message.content is not None
            assert len(response.choices) > 0
            
        except Exception as e:
            pytest.fail(f"OpenAI client failed: {e}")
    
    
    def test_streaming_with_openai_client(self, openai_client):
        """Test streaming with official OpenAI client"""
        try:
            stream = openai_client.chat.completions.create(
                model="DragonLLM/qwen3-8b-fin-v1.0",
                messages=[
                    {"role": "user", "content": "Count to 5"}
                ],
                max_tokens=50,
                stream=True
            )
            
            print(f"\n=== Streaming Compatibility ===")
            chunks = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
                    print(chunk.choices[0].delta.content, end="", flush=True)
            
            print()
            assert len(chunks) > 0, "No chunks received"
            
        except Exception as e:
            pytest.fail(f"Streaming failed: {e}")


class TestMessageFormats:
    """Test different message formats and parameters"""
    
    @pytest.mark.asyncio
    async def test_system_message(self, httpx_client):
        """Test with system message"""
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 50
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"\n=== System Message Test ===")
        print(f"Response: {data['choices'][0]['message']['content'][:100]}...")
    
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, httpx_client):
        """Test with conversation history"""
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [
                {"role": "user", "content": "My name is Alice."},
                {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
                {"role": "user", "content": "What's my name?"}
            ],
            "max_tokens": 50
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"\n=== Conversation History Test ===")
        print(f"Response: {data['choices'][0]['message']['content']}")
    
    
    @pytest.mark.asyncio
    async def test_various_parameters(self, httpx_client):
        """Test various OpenAI parameters"""
        parameters = [
            {"temperature": 0.0},
            {"temperature": 1.0},
            {"top_p": 0.5},
            {"max_tokens": 10},
            {"max_tokens": 100},
        ]
        
        print(f"\n=== Parameter Compatibility Test ===")
        
        for params in parameters:
            payload = {
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [{"role": "user", "content": "Hello"}],
                **params
            }
            
            response = await httpx_client.post(
                f"{BASE_URL}/v1/chat/completions",
                json=payload
            )
            
            assert response.status_code == 200
            print(f"✓ Parameters {params} work correctly")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_model(self, httpx_client):
        """Test with invalid model name"""
        payload = {
            "model": "invalid-model",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        print(f"\n=== Invalid Model Test ===")
        print(f"Status: {response.status_code}")
        # Should handle gracefully (either 400 or use default model)
    
    
    @pytest.mark.asyncio
    async def test_missing_messages(self, httpx_client):
        """Test with missing messages field"""
        payload = {
            "model": "DragonLLM/LLM-Pro-Finance-Small"
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        print(f"\n=== Missing Messages Test ===")
        print(f"Status: {response.status_code}")
        assert response.status_code in [400, 422], "Should return error for missing messages"
    
    
    @pytest.mark.asyncio
    async def test_empty_message(self, httpx_client):
        """Test with empty message content"""
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": ""}],
            "max_tokens": 50
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        print(f"\n=== Empty Message Test ===")
        print(f"Status: {response.status_code}")


class TestResponseFormat:
    """Test response format compliance"""
    
    @pytest.mark.asyncio
    async def test_response_schema(self, httpx_client):
        """Validate complete response schema"""
        payload = {
            "model": "DragonLLM/qwen3-8b-fin-v1.0",
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 50
        }
        
        response = await httpx_client.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"\n=== Response Schema Validation ===")
        
        # Root level fields
        required_fields = ["id", "object", "created", "model", "choices", "usage"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            print(f"✓ {field}: {type(data[field]).__name__}")
        
        # Choices validation
        choice = data["choices"][0]
        choice_fields = ["index", "message", "finish_reason"]
        for field in choice_fields:
            assert field in choice, f"Missing choice field: {field}"
        
        # Message validation
        message = choice["message"]
        message_fields = ["role", "content"]
        for field in message_fields:
            assert field in message, f"Missing message field: {field}"
        
        # Usage validation
        usage = data["usage"]
        usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]
        for field in usage_fields:
            assert field in usage, f"Missing usage field: {field}"
            assert isinstance(usage[field], int), f"{field} should be int"
        
        print("✓ All schema validations passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])







