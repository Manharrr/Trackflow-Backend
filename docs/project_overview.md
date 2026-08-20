# TrackFlow AI — Platform Overview & System Guide

TrackFlow AI is a secure, multi-tenant logistics Software-as-a-Service (SaaS) platform designed to streamline shipment management, dispatch operations, and team coordination.

---

## 1. What is TrackFlow AI?
* **Purpose**: An AI-powered logistics dashboard enabling companies to manage their supply chain, shipments, employees, and operations in isolated tenant environments.
* **Architecture**: A multi-tenant system where each tenant (company) gets its own subdomain workspace (e.g. `http://companyname.logesticgo.localhost:5173`) and isolated database partition.
* **Technology**: Built using a React frontend (Vite, Tailwind CSS, Redux), Django backend, and a FastAPI AI microservice powered by LangChain, FAISS, and Gemini.

---

## 2. User Roles & Duties (Access Control)

The platform supports four distinct user roles, each with specific permissions:

### A. Super Admin
* **Duties**:
  * Monitors global platform health and telemetry indices.
  * Reviews and approves pending tenant registration requests.
  * Manages global billing packages, workspace allocations, and database provisioning.
* **Routes**: `/super-admin/*`

### B. Company Admin (Tenant Administrator)
* **Duties**:
  * Configures company settings, uploads logos, and sets workspace addresses.
  * Onboards employees and operations personnel (by sending secure email invitations).
  * Assigns roles to personnel within their company tenant.
  * Accesses company-wide logistics charts, courier leaderboards, and financial overview metrics.
* **Routes**: `/dashboard/*`, `/settings`, `/profile`

### C. Operations Manager
* **Duties**:
  * Manages the active dispatch queue.
  * Creates shipments from customer orders.
  * Assigns orders/shipments to couriers/drivers.
  * Logs delay reasons or delivery failure remarks.
  * Monitors operations metrics, delivery success index, and courier performance leaderboards.
* **Routes**: `/operations/*`

### D. Courier / Driver (Employee)
* **Duties**:
  * Views their personal list of assigned shipments.
  * Updates shipment tracking status in real-time:
    * `Out for Delivery`
    * `Completed / Delivered`
    * `Delayed` (with delay reason code)
    * `Failed` (with failure reason code)
  * Logs proof of delivery or transit notes.
* **Routes**: `/employee/*`

---

## 3. Platform Modules & Workflows

### A. Order Management
* **Order States**:
  * `Pending`: Order placed, waiting for verification.
  * `Assigned`: Courier assigned to the order.
  * `Out for Delivery`: Courier is in transit.
  * `Delivered`: Completed successfully.
  * `Delayed`: Delivery delayed due to external factor.
  * `Cancelled`: Cancelled by admin or customer.
  * `Failed`: Attempted but failed delivery.

### B. Courier Assignment Flow
* **Manual Assignment**: Operations Managers assign orders to specific courier partners via the dispatch dashboard.
* **Bulk Assignment**: Administrators select multiple shipments and bulk-assign them to a driver to optimize routing.

### C. Tenant Workspace Security & Policy
* **Data Isolation**: Multi-tenancy enforces absolute data separation. Companies cannot see each other's orders, drivers, or logs.
* **Multi-Factor Authentication (MFA)**: All users are encouraged to set up MFA via TOTP Authenticator apps during setup for secure login verification.
* **Session Transfer**: Session tokens are transferrable securely across subdomains via encoded query parameters (`auth_transfer` / `refresh_token`) to allow seamless navigation across company subdomains.
