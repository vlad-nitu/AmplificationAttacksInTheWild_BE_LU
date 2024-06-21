# Use an official Python runtime as a parent image
FROM python:3.9.17

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container -> not needed, already present
COPY configs/requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install jq, dig, fpdns, ntpd, ip, and other requested tools
RUN apt-get update && \
    apt-get install -y jq dnsutils fpdns ntp iproute2 \
    vim zmap tshark traceroute tmux telnet tcpdump \
    strace texlive-extra-utils dnsutils netcat-openbsd net-tools less \
    bsdmainutils man net-tools && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the working directory contents into the container at /usr/src/app
# COPY src dst
COPY . .

# Set the default command to start a sh shell
CMD ["sh"]
