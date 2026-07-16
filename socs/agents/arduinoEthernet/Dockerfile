# OCS Barebones Agent
# ocs Agent for demonstrating how to write an Agent

# Use ocs base image
FROM simonsobs/ocs:latest

# Set the working directory to copy your Agent into
WORKDIR /app/agents/arduino/

# If there are extra dependencies install them here

# Copy the current directory into the WORKDIR
COPY . .

# Run registry on container startup
#ENTRYPOINT ["dumb-init", "ocs-agent-cli"]
ENTRYPOINT ["python3", "-u", "agent.py"]

# Set default commandline arguments
CMD ["--agent", "agent.py", "--entrypoint", "main"]

