# kali_execution_server/kali_driver/driver.py (Final Logic Fix)
import os
import time
import docker
import paramiko
import tarfile
from io import BytesIO


class KaliContainer:
    def __init__(self, owner):
        self._owner = owner
        self._ssh_client = None

        print("  [+] Creating Kali container from 'dawnyawn-kali-agent' image...")
        self._container = owner._docker_client.containers.create(
            image="dawnyawn-kali-agent",
            command="/usr/sbin/sshd -D",
            ports={"22/tcp": None},
            detach=True
        )

        self.id = self._container.id
        self.short_id = self._container.short_id

        self._ensure_started()
        print(f"  [+] Container '{self.short_id}' created and running.")

    def _ensure_started(self):
        self._container.reload()
        if self._container.status != "running":
            self._container.start()
            time.sleep(2) # A brief, initial sleep can still be helpful
        self._container.reload()

    def _ensure_connected(self):
        if self._ssh_client and self._ssh_client.get_transport().is_active():
            return

        self._container.reload()
        port_data = self._container.ports.get('22/tcp')
        if not port_data or 'HostPort' not in port_data[0]:
            raise Exception(f"Failed to find mapped SSH port for container {self.id}")

        public_port = int(port_data[0]['HostPort'])
        key_path = os.path.expanduser('~/.ssh/id_ecdsa')
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"SSH private key not found at {key_path}.")

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # --- THE FIX: Implement a retry loop for the SSH connection ---
        max_retries = 5
        retry_delay = 2  # in seconds
        for attempt in range(max_retries):
            try:
                self._ssh_client.connect(
                    hostname='localhost', port=public_port, username='root',
                    key_filename=key_path, timeout=10 # Use a shorter timeout for the connection attempt
                )
                # If connection is successful, break the loop
                print(f"  [+] SSH connection established to container '{self.short_id}' on attempt {attempt + 1}.")
                return
            except (paramiko.ssh_exception.SSHException, ConnectionResetError, TimeoutError) as e:
                if attempt < max_retries - 1:
                    print(f"  [!] SSH connection failed with '{type(e).__name__}'. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"  [!] SSH connection failed after {max_retries} attempts.")
                    # Re-raise the last exception to let the caller handle the final failure
                    raise e

    # --- THE FIX: This method NO LONGER returns output. It just executes. ---
    def send_command_and_get_output(self, command: str, timeout: int = 1800):
        self._ensure_connected()
        print(f"  [+] Sending command: '{command}'")
        stdin, stdout, stderr = self._ssh_client.exec_command(command, timeout=timeout)

        # --- THE FIX: We now wait for the command to complete by checking the exit status. ---
        # This is crucial because it blocks until the command is finished.
        exit_status = stdout.channel.recv_exit_status()
        print(f"  [+] Command finished with exit status: {exit_status}")
        # We no longer read stdout/stderr here, as it's all in the file.

    def copy_file_from_container(self, path: str) -> str:
        """Copies a file from the container and returns its content as a string."""
        try:
            bits, stat = self._container.get_archive(path)

            with BytesIO() as f:
                for chunk in bits:
                    f.write(chunk)
                f.seek(0)
                with tarfile.open(fileobj=f) as tar:
                    # Handle cases where the tarball might be empty or malformed
                    members = tar.getmembers()
                    if not members:
                         return f"Command produced no output file at '{path}' (empty archive)."
                    member = members[0]
                    extracted_file = tar.extractfile(member)
                    if extracted_file:
                        return extracted_file.read().decode('utf-8', errors='ignore')
                    else:
                        return f"Failed to extract file from archive for '{path}'."

        except docker.errors.NotFound:
            # If the command produced no output file, return a string indicating that.
            return f"Command produced no output file at '{path}'."
        except IndexError:
            # If the tarball is empty, it means the file was not created.
            return f"Command produced no output file at '{path}'."

    def destroy(self):
        if self._ssh_client:
            self._ssh_client.close()
        try:
            self._container.reload()
            print(f"\n  [+] Cleaning up container '{self.short_id}'...")
            if self._container.status in ["running", "created"]:
                self._container.stop()
            self._container.remove(force=True)
            print("  [+] Cleanup complete.")
        except docker.errors.NotFound:
            pass


class KaliManager:
    def __init__(self):
        try:
            self._docker_client = docker.from_env()
            self._docker_client.ping()
        except Exception as e:
            print("FATAL ERROR: Could not connect to Docker. Is it running?")
            raise e

    def create_container(self) -> "KaliContainer":
        return KaliContainer(owner=self)