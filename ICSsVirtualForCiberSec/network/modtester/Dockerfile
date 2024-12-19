FROM ubuntu

# Set the environment to non-interactive to avoid prompts during build
ENV DEBIAN_FRONTEND noninteractive

# Install necessary dependencies, including python3
RUN apt-get update && \
    apt-get -y install python3 && \
    apt-get -y install libpcap-dev && \
    apt-get -y install hping3 && \
    rm -rf /var/lib/apt/lists/*
