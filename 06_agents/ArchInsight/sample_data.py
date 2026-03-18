# sample_data.py
# Sample / Fallback Data for ArchInsight Multi-Agent Architecture Review
# Pairs with main.py
# Kadambari Mirashi

# This module provides a sample architecture description that can substitute
# for Agent 1 (VLM) output when no vision model is available or no diagram
# image is provided. This lets the full pipeline run end-to-end for testing
# and demonstration.

# 0. CONFIGURATION ###################################

# Path to a sample architecture diagram image.
# Replace this with the path to your own diagram.
SAMPLE_IMAGE_PATH = "diagram.png"


# 1. SAMPLE ARCHITECTURE DESCRIPTION ###################################

# This simulates what Agent 1 (Visual Architecture Interpreter) would produce
# after analyzing a typical enterprise microservices architecture diagram.
# Used as fallback input for Agents 2 and 3 when VLM is unavailable.

SAMPLE_ARCHITECTURE_DESCRIPTION = """
### Architecture Type
Microservices architecture with an event-driven integration layer. The primary pattern is request-response via REST APIs, with a secondary asynchronous pattern using a message broker for inter-service communication and event propagation.

### Detected Components
- **API Gateway** — Type: reverse proxy / API gateway; Technology: Kong or NGINX
- **Auth Service** — Type: REST API microservice; Technology: Node.js, issues JWTs
- **User Service** — Type: REST API microservice; Technology: Python (FastAPI)
- **Order Service** — Type: REST API microservice; Technology: Java (Spring Boot)
- **Inventory Service** — Type: REST API microservice; Technology: Go
- **Notification Service** — Type: event consumer microservice; Technology: Python
- **Message Broker** — Type: message queue / event bus; Technology: RabbitMQ
- **Users Database** — Type: relational database; Technology: PostgreSQL
- **Orders Database** — Type: relational database; Technology: PostgreSQL
- **Inventory Database** — Type: NoSQL document store; Technology: MongoDB
- **Redis Cache** — Type: in-memory cache; Technology: Redis
- **CDN** — Type: content delivery network; Technology: Cloudflare

### Inferred Data Flow
1. Client requests arrive at the CDN for static assets or pass through to the API Gateway.
2. The API Gateway authenticates requests via the Auth Service (JWT validation) and routes them to the appropriate microservice.
3. The User Service handles user profile operations, reading and writing to the Users PostgreSQL database.
4. The Order Service processes order creation and retrieval against the Orders PostgreSQL database. On order creation, it publishes an "OrderCreated" event to the RabbitMQ message broker.
5. The Inventory Service consumes "OrderCreated" events from RabbitMQ to decrement stock levels in the MongoDB inventory database. It also exposes a REST endpoint for stock queries, with results cached in Redis.
6. The Notification Service consumes events from RabbitMQ (e.g., "OrderCreated", "LowStock") and sends email/SMS notifications to users.
7. Responses flow back through the API Gateway to the client.

### Diagram Summary
This is a microservices-based e-commerce platform with six distinct services coordinated through an API gateway and a RabbitMQ message broker. The architecture separates concerns across user management, order processing, inventory tracking, and notifications. Synchronous REST calls handle client-facing operations while asynchronous events decouple order processing from inventory updates and notifications. The system uses a polyglot persistence strategy with PostgreSQL for transactional data and MongoDB for inventory, supplemented by a Redis cache layer.
""".strip()
