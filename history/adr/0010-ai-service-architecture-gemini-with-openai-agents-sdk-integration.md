# ADR-0010: AI Service Architecture: Gemini with OpenAI Agents SDK Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-17
- **Feature:** 002-ai-chat-service-integration
- **Context:** Phase III requires conversational AI for natural language task management. Need to select AI service provider, agent orchestration framework, and integration architecture.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - AI service choice affects cost, latency, capabilities
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - GPT-4, Claude, Gemini evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects backend, MCP tools, conversation handling
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Google Gemini** (`gemini-1.5-flash`) as the AI service provider, integrated through **OpenAI Agents SDK** via a custom adapter pattern.

**Components**:
- **AI Service**: Google Gemini API (`google-generativeai` Python package)
- **Model**: `gemini-1.5-flash` for <5s p95 response time
- **Agent Framework**: OpenAI Agents SDK (`openai` Python package)
- **Integration Pattern**: Custom Gemini adapter wrapping Gemini API in OpenAI-compatible interface
- **Tool Invocation**: OpenAI Agents SDK handles MCP tool calling based on Gemini responses
- **Conversation State**: Database-backed (no in-memory state)

## Consequences

### Positive

- **User Requirement**: Explicit user specification for Gemini in clarifications
- **Cost Efficiency**: Gemini pricing competitive for conversational AI workloads
- **Performance**: `gemini-1.5-flash` meets <5s p95 latency requirement
- **Constitutional Compliance**: OpenAI Agents SDK mandated by Phase III constitution (Principle XII)
- **Tool Calling**: OpenAI Agents SDK provides standardized tool invocation for MCP tools
- **Stateless Design**: Agent SDK enables database-backed conversation context
- **Flexibility**: Adapter pattern allows swapping AI providers without rewriting tool logic

### Negative

- **Integration Complexity**: Custom adapter required to bridge Gemini and OpenAI Agents SDK
- **Testing Overhead**: Adapter layer needs unit and integration tests
- **Documentation Gap**: Less documented than native OpenAI SDK usage
- **API Differences**: Gemini and OpenAI APIs have different response formats requiring translation
- **Vendor Lock-in**: Limited (adapter pattern mitigates), but switching providers requires adapter rewrite

## Alternatives Considered

**Alternative 1: OpenAI GPT-4 with Native SDK**
- **Pros**: Native OpenAI Agents SDK integration, excellent NLU, well-documented
- **Cons**: Higher cost per request, ruled out by user specification
- **Rejected Because**: User explicitly specified Gemini; cost concerns

**Alternative 2: Anthropic Claude with Custom Integration**
- **Pros**: Strong reasoning capabilities, good for complex task intent detection
- **Cons**: Not specified by user requirements, requires custom agent implementation
- **Rejected Because**: Not in user requirements; no constitutional mandate

**Alternative 3: Local Models (Llama, Mistral)**
- **Pros**: Lower operational cost, data privacy, no API rate limits
- **Cons**: Insufficient quality for intent detection, higher infrastructure cost, slower inference
- **Rejected Because**: Cannot meet <5s p95 latency and accuracy requirements

**Alternative 4: Gemini with Custom Agent Framework**
- **Pros**: Simpler integration, no adapter layer
- **Cons**: Violates Phase III constitution requiring OpenAI Agents SDK, would need to implement tool calling from scratch
- **Rejected Because**: Constitutional mandate for OpenAI Agents SDK (Principle XII)

## References

- Feature Spec: `specs/sphaseIII/002-ai-chat-service-integration/spec.md`
- Research Document: `specs/sphaseIII/002-ai-chat-service-integration/research.md` (Section 1, 2)
- Implementation Plan: `specs/sphaseIII/002-ai-chat-service-integration/plan.md`
- Constitution: `.specify/memory/constitution.md` (Principle XII: OpenAI Agents SDK)
- Related ADRs: ADR-0011 (MCP Server Architecture), ADR-0012 (Phase III Technology Stack)
