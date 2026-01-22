# Open Response Standard Implementation Plan

## Overview

This document outlines the implementation plan for vLLM's **Open Response Standard** in the `simple-llm-pro-finance` project. The Open Response Standard provides enhanced token tracking and comprehensive streaming events for better observability and client integration.

## What is the Open Response Standard?

The Open Response Standard is vLLM's enhanced OpenAI-compatible response protocol that includes:

### 1. Enhanced Token Tracking

**InputTokensDetails** (`vllm.entrypoints.openai.responses.protocol`):
- `cached_tokens` (int): Number of cached tokens
- `input_tokens_per_turn` (list[int]): Input tokens broken down per turn
- `cached_tokens_per_turn` (list[int]): Cached tokens broken down per turn

**OutputTokensDetails**:
- `reasoning_tokens` (int): Tokens used for reasoning
- `tool_output_tokens` (int): Tokens from tool outputs
- `output_tokens_per_turn` (list[int]): Output tokens broken down per turn
- `tool_output_tokens_per_turn` (list[int]): Tool output tokens broken down per turn

### 2. Streaming Response Events

Comprehensive event system for real-time streaming:
- `ResponseCreatedEvent` - Response lifecycle start
- `ResponseInProgressEvent` - Intermediate progress updates
- `ResponseCompletedEvent` - Response lifecycle end
- `ResponseContentPartAddedEvent` / `ResponseContentPartDoneEvent` - Content parts
- `ResponseReasoningTextDeltaEvent` / `ResponseReasoningTextDoneEvent` - Reasoning content
- Tool events (code interpreter, web search, MCP calls)

## Current State

- **vLLM Version**: 0.13.0 (as per README.md)
- **Base Image**: `vllm/vllm-openai:latest`
- **API Server**: `vllm.entrypoints.openai.api_server`
- **Tool Calling**: Enabled with `hermes` parser

## Implementation Tasks

### 1. Verify vLLM Version Support

Check if vLLM 0.13.0+ supports the Open Response Standard:
- [ ] Review vLLM changelog for open response standard introduction
- [ ] Check if `vllm.entrypoints.openai.responses.protocol` module exists
- [ ] Verify `InputTokensDetails` and `OutputTokensDetails` are available

### 2. Update vLLM Version (if needed)

If the current version doesn't support open responses:
- [ ] Update Dockerfile base image to latest vLLM version
- [ ] Test compatibility with existing deployment
- [ ] Update README.md with new version

### 3. Enable Open Response Standard

Configure vLLM to use enhanced response format:
- [ ] Review `start-vllm.sh` for any response format flags
- [ ] Add configuration for enhanced token tracking
- [ ] Enable streaming events if not already enabled

### 4. Update Documentation

- [ ] Document new token tracking capabilities
- [ ] Add examples of enhanced response format
- [ ] Update API documentation with new fields

### 5. Testing

- [ ] Test enhanced token tracking in responses
- [ ] Verify streaming events are properly emitted
- [ ] Test with existing clients for backward compatibility
- [ ] Integration tests for new response format

## References

- [vLLM Open Response Protocol Docs](https://docs.vllm.ai/en/latest/api/vllm/entrypoints/openai/responses/protocol/)
- [vLLM GitHub Repository](https://github.com/vllm-project/vllm)
- [OpenAI API Compatibility](https://docs.vllm.ai/en/latest/getting_started/examples/openai_chat_completion_structured_outputs.html)

## Next Steps

1. Review vLLM repository for latest open response standard implementation
2. Check current vLLM version in Docker image
3. Test response format with sample requests
4. Update client project (`open-finance-pydanticAI`) to consume enhanced responses
