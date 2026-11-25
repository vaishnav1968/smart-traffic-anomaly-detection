# Agent Sandbox Dockerfile
FROM python:3.10-slim

# Create non-root user
RUN groupadd -r agentgroup && useradd -r -g agentgroup -d /home/agentuser -m -s /bin/bash agentuser

WORKDIR /workspace

# Copy agent script
COPY agent.py /home/agentuser/agent.py
COPY workspace /workspace

# Install httpx
RUN pip install --no-cache-dir httpx

# Set restricted ownership
RUN chown -R agentuser:agentgroup /workspace /home/agentuser

# Drop to non-root user
USER agentuser

ENV PYTHONUNBUFFERED=1
ENV VETO_API_URL=http://veto-backend:8000/api/intercept

CMD ["python", "/home/agentuser/agent.py"]
