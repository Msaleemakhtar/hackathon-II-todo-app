# Architecture Diagram - Todo App Phase IV

> **Comprehensive system architecture for Kubernetes deployment with HTTPS/TLS**
>
> Complete visual reference for the AI Task Assistant infrastructure

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [TLS/HTTPS Architecture](#tlshttps-architecture)
3. [Component Details](#component-details)
4. [Network Flow](#network-flow)
5. [Data Flow](#data-flow)
6. [Scaling Behavior](#scaling-behavior)
7. [Storage Architecture](#storage-architecture)
8. [Security Architecture](#security-architecture)
9. [Resource Quotas](#resource-quotas)
10. [Monitoring Points](#monitoring-points)
11. [High Availability](#high-availability-considerations)
12. [Disaster Recovery](#disaster-recovery)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Internet / User                             │
│                           (Browser/Client)                               │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTPS Request (Port 443)
                                 │ https://todo-app.local/*
                                 │ TLS 1.2/1.3 Encrypted
                                 │
┌─────────────────────────────────────────────────────────────────────────┐
│                            Minikube Cluster                              │
│                          (Kubernetes v1.28+)                             │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    Nginx Ingress Controller                     │    │
│  │                    (ingress-nginx namespace)                    │    │
│  │                                                                 │    │
│  │  • TLS Termination (HTTPS → HTTP)                              │    │
│  │  • Certificate: todo-app-tls secret                            │    │
│  │  • Path-based routing                                          │    │
│  │  • Load balancing                                              │    │
│  └──────────────────────┬───────────────────┬─────────────────────┘    │
│                         │                   │                           │
│                         │ /api/*            │ /, /chat, /login          │
│                         │ (HTTP internal)   │ (HTTP internal)           │
│                         │                   │                           │
│  ┌──────────────────────▼──────┐   ┌───────▼──────────────────┐       │
│  │  Backend Service             │   │ Frontend Service          │       │
│  │  (ClusterIP)                 │   │ (ClusterIP)               │       │
│  │  Port: 8000                  │   │ Port: 3000                │       │
│  │  DNS: backend-service        │   │ DNS: frontend-service     │       │
│  └──────────────┬───────────────┘   └──────────┬────────────────┘      │
│                 │                               │                        │
│  ┌──────────────▼───────────────┐   ┌──────────▼─────────────────┐    │
│  │   Backend Deployment         │   │  Frontend Deployment        │    │
│  │   (HPA: 2-5 replicas)        │   │  (HPA: 2-5 replicas)        │    │
│  │   ┌─────────┐  ┌─────────┐  │   │  ┌─────────┐  ┌─────────┐  │    │
│  │   │ Pod 1   │  │ Pod 2   │  │   │  │ Pod 1   │  │ Pod 2   │  │    │
│  │   │ Backend │  │ Backend │  │   │  │Frontend │  │Frontend │  │    │
│  │   │ FastAPI │  │ FastAPI │  │   │  │Next.js  │  │Next.js  │  │    │
│  │   │ChatKit  │  │ChatKit  │  │   │  │ChatKit  │  │ChatKit  │  │    │
│  │   │JWT Auth │  │JWT Auth │  │   │  │UI       │  │UI       │  │    │
│  │   │500m CPU │  │500m CPU │  │   │  │500m CPU │  │500m CPU │  │    │
│  │   │512Mi RAM│  │512Mi RAM│  │   │  │512Mi RAM│  │512Mi RAM│  │    │
│  │   └────┬────┘  └────┬────┘  │   │  └─────────┘  └─────────┘  │    │
│  │        │            │        │   │                             │    │
│  │   Min: 2, Max: 5            │   │   Min: 2, Max: 5           │    │
│  │   CPU: 70%, Memory: 80%     │   │   CPU: 70%                 │    │
│  └──────┬───────────┬───────────┘   └─────────────────────────────┘    │
│         │           │                                                    │
│         │           └────────────────┐                                  │
│         │                            │                                  │
│  ┌──────▼────────────────────────────▼──────┐                          │
│  │        MCP Service (ClusterIP)           │                          │
│  │              Port: 8001                  │                          │
│  │        DNS: mcp-service                  │                          │
│  └─────────────────┬────────────────────────┘                          │
│                    │                                                    │
│  ┌─────────────────▼────────────────────────┐                          │
│  │         MCP Server Deployment            │                          │
│  │         ┌─────────────────────┐          │                          │
│  │         │ Pod 1               │          │                          │
│  │         │ MCP Server          │          │                          │
│  │         │ FastMCP             │          │                          │
│  │         │ Task Tools          │          │                          │
│  │         │ 250m CPU            │          │                          │
│  │         │ 256Mi RAM           │          │                          │
│  │         └──────┬──────────────┘          │                          │
│  │         Fixed: 1 replica                 │                          │
│  └────────────────┼──────────────────────────┘                          │
│                   │                                                     │
│                   │                                                     │
│  ┌────────────────▼──────────────────────────────────────────────────┐ │
│  │               Redis Service (ClusterIP)                           │ │
│  │                    Port: 6379                                     │ │
│  │               DNS: redis-service                                  │ │
│  └──────────────────────┬────────────────────────────────────────────┘ │
│                         │                                              │
│  ┌──────────────────────▼──────────────────────────────────────────┐  │
│  │              Redis StatefulSet                                   │  │
│  │              ┌───────────────────────┐                           │  │
│  │              │ redis-0               │                           │  │
│  │              │ Redis 7-alpine        │                           │  │
│  │              │ RDB Persistence       │                           │  │
│  │              │ 250m CPU              │                           │  │
│  │              │ 256Mi RAM             │                           │  │
│  │              └──────────┬────────────┘                           │  │
│  │                         │                                         │  │
│  │              ┌──────────▼────────────┐                           │  │
│  │              │ PersistentVolumeClaim │                           │  │
│  │              │ redis-data-redis-0    │                           │  │
│  │              │ Size: 1Gi             │                           │  │
│  │              │ StorageClass: standard│                           │  │
│  │              │ Access: ReadWriteOnce │                           │  │
│  │              └───────────────────────┘                           │  │
│  │              Fixed: 1 replica                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    ConfigMap & Secrets                            │ │
│  │                                                                   │ │
│  │  ConfigMap: todo-app-config (Non-sensitive)                      │ │
│  │  ├─ REDIS_HOST: redis-service                                    │ │
│  │  ├─ REDIS_PORT: "6379"                                           │ │
│  │  ├─ MCP_SERVER_URL: http://mcp-service:8001                      │ │
│  │  ├─ NEXT_PUBLIC_API_URL: https://todo-app.local/api              │ │
│  │  ├─ NEXT_PUBLIC_BETTER_AUTH_URL: https://todo-app.local          │ │
│  │  ├─ NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: domain_pk_...               │ │
│  │  └─ CORS_ORIGINS: ["https://todo-app.local", ...]               │ │
│  │                                                                   │ │
│  │  Secret: todo-app-secrets (Sensitive - base64)                   │ │
│  │  ├─ DATABASE_URL: postgresql://... (Neon)                        │ │
│  │  ├─ OPENAI_API_KEY: sk-...                                       │ │
│  │  └─ BETTER_AUTH_SECRET: (32-byte random)                         │ │
│  │                                                                   │ │
│  │  Secret: todo-app-tls (TLS Certificate)                          │ │
│  │  ├─ tls.crt: (X.509 certificate)                                 │ │
│  │  └─ tls.key: (RSA 2048-bit private key)                          │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               │ PostgreSQL Protocol (TLS)
                               │ Port: 5432
                               │
┌──────────────────────────────▼───────────────────────────────────────────┐
│                   External Neon PostgreSQL Database                      │
│                   (Serverless PostgreSQL - Cloud)                        │
│                   Region: us-east-1                                      │
│                                                                           │
│                   Tables:                                                │
│                   ├─ users (Better Auth)                                 │
│                   ├─ sessions (Better Auth)                              │
│                   ├─ accounts (Better Auth)                              │
│                   ├─ tasks (Task data)                                   │
│                   ├─ threads (ChatKit conversations)                     │
│                   └─ messages (ChatKit history)                          │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## TLS/HTTPS Architecture

### Certificate Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                  TLS Certificate Generation & Storage                   │
└────────────────────────────────────────────────────────────────────────┘

1. Certificate Generation (One-time setup):

   $ openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout tls.key \
       -out tls.crt \
       -subj "/CN=todo-app.local/O=TodoApp" \
       -addext "subjectAltName=DNS:todo-app.local,DNS:*.todo-app.local"

   Creates:
   ├─ tls.crt (Public certificate)
   │  ├─ Subject: CN=todo-app.local, O=TodoApp
   │  ├─ Issuer: Self-signed (CN=todo-app.local)
   │  ├─ Validity: 365 days
   │  ├─ Key Type: RSA 2048-bit
   │  └─ SAN: todo-app.local, *.todo-app.local
   │
   └─ tls.key (Private key)
      ├─ Type: RSA PRIVATE KEY
      ├─ Size: 2048 bits
      └─ Encrypted: No (--nodes flag)

2. Kubernetes Secret Creation:

   $ kubectl create secret tls todo-app-tls \
       --cert=tls.crt \
       --key=tls.key \
       -n todo-phaseiv

   Creates:
   ┌─────────────────────────────────────┐
   │   Secret: todo-app-tls              │
   │   Type: kubernetes.io/tls           │
   │   Namespace: todo-phaseiv           │
   │                                     │
   │   Data:                             │
   │   ├─ tls.crt: <base64-cert>        │
   │   └─ tls.key: <base64-key>         │
   └─────────────────────────────────────┘

3. Ingress References Secret:

   apiVersion: networking.k8s.io/v1
   kind: Ingress
   spec:
     tls:
     - hosts:
       - todo-app.local
       secretName: todo-app-tls  # References the secret
```

### TLS Handshake Flow (Detailed)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        HTTPS Request Lifecycle                           │
└──────────────────────────────────────────────────────────────────────────┘

Step 1: DNS Resolution
──────────────────────
Browser: "Resolve todo-app.local"
   ↓
/etc/hosts: "todo-app.local → 192.168.49.2 (Minikube IP)"
   ↓
Browser: "Connect to 192.168.49.2:443"


Step 2: TCP Handshake (Port 443)
──────────────────────────────────
Browser                          Ingress Controller
   │                                    │
   ├─── SYN ──────────────────────────→│
   │                                    │
   │←─── SYN-ACK ──────────────────────┤
   │                                    │
   ├─── ACK ──────────────────────────→│
   │                                    │
   └─── TCP Connection Established ────┘


Step 3: TLS Handshake (TLS 1.2/1.3)
────────────────────────────────────
Browser                          Nginx Ingress
   │                                    │
   ├─── ClientHello ─────────────────→ │
   │    • TLS versions: 1.2, 1.3       │
   │    • Cipher suites offered        │
   │    • Random nonce                 │
   │    • SNI: todo-app.local          │
   │                                    │
   │                    Ingress reads:  │
   │                    • SNI = todo-app.local
   │                    • Loads todo-app-tls secret
   │                    • Decodes tls.crt & tls.key
   │                                    │
   │←─── ServerHello ──────────────────┤
   │    • Chosen TLS version: 1.3      │
   │    • Chosen cipher: TLS_AES_256...│
   │    • Server random nonce          │
   │                                    │
   │←─── Certificate ──────────────────┤
   │    • Subject: CN=todo-app.local   │
   │    • Issuer: CN=todo-app.local    │
   │    • Public Key: RSA 2048-bit     │
   │    • Validity: 365 days           │
   │    • SAN: todo-app.local          │
   │                                    │
   │←─── ServerKeyExchange ────────────┤
   │    • Diffie-Hellman params        │
   │    • Signed with server's private │
   │      key (from tls.key)           │
   │                                    │
   │←─── ServerHelloDone ──────────────┤
   │                                    │
   Browser validates certificate:      │
   • CN matches todo-app.local? ✅     │
   • Valid date range? ✅              │
   • Trusted issuer? ❌ Self-signed!   │
   │                                    │
   ┌──────────────────────────────┐    │
   │   ⚠️  Browser Warning:       │    │
   │   "This certificate is       │    │
   │    not trusted"              │    │
   │                              │    │
   │   Options:                   │    │
   │   [×] Cancel                 │    │
   │   [✓] Accept Risk & Continue │    │
   │   [?] View Certificate       │    │
   └──────────────────────────────┘    │
   │                                    │
   User accepts risk (dev environment) │
   │                                    │
   ├─── ClientKeyExchange ────────────→│
   │    • Pre-master secret            │
   │      (encrypted with server's     │
   │       public key from cert)       │
   │                                    │
   │                    Ingress:       │
   │                    • Decrypts with tls.key
   │                    • Derives session keys
   │                                    │
   ├─── ChangeCipherSpec ─────────────→│
   │                                    │
   ├─── Finished ─────────────────────→│
   │    • Encrypted with session key   │
   │                                    │
   │←─── ChangeCipherSpec ─────────────┤
   │                                    │
   │←─── Finished ─────────────────────┤
   │    • Encrypted with session key   │
   │                                    │
   └─── TLS Session Established ───────┘
        Cipher: TLS_AES_256_GCM_SHA384
        Key Exchange: ECDHE
        Authentication: RSA


Step 4: Encrypted HTTP Request
───────────────────────────────
Browser                          Nginx Ingress
   │                                    │
   ├─── Encrypted HTTP Request ───────→│
   │    GET /chat HTTP/1.1              │
   │    Host: todo-app.local            │
   │    (all encrypted with session key)│
   │                                    │
   │              Ingress:              │
   │              • Decrypts request    │
   │              • Sees: GET /chat     │
   │              • Matches path: /(.*)│
   │              • Routes to: frontend-service:3000
   │              • Forwards: http://frontend-service:3000/chat
   │              (Plain HTTP internally!)
   │                                    │
   │         ┌────────────────────┐     │
   │         │  Internal Cluster  │     │
   │         │  (Plain HTTP)      │     │
   │         │                    │     │
   │         │  Frontend Service  │     │
   │         │     ↓              │     │
   │         │  Frontend Pod      │     │
   │         │     ↓              │     │
   │         │  Next.js processes │     │
   │         │     ↓              │     │
   │         │  Returns HTML      │     │
   │         └────────────────────┘     │
   │                                    │
   │              Ingress:              │
   │              • Receives HTTP response
   │              • Encrypts with session key
   │                                    │
   │←─── Encrypted HTTP Response ──────┤
   │    HTTP/1.1 200 OK                 │
   │    Content-Type: text/html         │
   │    (all encrypted with session key)│
   │                                    │
   Browser:                             │
   • Decrypts response                  │
   • Renders HTML                       │
   • Shows 🔒 in address bar            │


Step 5: Subsequent Requests (Session Reuse)
────────────────────────────────────────────
Browser                          Nginx Ingress
   │                                    │
   ├─── TLS Session ID ───────────────→│
   │    (Resume previous session)       │
   │                                    │
   │              Ingress:              │
   │              • Recognizes session ID
   │              • Reuses session keys
   │              • Skips full handshake
   │                                    │
   │←─── Session Resumed ───────────────┤
   │                                    │
   └─── Faster! (No handshake) ────────┘
        Saved ~100ms per request
```

### Why HTTPS is Required

```
┌────────────────────────────────────────────────────────────────────┐
│              HTTPS Requirements for ChatKit                         │
└────────────────────────────────────────────────────────────────────┘

1. Secure Context API Requirement:
   ───────────────────────────────
   ChatKit SDK uses: crypto.randomUUID()
   
   Browser Policy:
   ├─ Secure contexts ONLY:
   │  ├─ https://* ✅
   │  ├─ http://localhost ✅
   │  ├─ http://127.0.0.1 ✅
   │  └─ http://<anything-else> ❌
   │
   └─ http://todo-app.local ❌ (NOT a secure context!)
   
   Solution: Deploy with HTTPS → Ingress with TLS


2. JWT Token Protection:
   ──────────────────────
   Without HTTPS:
   ┌─────────────────────────────────────┐
   │  Authorization: Bearer eyJhbGc...  │ ← Plain text!
   │  (Anyone on network can intercept) │
   └─────────────────────────────────────┘
   
   With HTTPS:
   ┌─────────────────────────────────────┐
   │  ✓ Encrypted TLS tunnel            │
   │  ✓ Token invisible to network       │
   │  ✓ Man-in-middle attack prevented   │
   └─────────────────────────────────────┘


3. Session Cookie Security:
   ────────────────────────
   Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Strict
                               ↑
                    Only sent over HTTPS
   
   Without "Secure" flag:
   ├─ Cookie sent over HTTP → Interceptable
   └─ Session hijacking risk
   
   With "Secure" flag + HTTPS:
   ├─ Cookie encrypted in transit
   └─ Session protected


4. Browser Security Policies:
   ───────────────────────────
   Modern browsers enforce:
   ├─ Mixed content blocking (HTTPS page can't load HTTP resources)
   ├─ Secure context requirements (crypto APIs, service workers)
   ├─ Cookie security (Secure flag)
   └─ CORS preflight (stricter for HTTP)
```

### Certificate Trust Flow

```
┌──────────────────────────────────────────────────────────────────┐
│           Browser Certificate Validation Process                 │
└──────────────────────────────────────────────────────────────────┘

Production (Let's Encrypt):
──────────────────────────
1. Browser receives certificate
2. Checks certificate chain:
   ┌─────────────────────────────────┐
   │  todo-app.com certificate       │
   │  ↓ Signed by                    │
   │  Let's Encrypt Intermediate CA  │
   │  ↓ Signed by                    │
   │  ISRG Root X1 (in browser store)│
   └─────────────────────────────────┘
3. Root CA trusted? ✅
4. Certificate valid? ✅
5. Domain matches? ✅
6. Show 🔒 (Secure)


Development (Self-Signed):
──────────────────────────
1. Browser receives certificate
2. Checks certificate chain:
   ┌─────────────────────────────────┐
   │  todo-app.local certificate     │
   │  ↓ Signed by                    │
   │  todo-app.local (self-signed)   │
   │  ↓ NOT in browser store         │
   │  ❌ Untrusted root               │
   └─────────────────────────────────┘
3. Root CA trusted? ❌
4. Shows warning: "Not Secure"
5. User must manually accept risk


Manual Trust (Development Workaround):
───────────────────────────────────────
Chrome/Edge (Linux):
$ sudo cp tls.crt /usr/local/share/ca-certificates/todo-app.crt
$ sudo update-ca-certificates
$ # Restart browser
→ Certificate now trusted ✅

Firefox:
1. Open: https://todo-app.local
2. Click "Advanced"
3. Click "Accept the Risk and Continue"
4. Firefox remembers exception ✅

Chrome (Quick bypass):
1. Open: https://todo-app.local
2. Click anywhere on page
3. Type: thisisunsafe
4. Page loads ✅ (temporary)
```

### TLS Configuration (Ingress)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: todo-phaseiv
  annotations:
    # Force HTTPS redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    
    # TLS configuration
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"
    nginx.ingress.kubernetes.io/ssl-ciphers: "HIGH:!aNULL:!MD5"
    
    # HSTS (HTTP Strict Transport Security)
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "Strict-Transport-Security: max-age=31536000; includeSubDomains";
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo-app.local
    secretName: todo-app-tls  # References the TLS secret
  rules:
  - host: todo-app.local
    http:
      paths:
      # Backend API (except /api/auth)
      - path: /api/(?!auth)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      # Frontend (all other paths)
      - path: /(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
```

### Security Headers (HTTPS)

```
Response Headers Added by Ingress:
───────────────────────────────────
Strict-Transport-Security: max-age=31536000; includeSubDomains
  └─ Tells browser: "Only use HTTPS for 1 year"

X-Content-Type-Options: nosniff
  └─ Prevents MIME-type sniffing attacks

X-Frame-Options: SAMEORIGIN
  └─ Prevents clickjacking attacks

X-XSS-Protection: 1; mode=block
  └─ Enables browser XSS filter
```

---

## Component Details

### Ingress Layer

**Nginx Ingress Controller**
- **Purpose**: HTTPS termination, HTTP routing, load balancing
- **Namespace**: `ingress-nginx`
- **Configuration**:
  - Host: `todo-app.local`
  - TLS: Enabled (todo-app-tls secret)
  - Protocols: TLS 1.2, TLS 1.3
  - Path-based routing:
    - `/api/(?!auth)(.*)` → Backend Service (port 8000)
    - `/(.*)` → Frontend Service (port 3000)
  - SSL Redirect: Enabled (HTTP → HTTPS)
  - HSTS: Enabled (max-age 1 year)

### Application Layer

#### Frontend (Next.js 16)
- **Technology**: Next.js 16, React 19, TypeScript
- **Features**: 
  - ChatKit UI component (OpenAI)
  - Better Auth client
  - Server-side rendering
  - Static asset serving
- **Replicas**: 2-5 (managed by HPA)
- **Resources**:
  - CPU: 500m request, 1000m limit
  - Memory: 512Mi request, 1024Mi limit
- **Scaling**:
  - Metric: CPU utilization
  - Target: 70%
  - Scale-up: 2 minutes under load
  - Scale-down: 5 minutes after load decreases
- **Health Probes**:
  - Liveness: `GET /api/health` (10s delay, 10s period, 3 failures)
  - Readiness: `GET /api/health` (5s delay, 10s period, 3 failures)
  - Startup: `GET /api/health` (0s delay, 10s period, 30 failures)
- **Environment**:
  - `NEXT_PUBLIC_API_URL`: https://todo-app.local/api
  - `NEXT_PUBLIC_BETTER_AUTH_URL`: https://todo-app.local
  - `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`: (from ConfigMap)

#### Backend (FastAPI + Python)
- **Technology**: FastAPI 0.104+, Python 3.11+, ChatKit SDK
- **Features**:
  - ChatKit SDK adapter (stateless HTTP)
  - JWT authentication (Better Auth)
  - Rate limiting (10 req/min per user)
  - Input sanitization
  - MCP tool orchestration
  - Session caching (Redis)
- **Replicas**: 2-5 (managed by HPA)
- **Resources**:
  - CPU: 500m request, 1000m limit
  - Memory: 512Mi request, 1024Mi limit
- **Scaling**:
  - Metrics: CPU (70%), Memory (80%)
  - Scale-up: 2 minutes
  - Scale-down: 5 minutes
- **Health Probes**:
  - Liveness: `GET /health` (10s delay, 10s period)
  - Readiness: `GET /health` (5s delay, 10s period)
  - Startup: `GET /health` (0s delay, 10s period, 30 failures)
- **Dependencies**:
  - MCP Server (http://mcp-service:8001)
  - Redis (redis-service:6379)
  - PostgreSQL (Neon, external)

#### MCP Server (FastMCP)
- **Technology**: FastMCP (Model Context Protocol), Python 3.11+
- **Features**:
  - Task management tools (add_task, list_tasks, update_task, delete_task)
  - User context validation
  - Direct PostgreSQL access
  - Stateless HTTP transport
- **Replicas**: 1 (fixed)
- **Resources**:
  - CPU: 250m request, 500m limit
  - Memory: 256Mi request, 512Mi limit
- **Health Probes**:
  - Liveness: `GET /mcp` (10s delay, 10s period)
  - Readiness: `GET /mcp` (5s delay, 10s period)
- **Security**:
  - DNS rebinding protection
  - Allowed hosts: localhost, mcp-server, Kubernetes DNS
  - User context required for all tools

### Data Layer

#### Redis (Session Cache)
- **Type**: StatefulSet (stable network identity)
- **Image**: redis:7-alpine
- **Replicas**: 1 (fixed)
- **Resources**:
  - CPU: 250m request, 500m limit
  - Memory: 256Mi request, 512Mi limit
- **Persistence**:
  - Volume: 1Gi PersistentVolumeClaim
  - StorageClass: standard (Minikube hostPath)
  - Access Mode: ReadWriteOnce
  - Data Format: RDB (snapshot on shutdown + periodic)
  - Save Policy: save 900 1, save 300 10, save 60 10000
- **Health Probes**:
  - Liveness: `redis-cli ping` (10s delay, 10s period)
  - Readiness: `redis-cli ping` (5s delay, 10s period)
- **Configuration**:
  - maxmemory-policy: allkeys-lru
  - appendonly: no (RDB only for dev)
- **Data Stored**:
  - Session tokens (TTL: 1 hour)
  - User context cache
  - Rate limit counters

#### PostgreSQL (Neon Serverless)
- **Provider**: Neon Serverless PostgreSQL
- **Connection**: TLS-encrypted (sslmode=require)
- **Shared**: Same database instance as Phase III
- **Region**: us-east-1 (or configured region)
- **Features**:
  - Auto-scaling compute
  - Automatic backups (point-in-time recovery)
  - Branch databases for testing
- **Tables**:
  - `users` - User accounts (Better Auth)
  - `sessions` - Active sessions (Better Auth)
  - `accounts` - OAuth accounts (Better Auth)
  - `tasks` - Task data (user-isolated)
  - `threads` - ChatKit conversation threads
  - `messages` - ChatKit message history
- **Access**:
  - Backend: Full access (via DATABASE_URL secret)
  - MCP Server: Full access (same DATABASE_URL)
  - Connection pooling: Managed by Neon

---

## Network Flow

### User Request Flow (HTTPS)

```
1. Browser → HTTPS Request
   GET https://todo-app.local/chat
   
2. DNS Resolution
   /etc/hosts → todo-app.local → 192.168.49.2 (Minikube IP)
   
3. TLS Handshake
   ├─ Browser → ClientHello
   ├─ Ingress → ServerHello + Certificate (todo-app-tls)
   ├─ Browser validates certificate (self-signed warning)
   ├─ User accepts risk
   └─ TLS session established
   
4. Encrypted HTTP Request
   Browser → Ingress (HTTPS)
   
5. Ingress TLS Termination
   ├─ Decrypts HTTPS → HTTP
   ├─ Matches path "/chat" to: path: /(.*)
   └─ Routes to: http://frontend-service:3000/chat
   
6. Frontend Service (ClusterIP)
   ├─ Load balances to: frontend-pod-1 or frontend-pod-2
   └─ Forwards to: http://<pod-ip>:3000/chat
   
7. Frontend Pod (Next.js)
   ├─ Server-side renders page
   ├─ Fetches user session
   ├─ Includes ChatKit SDK
   └─ Returns HTML
   
8. Response Flow (Reverse)
   Frontend Pod → Service → Ingress
   
9. Ingress Encrypts Response
   ├─ Encrypts HTTP → HTTPS
   └─ Sends to browser
   
10. Browser
    ├─ Decrypts response
    ├─ Renders HTML
    └─ Shows 🔒 (HTTPS active)
```

### Internal Service Communication (HTTP)

```
All internal communication uses plain HTTP (cluster network is trusted):

Frontend Pod → Backend Service
  http://backend-service.todo-phaseiv.svc.cluster.local:8000
  └─ POST /chatkit (with JWT in Authorization header)

Backend Pod → MCP Service
  http://mcp-service.todo-phaseiv.svc.cluster.local:8001
  └─ POST /mcp (MCP protocol)

Backend Pod → Redis Service
  redis://redis-service.todo-phaseiv.svc.cluster.local:6379
  └─ GET/SET/EXPIRE commands (Redis protocol)

Backend Pod → Neon PostgreSQL
  postgresql://<host>.neon.tech:5432/db?sslmode=require
  └─ TLS-encrypted connection (external network)

MCP Pod → Neon PostgreSQL
  postgresql://<host>.neon.tech:5432/db?sslmode=require
  └─ TLS-encrypted connection (same DATABASE_URL)
```

### DNS Resolution (Kubernetes)

```
Service Discovery via Kubernetes DNS:
─────────────────────────────────────
Short name (same namespace):
  backend-service → 10.96.123.45 (ClusterIP)

FQDN (cross-namespace):
  backend-service.todo-phaseiv.svc.cluster.local → 10.96.123.45

External name:
  <db-host>.neon.tech → <external-ip> (via external DNS)
```

---

## Data Flow

### Complete Chat Message Flow (with TLS)

```
┌────────────────────────────────────────────────────────────────┐
│  User: "Show me my pending tasks"                              │
└────────────────────────────────────────────────────────────────┘
                           │
                           ▼
1. ChatKit UI → HTTPS POST
   ┌──────────────────────────────────────────────────────┐
   │ POST https://todo-app.local/api/chatkit              │
   │ Headers:                                             │
   │   Authorization: Bearer eyJhbGc...                   │
   │   Content-Type: application/json                     │
   │ Body:                                                │
   │   {"type": "chat.create_message", ...}               │
   │ (All encrypted with TLS session key)                 │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
2. Ingress TLS Termination
   ┌──────────────────────────────────────────────────────┐
   │ • Decrypts HTTPS → HTTP                              │
   │ • Extracts: POST /api/chatkit                        │
   │ • Matches: /api/(?!auth)(.*)                         │
   │ • Routes to: backend-service:8000                    │
   │ • Forwards: http://backend-service:8000/chatkit      │
   │   (Plain HTTP - cluster internal)                    │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
3. Backend Service → Backend Pod
   ┌──────────────────────────────────────────────────────┐
   │ • Load balances to: backend-pod-1                    │
   │ • Rate limiting: Check 10 req/min                    │
   │ • JWT validation: Decode & verify                    │
   │ • Extract user_id from JWT                           │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
4. ChatKit SDK Adapter
   ┌──────────────────────────────────────────────────────┐
   │ • Creates context: {"user_id": "user_123"}           │
   │ • Calls: task_server.process(body, context)          │
   │ • Agent analyzes: "Show me my pending tasks"         │
   │ • Intent: LIST_TASKS                                 │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
5. MCP Tool Call
   ┌──────────────────────────────────────────────────────┐
   │ POST http://mcp-service:8001/mcp                     │
   │ Body:                                                │
   │   {                                                  │
   │     "tool": "list_tasks",                            │
   │     "params": {                                      │
   │       "user_id": "user_123",                         │
   │       "status": "pending"                            │
   │     },                                               │
   │     "context": {"user_id": "user_123"}               │
   │   }                                                  │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
6. MCP Server → PostgreSQL
   ┌──────────────────────────────────────────────────────┐
   │ • Validates user_id in context                       │
   │ • Connects: postgresql://<neon>.neon.tech:5432       │
   │   (TLS-encrypted connection)                         │
   │ • Query:                                             │
   │   SELECT id, title, status, created_at               │
   │   FROM tasks                                         │
   │   WHERE user_id = 'user_123'                         │
   │     AND status = 'pending'                           │
   │   ORDER BY created_at DESC                           │
   │ • Returns: [                                         │
   │     {"id": 1, "title": "Buy groceries", ...},        │
   │     {"id": 5, "title": "Call dentist", ...}          │
   │   ]                                                  │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
7. Response → ChatKit SDK → OpenAI
   ┌──────────────────────────────────────────────────────┐
   │ • MCP returns tool result to backend                 │
   │ • ChatKit SDK sends to OpenAI API:                   │
   │   - User message: "Show me my pending tasks"         │
   │   - Tool result: [task list]                         │
   │ • OpenAI generates natural response:                 │
   │   "You have 2 pending tasks:                         │
   │    1. Buy groceries                                  │
   │    2. Call dentist"                                  │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
8. Backend Streams Response (SSE)
   ┌──────────────────────────────────────────────────────┐
   │ HTTP/1.1 200 OK                                      │
   │ Content-Type: text/event-stream                      │
   │ Cache-Control: no-cache                              │
   │                                                      │
   │ data: {"type": "chunk", "content": "You "}           │
   │ data: {"type": "chunk", "content": "have "}          │
   │ data: {"type": "chunk", "content": "2 "}             │
   │ ... (streaming chunks)                               │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
9. Ingress Encrypts & Forwards
   ┌──────────────────────────────────────────────────────┐
   │ • Receives SSE stream from backend                   │
   │ • Encrypts each chunk with TLS session key           │
   │ • Forwards HTTPS to browser                          │
   └──────────────────────────────────────────────────────┘
                           │
                           ▼
10. Browser Receives & Displays
   ┌──────────────────────────────────────────────────────┐
   │ • Decrypts HTTPS stream                              │
   │ • ChatKit UI displays progressively:                 │
   │   "You have 2 pending tasks:                         │
   │    1. Buy groceries                                  │
   │    2. Call dentist"                                  │
   │ • Stores in thread history (localStorage)            │
   └──────────────────────────────────────────────────────┘
```

### Session Caching Flow (Redis)

```
Login → Session Creation:
────────────────────────
1. User submits credentials
   ↓
2. Better Auth validates
   ↓
3. Backend creates session:
   ┌─────────────────────────────────────┐
   │ HMSET session:abc123                │
   │   user_id user_123                  │
   │   email user@example.com            │
   │   exp 1735308000                    │
   │ EXPIRE session:abc123 3600          │
   └─────────────────────────────────────┘
   ↓
4. Backend returns JWT token
   ↓
5. Frontend stores token


Subsequent Requests → Cache Lookup:
───────────────────────────────────
1. Frontend sends request with JWT
   ↓
2. Backend extracts session_id from JWT
   ↓
3. Check Redis cache:
   ┌─────────────────────────────────────┐
   │ GET session:abc123                  │
   │ → {"user_id": "user_123", ...}      │
   └─────────────────────────────────────┘
   ↓
4. Cache Hit? ✅
   └─ Use cached session (fast!)
   
   Cache Miss? ❌
   ├─ Query PostgreSQL
   ├─ Validate session
   └─ Store in Redis for next request
```

---

## Scaling Behavior

### Horizontal Pod Autoscaling (HPA)

```
┌────────────────────────────────────────────────────────────────┐
│                  HPA Scaling Decision Flow                      │
└────────────────────────────────────────────────────────────────┘

Every 15 seconds:

1. Metrics Server collects pod metrics
   ├─ Polls kubelet on each node
   └─ Gets CPU/Memory usage per pod

2. HPA reads metrics
   ├─ Queries Metrics Server API
   └─ Calculates average utilization

3. HPA calculates desired replicas
   ┌──────────────────────────────────────────────────────┐
   │ desired = ceil(current * (current_usage / target))   │
   │                                                      │
   │ Example (Backend):                                   │
   │ current = 2 replicas                                 │
   │ current_usage = 85% CPU                              │
   │ target = 70% CPU                                     │
   │ desired = ceil(2 * (85 / 70)) = ceil(2.43) = 3      │
   └──────────────────────────────────────────────────────┘

4. HPA applies constraints
   ├─ Min replicas: 2
   ├─ Max replicas: 5
   └─ desired = min(max(desired, 2), 5)

5. HPA updates Deployment
   ├─ Scale up immediately (if CPU > target)
   ├─ Scale down with 5-minute stabilization
   └─ kubectl scale deployment/backend --replicas=3


Scaling Timeline:
────────────────
Low Load (40% CPU):
  Replicas: 2 (minimum)

Medium Load (75% CPU):
  t=0s:    Metrics collected (75% CPU)
  t=15s:   HPA calculates: desired=3
  t=30s:   HPA triggers scale-up
  t=45s:   New pod starting
  t=75s:   New pod ready
  t=90s:   Traffic routed to new pod
  Result:  3 replicas, CPU drops to ~50%

High Load (95% CPU):
  t=0s:    3 replicas at 95% CPU
  t=15s:   HPA calculates: desired=5
  t=30s:   HPA triggers scale-up
  t=90s:   2 new pods ready
  Result:  5 replicas (max), CPU ~57%

Load Decreases (30% CPU):
  t=0s:    5 replicas at 30% CPU
  t=15s:   HPA calculates: desired=2
  t=15s:   HPA waits (scale-down delay)
  t=5m:    Still low usage → scale down
  t=5m30s: Pods terminating
  Result:  2 replicas (minimum)
```

### Load Distribution

```
Ingress Load Balancing Algorithm: Round-Robin
─────────────────────────────────────────────
Request 1 → frontend-pod-1
Request 2 → frontend-pod-2
Request 3 → frontend-pod-1
Request 4 → frontend-pod-2
...

Service Load Balancing: iptables (default)
──────────────────────────────────────────
kube-proxy creates iptables rules:
  frontend-service:3000
    ├─ 50% → frontend-pod-1:3000
    └─ 50% → frontend-pod-2:3000

Session Affinity: None (stateless)
──────────────────────────────────
Each request can go to any pod
(session state stored in Redis, not pods)
```

---

## Storage Architecture

### Redis Persistence (StatefulSet)

```
┌────────────────────────────────────────────────────────────────┐
│                  Redis Data Persistence Flow                    │
└────────────────────────────────────────────────────────────────┘

Pod: redis-0
  ├─ Container: redis:7-alpine
  ├─ Volume Mount: /data
  │  └─ Source: PVC (redis-data-redis-0)
  │
  └─ Redis Process
     ├─ Writes to: /data/dump.rdb
     ├─ Save triggers:
     │  ├─ save 900 1 (15 min if ≥1 key changed)
     │  ├─ save 300 10 (5 min if ≥10 keys changed)
     │  └─ save 60 10000 (1 min if ≥10k keys changed)
     └─ On shutdown: Automatic SAVE


PersistentVolumeClaim: redis-data-redis-0
  ├─ Size: 1Gi
  ├─ Access Mode: ReadWriteOnce
  ├─ StorageClass: standard
  └─ Bound to: PersistentVolume (auto-provisioned)


PersistentVolume: (Minikube hostPath)
  ├─ Type: hostPath (local storage)
  ├─ Path: /tmp/hostpath-provisioner/todo-phaseiv/redis-data-redis-0
  └─ Reclaim Policy: Delete


Minikube Host Filesystem:
  /tmp/hostpath-provisioner/
    └─ todo-phaseiv/
       └─ redis-data-redis-0/
          └─ dump.rdb (Redis snapshot)


Pod Restart Scenario:
────────────────────
$ kubectl delete pod redis-0 -n todo-phaseiv

1. Pod deleted
2. StatefulSet creates new redis-0 pod
3. New pod mounts SAME PVC: redis-data-redis-0
4. Redis starts, reads /data/dump.rdb
5. Data restored! ✅

Namespace Delete Scenario:
─────────────────────────
$ kubectl delete namespace todo-phaseiv

1. All pods deleted
2. All PVCs deleted
3. PV reclaim policy: Delete
4. PV deleted
5. Host path data deleted
6. Data lost! ❌

Minikube Delete Scenario:
────────────────────────
$ minikube delete

1. Entire VM deleted
2. All host paths deleted
3. Data lost! ❌
```

### PostgreSQL Persistence (Neon)

```
Neon Serverless PostgreSQL:
──────────────────────────
Provider: Neon (cloud-hosted)
Type: Serverless PostgreSQL
Persistence: Cloud-native storage (always durable)

Features:
├─ Automatic backups (every 24 hours)
├─ Point-in-time recovery (up to 7 days retention)
├─ Branch databases (instant copies for testing)
├─ Auto-scaling compute (scales to zero when idle)
└─ Multi-region replication (optional)

Backup Strategy:
├─ Automatic: Managed by Neon
├─ Manual: pg_dump from backend pod
└─ Restoration: Neon console or API

Connection:
Backend/MCP → TLS connection → Neon (us-east-1)
  └─ DATABASE_URL: postgresql://...?sslmode=require
```

---

## Security Architecture

### Secret Management Flow

```
┌────────────────────────────────────────────────────────────────┐
│              Secret Creation & Distribution                     │
└────────────────────────────────────────────────────────────────┘

1. Developer creates values-local.yaml (gitignored):
   ┌──────────────────────────────────────┐
   │ secrets:                             │
   │   DATABASE_URL: cG9zdGdyZXNxbC8v...  │
   │   OPENAI_API_KEY: c2stcHJvai1...    │
   │   BETTER_AUTH_SECRET: YWJjZGVm...   │
   │ (All base64-encoded)                 │
   └──────────────────────────────────────┘

2. Helm creates Kubernetes Secret:
   $ helm install todo-app ...
   
   ┌──────────────────────────────────────┐
   │ apiVersion: v1                       │
   │ kind: Secret                         │
   │ metadata:                            │
   │   name: todo-app-secrets             │
   │   namespace: todo-phaseiv            │
   │ type: Opaque                         │
   │ data:                                │
   │   DATABASE_URL: (base64)             │
   │   OPENAI_API_KEY: (base64)           │
   │   BETTER_AUTH_SECRET: (base64)       │
   └──────────────────────────────────────┘

3. Pod mounts secret as environment variables:
   ┌──────────────────────────────────────┐
   │ spec:                                │
   │   containers:                        │
   │   - name: backend                    │
   │     env:                             │
   │     - name: DATABASE_URL             │
   │       valueFrom:                     │
   │         secretKeyRef:                │
   │           name: todo-app-secrets     │
   │           key: DATABASE_URL          │
   └──────────────────────────────────────┘

4. Application reads environment variable:
   ┌──────────────────────────────────────┐
   │ # Inside backend pod                 │
   │ $ env | grep DATABASE_URL            │
   │ DATABASE_URL=postgresql://...        │
   │ (Kubernetes decodes base64)          │
   └──────────────────────────────────────┘

Security Properties:
───────────────────
✅ Secrets stored encrypted at rest (etcd)
✅ Secrets transmitted encrypted (TLS)
✅ Secrets only visible to authorized pods
✅ values-local.yaml gitignored (not in repo)
❌ Base64 ≠ encryption (anyone with cluster access can decode)
```

### TLS Secret Management

```
TLS Certificate Lifecycle:
─────────────────────────
1. Generate certificate (one-time):
   $ openssl req -x509 -nodes -days 365 ...
   Creates: tls.crt, tls.key

2. Create Kubernetes secret:
   $ kubectl create secret tls todo-app-tls \
       --cert=tls.crt \
       --key=tls.key \
       -n todo-phaseiv

3. Ingress references secret:
   spec:
     tls:
     - secretName: todo-app-tls

4. Nginx loads certificate:
   ├─ Reads todo-app-tls secret
   ├─ Decodes base64
   ├─ Loads tls.crt (public cert)
   └─ Loads tls.key (private key)

5. TLS handshake:
   ├─ Browser → ClientHello
   ├─ Nginx → ServerHello + tls.crt
   └─ Session established

Certificate Rotation (every 365 days):
──────────────────────────────────────
1. Generate new certificate
2. Update secret:
   $ kubectl create secret tls todo-app-tls \
       --cert=tls-new.crt \
       --key=tls-new.key \
       -n todo-phaseiv \
       --dry-run=client -o yaml | kubectl apply -f -
3. Restart ingress controller:
   $ kubectl rollout restart -n ingress-nginx \
       deployment/ingress-nginx-controller
4. New certificate active ✅
```

### Network Security

```
Current (Development):
─────────────────────
• No NetworkPolicies (all pods can communicate)
• No pod-to-pod encryption (cluster network trusted)
• TLS only at ingress layer (external → cluster)

Production Recommendations:
──────────────────────────
1. NetworkPolicy (Egress):
   ┌────────────────────────────────────┐
   │ Frontend:                          │
   │ ├─ Allow → Backend                 │
   │ └─ Deny all other egress           │
   └────────────────────────────────────┘
   
2. NetworkPolicy (Ingress):
   ┌────────────────────────────────────┐
   │ Backend:                           │
   │ ├─ Allow ← Frontend                │
   │ ├─ Allow ← Ingress                 │
   │ └─ Deny all other ingress          │
   └────────────────────────────────────┘
   
3. Service Mesh (Istio/Linkerd):
   ├─ mTLS between all pods
   ├─ Encrypted pod-to-pod communication
   └─ Certificate rotation
```

---

## Resource Quotas

### Total Cluster Requirements

**Minimum Configuration (2 replicas):**
```
Component       CPU (cores)    Memory (GB)
─────────────────────────────────────────
Frontend x2     1.0 (2×500m)   1.0 (2×512Mi)
Backend x2      1.0 (2×500m)   1.0 (2×512Mi)
MCP Server x1   0.5 (500m)     0.5 (512Mi)
Redis x1        0.5 (500m)     0.25 (256Mi)
Ingress         0.5 (500m)     0.25 (256Mi)
Metrics Server  0.1 (100m)     0.2 (200Mi)
─────────────────────────────────────────
TOTAL           3.6 cores      3.2 GB

Minikube Start Command:
$ minikube start --cpus=4 --memory=8192
```

**Maximum Configuration (5 replicas):**
```
Component       CPU (cores)    Memory (GB)
─────────────────────────────────────────
Frontend x5     5.0 (5×1000m)  5.0 (5×1024Mi)
Backend x5      5.0 (5×1000m)  5.0 (5×1024Mi)
MCP Server x1   0.5 (500m)     0.5 (512Mi)
Redis x1        0.5 (500m)     0.25 (256Mi)
Ingress         0.5 (500m)     0.25 (256Mi)
Metrics Server  0.1 (100m)     0.2 (200Mi)
─────────────────────────────────────────
TOTAL           11.6 cores     11.2 GB

Minikube Start Command (not recommended):
$ minikube start --cpus=12 --memory=16384
```

### Resource Limits vs Requests

```
Requests: Guaranteed resources
  └─ Pod will only be scheduled on nodes with available resources

Limits: Maximum resources
  └─ Pod can burst up to limit, then throttled (CPU) or OOMKilled (Memory)

Example (Backend Pod):
  requests:
    cpu: 500m      ← Guaranteed: always gets 0.5 CPU cores
    memory: 512Mi  ← Guaranteed: always gets 512 MB RAM
  limits:
    cpu: 1000m     ← Maximum: can burst to 1.0 CPU cores
    memory: 1024Mi ← Maximum: killed if exceeds 1024 MB

QoS Class: Burstable
  └─ Has requests < limits
```

---

## Monitoring Points

### Health Check Endpoints

```
Component    Endpoint                      Response
──────────────────────────────────────────────────────────
Frontend     GET /api/health               {"status": "ok"}
Backend      GET /health                   {"status": "healthy", "service": "phaseiv-backend"}
MCP Server   GET /mcp                      {"jsonrpc": "2.0", ...}
Redis        exec: redis-cli ping          PONG
Ingress      GET /healthz                  ok (200)
```

### Prometheus Metrics (Future)

```
Recommended metrics to expose:
────────────────────────────
# HTTP request metrics
http_requests_total{method, path, status}
http_request_duration_seconds{method, path}

# Pod metrics (from Metrics Server)
container_cpu_usage_seconds_total
container_memory_working_set_bytes

# HPA metrics
kube_hpa_status_current_replicas
kube_hpa_status_desired_replicas
kube_hpa_spec_target_metric

# Custom application metrics
chatkit_messages_total{user_id}
mcp_tool_calls_total{tool_name}
redis_keys_total
task_operations_total{operation}
```

### Logging Best Practices

```
Log Levels:
──────────
ERROR: Application errors, exceptions
WARN:  Recoverable errors, degraded performance
INFO:  Normal operations, state changes
DEBUG: Detailed diagnostic information

Structured Logging (JSON):
─────────────────────────
{
  "timestamp": "2025-01-26T10:30:45Z",
  "level": "INFO",
  "service": "backend",
  "user_id": "user_123",
  "request_id": "abc-def-123",
  "message": "ChatKit message processed",
  "duration_ms": 234
}

Log Aggregation:
───────────────
kubectl logs -l app=backend -n todo-phaseiv | jq .
  └─ Filter, parse, analyze JSON logs
```

---

## High Availability Considerations

### Current Setup (Development)

```
Single Points of Failure:
────────────────────────
❌ Minikube (single-node cluster)
❌ Redis (1 replica, no failover)
❌ MCP Server (1 replica)
❌ Ingress (1 controller instance)
```

### Production Recommendations

```
1. Multi-Node Cluster (3+ nodes):
   ──────────────────────────────
   ├─ Node 1: Control plane + workers
   ├─ Node 2: Workers
   └─ Node 3: Workers
   
   Benefits:
   ├─ Pod anti-affinity (spread across nodes)
   ├─ Node failure tolerance
   └─ Rolling updates without downtime

2. Redis High Availability:
   ────────────────────────
   Option A: Redis Sentinel
   ├─ 3 Redis instances (1 master, 2 replicas)
   ├─ 3 Sentinel processes (quorum-based failover)
   └─ Automatic master election

   Option B: Redis Cluster
   ├─ 6+ Redis instances (3 masters, 3 replicas)
   ├─ Data sharding across masters
   └─ Built-in failover

3. MCP Server Scaling:
   ───────────────────
   ├─ Increase replicas: 2-3
   ├─ StatelessSet (not StatefulSet)
   └─ Load balanced by Service

4. Distributed Storage:
   ────────────────────
   Replace hostPath with:
   ├─ Longhorn (distributed block storage)
   ├─ Rook/Ceph (distributed storage)
   └─ Cloud provider storage (EBS, Persistent Disk)

5. PodDisruptionBudgets:
   ─────────────────────
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   spec:
     minAvailable: 1
     selector:
       matchLabels:
         app: backend
   
   Ensures:
   ├─ At least 1 backend pod always available
   └─ Prevents simultaneous eviction during updates

6. Ingress High Availability:
   ──────────────────────────
   ├─ Multiple Ingress controller replicas
   ├─ LoadBalancer service (cloud)
   └─ External load balancer (on-prem)
```

---

## Disaster Recovery

### Backup Strategy

```
Component         Backup Method              Frequency    Retention
─────────────────────────────────────────────────────────────────────
Redis             BGSAVE snapshot            Daily        7 days
                  Copy to: kubectl cp        Manual       -

PostgreSQL        Neon automatic backups     Daily        7 days
                  Point-in-time recovery     Continuous   -
                  Manual: pg_dump            Weekly       30 days

Application       Stateless (no backups)     -            -
  (Pods)

ConfigMaps        Git repository             Continuous   Forever
  & Secrets

Helm Charts       Git repository             Continuous   Forever

PVCs              Manual: tar hostPath       Weekly       4 weeks
```

### Recovery Procedures

#### Redis Data Loss

```
1. Identify latest backup:
   $ ls -lh backups/redis-*.rdb
   
2. Scale backend to 0 (stop writes):
   $ kubectl scale deployment/backend --replicas=0 -n todo-phaseiv
   $ kubectl scale deployment/mcp-server --replicas=0 -n todo-phaseiv
   
3. Copy backup to Redis pod:
   $ kubectl cp backups/redis-20250126.rdb \
       todo-phaseiv/redis-0:/data/dump.rdb
   
4. Restart Redis:
   $ kubectl delete pod redis-0 -n todo-phaseiv
   $ kubectl wait --for=condition=ready pod/redis-0 -n todo-phaseiv
   
5. Verify data:
   $ kubectl exec redis-0 -n todo-phaseiv -- redis-cli DBSIZE
   
6. Scale backend back up:
   $ kubectl scale deployment/backend --replicas=2 -n todo-phaseiv
   $ kubectl scale deployment/mcp-server --replicas=1 -n todo-phaseiv
```

#### Complete Cluster Failure

```
1. Recreate Minikube cluster:
   $ minikube delete
   $ minikube start --cpus=4 --memory=8192 --driver=docker
   $ minikube addons enable ingress
   
2. Recreate TLS secret:
   $ kubectl create secret tls todo-app-tls \
       --cert=certs/tls.crt \
       --key=certs/tls.key \
       -n todo-phaseiv
   
3. Deploy application:
   $ helm install todo-app kubernetes/helm/todo-app \
       -n todo-phaseiv \
       --create-namespace \
       -f kubernetes/helm/todo-app/values-local.yaml \
       -f kubernetes/helm/todo-app/values-tls.yaml \
       --wait
   
4. Restore Redis data:
   (Follow Redis recovery procedure above)
   
5. Verify all services:
   $ kubectl get pods -n todo-phaseiv
   $ curl -k https://todo-app.local/api/health
   
6. PostgreSQL data:
   ✅ No action needed (Neon is external, always available)
```

#### PostgreSQL Recovery (Neon)

```
Neon provides automatic recovery:
────────────────────────────────
1. Point-in-time recovery:
   - Via Neon console: Select timestamp
   - Creates new branch database
   - Update DATABASE_URL secret to point to branch

2. Restore from manual backup:
   $ kubectl cp backups/postgres-20250126.sql \
       todo-phaseiv/<backend-pod>:/tmp/
   $ kubectl exec -it <backend-pod> -n todo-phaseiv -- bash
   # psql $DATABASE_URL < /tmp/postgres-20250126.sql
```

---

## Related Documentation

- **[README.md](../../README.md)** - Project overview and quick start
- **[KUBERNETES_GUIDE.md](./KUBERNETES_GUIDE.md)** - Complete deployment guide
- **[RUNBOOK.md](./RUNBOOK.md)** - Operational procedures and troubleshooting
- **[Helm Chart](../helm/todo-app/README.md)** - Helm chart documentation

---

**Last Updated**: 2025-12-26  
**Version**: 2.0 (Phase IV with HTTPS/TLS)  
**Maintained By**: Phase IV Development Team

---

**🔒 Security Note**: This architecture uses self-signed TLS certificates for development. For production deployment, use certificates from a trusted Certificate Authority (e.g., Let's Encrypt).
