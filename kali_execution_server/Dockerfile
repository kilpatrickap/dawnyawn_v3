# Dockerfile for a POWERFUL Villager Agent Environment

# 1. Start from the official Kali Linux base image
FROM kalilinux/kali-rolling

# 2. Set environment variable for non-interactive installations
ENV DEBIAN_FRONTEND=noninteractive

# 3. Update and install a comprehensive set of pentesting tools
RUN apt-get update && apt-get install -y \
    # Networking & Recon
    openssh-server \
    nmap \
    dnsutils \
    net-tools \
    curl \
    whois \
    whatweb \
    # Web Pentesting
    gobuster \
    nikto \
    # Exploitation
    sqlmap \
    hydra \
    # Metasploit is very large, uncomment it if you need its power
    # metasploit-framework \
    && rm -rf /var/lib/apt/lists/*

# 4. Configure the SSH Server
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN mkdir -p /root/.ssh

# 5. Authorize your SSH key
COPY id_ecdsa.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# 6. Expose the SSH port
EXPOSE 22

# 7. Start the SSH server
CMD ["/usr/sbin/sshd", "-D"]