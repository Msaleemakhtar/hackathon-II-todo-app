# Modern Todo Application

A full-stack, production-ready task management application showcasing Spec-Driven Development (SDD) principles and modern technologies.

## Project Overview

This repository contains a comprehensive todo application developed in multiple phases, demonstrating progressive development approaches and architectural decisions following Spec-Driven Development principles.

## Quick Links

- **[Phase III Documentation](phaseIII/)** - AI-powered task management setup
- **[Phase IV Documentation](phaseIV/README.md)** - Kubernetes deployment guide
- **[Kubernetes Guide](phaseIV/kubernetes/docs/KUBERNETES_GUIDE.md)** - Complete K8s deployment instructions
- **[Operational Runbook](phaseIV/kubernetes/docs/RUNBOOK.md)** - Troubleshooting and operations
- **[Constitution](.specify/memory/constitution.md)** - Project governance and architectural principles
- **[Architecture Decisions](history/adr/)** - ADR records for significant decisions

## Completed Phases

### Phase I - Command-Line Todo Application
A feature-rich command-line todo application built with Python 3.13 following Test-Driven Development (TDD) principles and Spec-Driven Development methodology. Key features include:
- Task management (add, view, update, delete, mark complete)
- Input validation with clear error messages
- In-memory storage with sequential IDs
- Rich console UI with formatted tables
- Comprehensive test coverage (100% on core business logic)

### Phase II - Full-Stack Web Application
A modern full-stack todo application built with Next.js 16, FastAPI, and PostgreSQL. Features include:
- Next.js 16 frontend with React 19 and TypeScript
- FastAPI backend with SQLModel ORM
- PostgreSQL database with proper migrations
- Better Auth integration for authentication
- Responsive UI with Tailwind CSS and shadcn/ui
- Real-time updates and PWA capabilities
- Complete API with JWT validation

### Phase III - AI-Powered Task Management
Integration of AI capabilities through Model Context Protocol (MCP) and OpenAI Agents SDK. Features include:
- MCP server implementation with 5 stateless tools (add, list, complete, delete, update)
- OpenAI Agents SDK integration for conversational AI
- ChatKit frontend for natural language task management
- Database-backed state with separate Phase III tables
- Better Auth + JWT authentication integration
- Stateless, horizontally scalable architecture
- Complete data isolation per user

### Phase IV - Kubernetes Production Deployment
Production-ready Kubernetes deployment with enterprise-grade infrastructure. Features include:
- Kubernetes orchestration with Helm 3.13+ charts
- HTTPS with Nginx Ingress Controller
- Horizontal Pod Autoscaling (HPA) based on CPU/memory metrics
- Redis StatefulSet for session caching with persistent storage
- Neon Serverless PostgreSQL integration
- Minikube local development environment
- Health checks and liveness/readiness probes
- Resource management with Burstable QoS
- Sequential rollout deployment strategy
- Comprehensive operational runbooks

## Architecture & Technologies

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, OpenAI ChatKit
- **Backend**: FastAPI, Python 3.11+, SQLModel, Neon Serverless PostgreSQL
- **AI Integration**: Model Context Protocol (MCP), OpenAI Agents SDK
- **Authentication**: Better Auth with JWT validation
- **Infrastructure**: Kubernetes, Helm 3.13+, Docker, Nginx Ingress
- **Caching**: Redis (StatefulSet with persistent volumes)
- **Package Managers**: UV (Python), Bun (JavaScript)
- **Development Methodology**: Spec-Driven Development (SDD)
- **Deployment**: Minikube (local), Horizontal Pod Autoscaling (HPA)

## Contributing

This project follows Spec-Driven Development (SDD) principles. All contributions must adhere to the constitutional governance rules defined in `.specify/memory/constitution.md`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.