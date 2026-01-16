# Helm Chart Comprehensive Review

**Date:** 2026-01-03
**Chart:** todo-app (Phase V)
**Status:** ⚠️ **5 Issues Found (2 Critical, 3 Minor)**

---

## ❌ CRITICAL ISSUES

### Issue 1: Frontend Database URL Reference - INCORRECT KEY
**File:** `templates/frontend-deployment.yaml:47`
**Severity:** 🔴 **CRITICAL - Pod will fail to start**

**Problem:**
```yaml
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-app-secrets
      key: DATABASE_URL  # ❌ WRONG KEY
```

**Root Cause:**
Frontend uses Better Auth with plain PostgreSQL driver, which requires `FRONTEND_DATABASE_URL` from the secret. The secret template (secret.yaml:14) creates `FRONTEND_DATABASE_URL` key, not `DATABASE_URL`.

**Impact:**
- Frontend pods will fail with `CreateContainerConfigError: couldn't find key DATABASE_URL in Secret`
- Frontend cannot connect to database even if pod starts

**Fix Required:**
```yaml
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-app-secrets
      key: FRONTEND_DATABASE_URL  # ✅ CORRECT
```

**Location:** `phaseV/kubernetes/helm/todo-app/templates/frontend-deployment.yaml:47`

---

### Issue 2: Port Conflict - Recurring Service and Email Delivery
**File:** `templates/recurring-deployment.yaml:72,80` and `templates/email-delivery-deployment.yaml:29`
**Severity:** 🔴 **CRITICAL - Service conflict**

**Problem:**
Both recurring-service and email-delivery-service use port **8003**:

**recurring-deployment.yaml:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8003  # ❌ CONFLICT

readinessProbe:
  httpGet:
    path: /health
    port: 8003  # ❌ CONFLICT

# Service definition
ports:
  - name: http
    protocol: TCP
    port: 8003
    targetPort: 8003
```

**email-delivery-deployment.yaml:**
```yaml
ports:
- containerPort: 8003  # ❌ SAME PORT
  name: http
  protocol: TCP
```

**Impact:**
- If both services run, one will fail health checks
- Kubernetes service routing will be ambiguous
- Potential connection errors

**Fix Required:**
Change recurring-service to use port **8004**:

**In `templates/recurring-deployment.yaml`:**
```yaml
# Line 72 & 80 (probes)
port: 8004  # ✅ Changed from 8003

# Line 101-102 (service)
port: 8004
targetPort: 8004
```

**Also update backend code:** `app/services/recurring_task_service_standalone.py` to listen on port 8004

---

## ⚠️ MINOR ISSUES

### Issue 3: Chart Metadata - Outdated Description
**File:** `Chart.yaml:3`
**Severity:** 🟡 **MINOR - Documentation only**

**Problem:**
```yaml
description: Phase IV Todo Chatbot - Kubernetes deployment with Helm
```

**Should be:**
```yaml
description: Phase V Event-Driven Todo App - Kubernetes deployment with Helm
```

**Impact:** None functional, just documentation clarity

---

### Issue 4: ConfigMap Value Overrides - Potential Template Issue
**File:** `templates/configmap.yaml` and `values-local.yaml`
**Severity:** 🟡 **MINOR - Works but inconsistent**

**Observation:**
`configmap.yaml` uses:
```yaml
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: {{ .Values.configMap.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY | quote }}
```

`values-local.yaml` defines:
```yaml
configMap:
  NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: "domain_pk_..."
```

**Analysis:**
- ✅ This works correctly - values-local.yaml overrides will merge with values.yaml
- ⚠️ However, configmap.yaml lines 23-30 have conditional TLS logic that might override values-local.yaml settings

**Recommendation:**
Review configmap.yaml lines 22-31 to ensure values-local.yaml overrides take precedence over conditional TLS logic.

**Current behavior:**
```yaml
{{- if .Values.ingress.tls.enabled }}
  NEXT_PUBLIC_API_URL: {{ printf "https://%s/api" .Values.ingress.host | quote }}
  # This OVERRIDES values-local.yaml!
{{- else }}
  NEXT_PUBLIC_API_URL: {{ printf "http://%s/api" .Values.ingress.host | quote }}
{{- end }}
```

**Better approach:**
```yaml
{{- if .Values.configMap.NEXT_PUBLIC_API_URL }}
  NEXT_PUBLIC_API_URL: {{ .Values.configMap.NEXT_PUBLIC_API_URL | quote }}
{{- else if .Values.ingress.tls.enabled }}
  NEXT_PUBLIC_API_URL: {{ printf "https://%s/api" .Values.ingress.host | quote }}
{{- else }}
  NEXT_PUBLIC_API_URL: {{ printf "http://%s/api" .Values.ingress.host | quote }}
{{- end }}
```

---

### Issue 5: Email Delivery Secret Template - Double Base64 Encoding
**File:** `templates/email-delivery-secret.yaml:14-15`
**Severity:** 🟡 **MINOR - Values need to be plaintext**

**Problem:**
```yaml
smtp-username: {{ .Values.emailDelivery.smtp.username | b64enc | quote }}
smtp-password: {{ .Values.emailDelivery.smtp.password | b64enc | quote }}
```

**Current values-local.yaml:**
```yaml
emailDelivery:
  smtp:
    username: "saleemakhtar864@gmail.com"  # Plaintext
    password: "orbkgyktbdrkwbpu"  # Plaintext
