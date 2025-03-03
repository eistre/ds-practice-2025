# Documentation

## Project Overview
This project is a distributed system for an online book store in the distributed systems course.

## Project Structure
```
/
├── docs/                       # Project documentation
├─- fraud_detection/            # Fraud detection service
├── frontend/                   # Frontend client
├── orchestrator/               # Orchestration service for managing other services
├── suggestions/                # Book suggestions service
├── transaction_verification/   # Transaction verification service
├── utils/                      # Shared utilities and libraries (gRPC, OpenAPI)
├── docker-compose.yaml         # Docker Compose configuration
```

## System Architecture

The system implements a client-server architecture with the Orchestrator service acting as the central coordination point. Clients interact with the Orchestrator service through synchronous REST/HTTP calls to place book orders.

Upon receiving client requests, the Orchestrator service coordinates with specialized microservices (Fraud Detection, Suggestions, and Transaction Verification) via gRPC to fulfill the order processing workflow. It manages concurrent interactions with downstream services using a multi-threaded approach. Despite this parallelization, all service-to-service communications maintain synchronous request-response patterns, ensuring transaction integrity.

## Architecture Diagram

![Architecture diagram](./architecture_diagram.png)

The architecture diagram illustrates the distributed system with the following components:
- **Frontend**: Client application for user interaction (port 8080);
- **Orchestrator**: Central service for managing other services (port 8081);
- **Fraud Detection**: Service for detecting fraudulent transactions (port 50051);
- **Transaction Verification**: Service for verifying user transactions (port 50052);
- **Suggestions**: Service for providing book recommendations (port 50053).

Communication between the frontend and orchestrator happens over REST/HTTP, while service-to-service communication occurs over gRPC. Fraud Detection and Suggestions services utilize external Google Gemini API for AI-based fraud detection and book recommendations via REST/HTTP.

## System Diagram

![System diagram](./system_diagram.png)

This diagram shows the request lifecycle:
1. The client submits an order request through the frontend;
2. The frontend sends the request to the Orchestrator service;
3. The Orchestrator service calls the Fraud Detection, Transaction Verification, and Suggestions services concurrently to process the order;
    1. The Fraud Detection and Suggestions services call the Google Gemini API for fraud detection and book recommendations;
    2. Google Gemini API responds with the fraud detection result and book recommendations;
4. The Services respond to the Orchestrator service with their results;
5. The Orchestrator service aggregates the responses and sends the final order status to the frontend;
6. The frontend displays the order status to the client.

## Setup
1. Clone the repository;
2. Create `.env` files in `fraud_detection` and `suggestions` directories with the following content:
    ```
    GOOGLE_API_KEY=<your_google_api_key>
    ```
3. Run `docker-compose up --build` to start all services;
4. Access the frontend at `http://localhost:8080`.
