# Multi-Agent Collab
This repository contains the setup for various AI agents and chat integrations, primarily focused on Slack. Each folder within the `repository` directory represents a distinct agent, each equipped with its own Dockerfile for containerization. We utilize Docker Compose to orchestrate all agents and chat integrations simultaneously. For live interactions, such as receiving messages from Slack, ngrok is employed to expose the local development environment to the internet.

## Directory Structure

- **/repository/**: Contains subdirectories for each agent. Each subdirectory has a Dockerfile.
- **/chat-integrations/**: Contains chat integrations like Slack
- **docker-compose.yml**: Used to define and run multi-container Docker applications.

## Prerequisites

- **Docker**: Ensure Docker is installed and running on your machine. Docker is used to create containers for the agents and the Slack integration.

## Setup Instructions

### Setting Up Docker Compose

Navigate to the root directory of this project and build the services using Docker Compose:

```bash
docker-compose up --build
```

This command builds and starts all the services defined in the `docker-compose.yml` file. Each service represents either an agent or the Slack integration.

Ngrok will provide a URL which you must configure in your Slack application under Event Subscriptions and Interactivity & Shortcuts.

### 3. Updating Slack Configuration

After setting up ngrok, update your Slack application's configuration to use the ngrok URL for events and interactivity. This ensures that Slack sends events to your locally running application.

## Usage

Once the Docker containers are up and running, and ngrok is configured, your setup is ready to receive and process messages. Make sure your chat intrgrations have the necessary permissions to read and respond to messages.

## Contributing

Contributions to enhance the agents or integrations are welcome. Please ensure you follow the existing code structure and update the Docker configurations as necessary.

---

This README provides a comprehensive guide on how to set up and run the integrations and agents using Docker and ngrok. Be sure to replace placeholder paths and commands with those specific to your project setup.