```

**Analysis:**
- ✅ **This is actually CORRECT!**
- The template applies `| b64enc` to the plaintext values from values-local.yaml
- Kubernetes secrets require base64-encoded data
- This is the right approach (values file has plaintext, template encodes)

**No fix needed** - This is working as designed.

---

## ✅ VERIFIED CORRECT

### Secret Template (secret.yaml)
- ✅ All secret keys properly defined with conditional checks
- ✅ Uses `{{ .Values.secrets.* | quote }}` correctly (values already base64-encoded)
- ✅ Covers all required secrets: DATABASE_URL, FRONTEND_DATABASE_URL, OPENAI_API_KEY, etc.

### Backend Deployment
- ✅ All environment variables correctly mapped
- ✅ Kafka configuration (secrets + configmap) properly split
- ✅ REDIS_PASSWORD conditionally included
- ✅ Resource limits defined
- ✅ Health probes configured

### MCP Server Deployment
- ✅ Correct command: `/app/.venv/bin/python -m app.mcp.standalone`
- ✅ All required env vars (DATABASE_URL, OPENAI_API_KEY, KAFKA_*, REDIS_*)
- ✅ Proper port configuration (8001)

### Notification Service Deployment
- ✅ Single replica (prevents duplicate reminders)
- ✅ Correct command: `python -m app.services.notification_service_standalone`
- ✅ All Kafka env vars configured
- ✅ Health probes on port 8002

### Email Delivery Service Deployment
- ✅ Single replica (prevents duplicate emails)
- ✅ Graceful shutdown configuration (preStop hook, terminationGracePeriodSeconds)
- ✅ References correct secrets (database, kafka, smtp)
- ✅ Health probes properly configured

### Label Consistency (_helpers.tpl)
- ✅ All helper templates properly defined
- ✅ Consistent labeling across all resources
- ✅ Proper selector label matching

---

## 🎯 REQUIRED FIXES (Priority Order)

### Fix 1: Frontend Database URL Key ⚠️ **MUST FIX**
```bash
# File: phaseV/kubernetes/helm/todo-app/templates/frontend-deployment.yaml
# Line: 47
# Change:
key: DATABASE_URL  # OLD
key: FRONTEND_DATABASE_URL  # NEW
```

### Fix 2: Recurring Service Port Conflict ⚠️ **MUST FIX**
```bash
# File: phaseV/kubernetes/helm/todo-app/templates/recurring-deployment.yaml
# Lines: 72, 80, 101, 102
# Change all instances of port 8003 to 8004

# Also update backend code:
# File: phaseV/backend/app/services/recurring_task_service_standalone.py
# Change: PORT = 8003  → PORT = 8004
```

### Fix 3: Chart Description (Optional)
```bash
# File: phaseV/kubernetes/helm/todo-app/Chart.yaml
# Line: 3
description: Phase V Event-Driven Todo App - Kubernetes deployment with Helm
```

### Fix 4: ConfigMap Override Priority (Optional but Recommended)
```bash
# File: phaseV/kubernetes/helm/todo-app/templates/configmap.yaml
# Lines: 23-30
# Add conditional check for .Values.configMap.* before TLS logic
```

---

## 📊 Summary

| Category | Count | Details |
|----------|-------|---------|
| **Critical Issues** | 2 | Frontend DB key, Port conflict |
| **Minor Issues** | 3 | Chart description, ConfigMap priority, (email secret is actually correct) |
| **Total Issues** | 5 | 2 must fix before deployment |
| **Verified Correct** | 15+ | All other templates working as designed |

---

## 🔍 Deployment Readiness

**Current State:** ⚠️ **NOT READY**

**Blocking Issues:**
1. ❌ Frontend will fail to start (DATABASE_URL key error)
2. ❌ Recurring service will conflict with email-delivery (port 8003)

**After Fixes:** ✅ **READY TO DEPLOY**

**Recommended Deployment Command:**
```bash
cd /home/salim/Desktop/hackathon-II-todo-app/phaseV/kubernetes/helm

helm upgrade todo-app ./todo-app \
  --install \
  --namespace todo-phasev \
  --create-namespace \
  -f ./todo-app/values.yaml \
  -f ./todo-app/values-local.yaml \
  --timeout 10m \
  --wait
```

---

## 📝 Next Steps

1. **Fix frontend-deployment.yaml** - Change DATABASE_URL key to FRONTEND_DATABASE_URL
2. **Fix recurring-deployment.yaml** - Change port from 8003 to 8004
3. **Update recurring service code** - Change listening port to 8004
4. **Optional: Update Chart.yaml** - Change description to Phase V
5. **Deploy with corrected charts**
6. **Verify all pods start successfully**

**Estimated time to fix:** 5 minutes
**Risk level after fixes:** ✅ Low - all critical issues addressed
