---
title: "Authentication & Session Management"
sidebar_position: 2
---

The OffloadSecurity CSPM platform implements an enterprise-grade authentication and session management system designed for high security and resilience. It features PBKDF2-based password hashing, multi-tier session persistence, and a challenge-response MFA flow.

## 1. Authentication Flow & Security

The `AuthService` `backend/core/auth_system.py:237-270` manages the core identity lifecycle. It utilizes secure hashing and timing-safe practices to protect against common authentication attacks.

### 1.1. Password Hashing (PBKDF2)
Passwords are never stored in plaintext. The system uses **PBKDF2-SHA256** for hashing `backend/core/auth_system.py:54-66`. 
- **Iteration Count**: Modern hashes use 600,000 iterations to meet OWASP recommendations `backend/core/auth_system.py:29-29`.
- **Backward Compatibility**: The system supports legacy 100,000 iteration hashes by encoding the iteration count within the salt string (format: `{iterations}${hex_salt}`) `backend/core/auth_system.py:73-94`.
- **Salt Generation**: A unique 16-byte hex salt is generated for every user using `secrets.token_hex(16)` `backend/core/auth_system.py:61-61`.

### 1.2. Login Protection Mechanisms
- **Brute-Force Lockout**: Accounts are locked after 5 failed attempts `backend/core/auth_system.py:27-27`. The lockout duration is 15 minutes (900 seconds) `backend/core/auth_system.py:28-28`.
- **Email Enumeration Protection**: To prevent timing attacks that reveal if an email exists, the system uses a pre-computed dummy hash (`_TIMING_PAD_HASH`) `backend/core/auth_system.py:70-70`. If a user is not found, the system still performs a PBKDF2 verification against this dummy hash so that response times remain consistent `backend/core/auth_system.py:255-262`.

### 1.3. Identity Logic
Users are represented by the `User` class `backend/core/auth_system.py:97-121` and assigned one of several roles: `ADMIN`, `SECURITY_MANAGER`, `SECURITY_ANALYST`, `COMPLIANCE_OFFICER`, `AUDITOR`, or `VIEWER` `backend/core/auth_system.py:32-45`. These roles map to granular permissions calculated in `_get_permissions` `backend/core/auth_system.py:123-164`.

**Sources:** `backend/core/auth_system.py:24-262`, `backend/core/auth_standard.py:37-104`

---

## 2. Session Management & Storage

The platform employs a multi-tier `SessionStorage` architecture to ensure sessions survive server restarts and remain performant.

### 2.1. Multi-Tier Storage Strategy
The `SessionStorage` class `backend/services/session_storage_service.py:41-50` attempts to initialize backends in the following order of priority `backend/services/session_storage_service.py:68-91`:
1.  **Redis**: Primary high-performance store with native TTL support `backend/services/session_storage_service.py:92-111`.
2.  **MongoDB**: Persistent fallback. Sessions are stored in the `sessions` collection with a TTL index on `expires_at` `backend/services/session_storage_service.py:113-179`.
3.  **In-Memory**: Last resort fallback if both Redis and MongoDB are unreachable `backend/services/session_storage_service.py:86-90`.

### 2.2. Session Security & Hashing
To prevent session hijacking via database or memory dumps, session IDs (generated as `secrets.token_urlsafe(32)`) are hashed using **SHA-256** before storage `backend/services/session_storage_service.py:21-38`. The `create_session` method automatically hashes the raw ID before persistence `backend/services/session_storage_service.py:180-192`.

### 2.3. Session Validation & Retrieval
The `get_current_user` dependency `backend/core/auth_standard.py:37-104` validates credentials in order:
1.  `Authorization: Bearer {token}` header `backend/core/auth_standard.py:44-44`.
2.  `X-Session-ID` header for frontend compatibility `backend/core/auth_standard.py:45-45`.
3.  `?token=` query parameter, accepted **only** on SSE endpoints to prevent leakage in access logs `backend/core/auth_standard.py:55-70`.

### Code Entity Mapping: Authentication & Session Data Flow

Title: "Auth & Session Data Flow"
```mermaid
graph TD
    subgraph "Frontend_Layer"
        ApiSvc["AuthContext.js:useAuth"]
        LoginComp["Login.js:handleLogin"]
    end

    subgraph "Backend_API_Layer"
        AuthStd["auth_standard.py:get_current_user"]
        AuthSvc["auth_system.py:AuthService"]
    end

    subgraph "Storage_Layer"
        SessionSvc["session_storage_service.py:SessionStorage"]
        DB[("MongoDB: sessions_collection")]
        Redis[("Redis: Session_Cache")]
    end

    LoginComp -- "POST /auth/login" --> AuthSvc
    ApiSvc -- "Authorization: Bearer" --> AuthStd
    AuthStd -- "auth_service.get_user_from_session()" --> AuthSvc
    AuthSvc -- "session_storage.get_session()" --> SessionSvc
    SessionSvc -- "GET" --> Redis
    SessionSvc -- "find_one" --> DB
    
    AuthSvc -- "session_storage.create_session()" --> SessionSvc
    SessionSvc -- "SETEX" --> Redis
    SessionSvc -- "insert_one" --> DB
```
**Sources:** `backend/services/session_storage_service.py:20-192`, `backend/core/auth_standard.py:37-104`, `backend/core/auth_system.py:237-270`, `frontend/src/AuthContext.js:19-141`, `frontend/src/components/Login.js:16-67`

---

## 3. MFA TOTP Challenge-Token Flow

The Multi-Factor Authentication (MFA) system uses a challenge-token flow to decouple the initial password check from the second-factor verification.

### 3.1. The MFA Challenge
When a user with MFA enabled logs in, the `AuthService` does not return a full session immediately. Instead, it returns an `mfa_required: true` flag and a temporary `mfa_token` challenge string `backend/routes/mfa_routes.py:181-200`.

### 3.2. Verification Flow
1.  **Setup**: User calls `/api/auth/mfa/setup` to receive a TOTP secret and QR code `backend/routes/mfa_routes.py:63-79`.
2.  **Enable**: User provides a 6-digit code to `/api/auth/mfa/enable`. Success triggers the generation of backup codes `backend/routes/mfa_routes.py:87-113`.
3.  **Verify**: During login, the user submits the `mfa_token` and the TOTP `code` to `/api/auth/mfa/verify` `backend/routes/mfa_routes.py:181-200`.

### Code Entity Mapping: MFA Verification Flow

Title: "MFA Challenge-Response Sequence"
```mermaid
sequenceDiagram
    participant U as "User (Client)"
    participant R as "mfa_routes.py"
    participant M as "mfa_service.py"
    participant S as "session_storage_service.py"

    U->>R: "POST /login (email, password)"
    R->>M: "get_mfa_status(user_id)"
    M-->>R: "enabled=true"
    R->>S: "create_session(mfa_token, temp_data)"
    R-->>U: "200 OK (mfa_required=true, mfa_token)"
    
    U->>R: "POST /mfa/verify (mfa_token, code)"
    R->>M: "verify_totp(user_id, code)"
    M-->>R: "valid=true"
    R->>S: "create_session(user_id, session_data)"
    R-->>U: "200 OK (session_id, user)"
```
**Sources:** `backend/routes/mfa_routes.py:63-200`, `backend/services/session_storage_service.py:180-192`, `backend/services/mfa_service.py:1-100`

---

## 4. Registration & Invitation System

OffloadSecurity is designed as an **invite-only** platform. Registration is managed through an invitation-based flow to ensure auditable access control.

### 4.1. Invitation Lifecycle
Users can only register if they possess a valid invitation token `frontend/src/components/Register.js:23-35`.
- **Registration Flow**: The `Register.js` component extracts the `invitation_token` from URL parameters `frontend/src/components/Register.js:24-24`.
- **Validation**: Registration requires matching the email address to which the invitation was originally sent `frontend/src/components/Register.js:60-63`.
- **Blocked Access**: If no token is present, the frontend displays an "Invite Only" blocked message `frontend/src/components/Register.js:124-159`.

### 4.2. Bootstrap & Setup Mode
For fresh installations, the platform includes a `ProtectedRoute` logic that detects if the initial setup is complete `frontend/src/components/ProtectedRoute.js:11-27`.
- **Setup Redirect**: If `/api/setup/status` returns `setup_complete: false`, users are redirected to the `/setup` route to create the first admin account `frontend/src/components/ProtectedRoute.js:58-60`.

### 4.3. Audit Trail & Webhook Integration
Every authentication event is captured by the `AuditTrailMiddleware` `backend/middleware/audit_trail.py:155-168`. Actions like `user.login` and `mfa.enable` are classified and stored in an immutable log `backend/middleware/audit_trail.py:55-63`. Furthermore, the `WebhookEventBus` can push these events (e.g., `user.login`) to external SIEM/SOAR systems `backend/services/webhook_event_bus.py:12-12`.

**Sources:** `frontend/src/components/Register.js:1-162`, `frontend/src/components/ProtectedRoute.js:6-67`, `backend/middleware/audit_trail.py:1-144`, `backend/services/webhook_event_bus.py:1-102`

---