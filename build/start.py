#! /usr/bin/env python3

from toml import load, TomlDecodeError
from os import environ, path
from subprocess import run, Popen, check_output, CalledProcessError
from signal import SIGTERM, signal
from re import search, match
from sys import exit
from time import sleep


# Load and validate configuration
try:
    config_path = path.join(environ.get("HOME", ""), "configuration.toml")
    if not path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    config = load(config_path)
    # Validate required keys
    for k in ["destAddr", "tap", "run"]:
        if k not in config:
            raise KeyError(k)
    if "target" not in config["run"]:
        raise KeyError("run.target")
except FileNotFoundError as fnf_error:
    print(f"Error: {fnf_error}")
    exit(1)
except TomlDecodeError:
    print("Error: Malformed configuration file (invalid TOML syntax).")
    exit(1)
except KeyError as key_error:
    print(f"Error: Configuration file is missing a required key: {key_error}")
    exit(1)
except Exception as e:
    print(f"Unexpected error while loading configuration: {e}")
    exit(1)

dest_addr = config["destAddr"]
tap_name = config["tap"]
target_name = config["run"]["target"]


def get_ip_from_getent(service_name):
    """Resolve the IP address of a service using 'getent hosts'."""
    try:
        # Run the 'getent hosts' command
        result = check_output(["getent", "hosts", service_name], text=True)

        # Parse the IP address using a regular expression
        match = search(r"(\d+\.\d+\.\d+\.\d+)", result)
        if match:
            return match.group(1)  # Return the first IP address found
        else:
            raise ValueError(f"No IP address found for service '{service_name}'")
    except CalledProcessError:
        raise RuntimeError(
            f"Failed to run 'getent hosts {service_name}'. Is the service name correct?"
        )
    except Exception as e:
        raise RuntimeError(f"Error resolving IP address for '{service_name}': {e}")


# Resolve destination DNS
if not match(r"(\d+\.\d+\.\d+\.\d+)", dest_addr):
    try:
        dest_addr = get_ip_from_getent(dest_addr)
    except RuntimeError as e:
        print(e)
        exit(1)

# Create tap device
try:
    run(["mkdir", "-p", "/dev/net"], check=True)
    run(["mknod", "/dev/net/tun", "c", "10", "200"], check=True)
    run(["chmod", "600", "/dev/net/tun"], check=True)
except CalledProcessError as e:
    print(f"Error creating tap device: {e}")
    exit(1)

# Create iptables rules
try:
    # traffic from TAP: overwrite dest IP from this to dest_addr
    run(
        ["iptables", "-t", "nat", "-A", "PREROUTING", "-i", tap_name, "-p", "udp"]
        + ["-j", "DNAT", "--to-destination", dest_addr],
        check=True,
    )
    # traffic exiting container: map ns-3 source IPs to local ports
    run(
        ["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "eth0", "-p", "udp"]
        + ["-j", "MASQUERADE", "--to-ports", "40000-50000"],
        check=True,
    )
except CalledProcessError as e:
    print(f"Error creating iptables rules: {e}")
    exit(1)

# Build ns-3 command
try:
    ns3_run = [environ["NS3DIR"] + "/./ns3", "run"]
    options = ["--cwd", environ["OUTPUT"]]
    target = [target_name]
    if "args" in config["run"] and config["run"]["args"]:
        target.append("--")
        target.append("--tapName=" + tap_name)
        for p, v in config["run"]["args"].items():
            if isinstance(v, bool):
                v = int(v)
            target.append("--" + p + "=" + str(v))
except KeyError as e:
    print(f"Environment variable missing: {e}")
    exit(1)

# Run ns-3 simulation
try:
    p = Popen(ns3_run + options + target)

    # Propagate SIGTERM from docker stop
    def propagate_and_sleep(*_):
        p.send_signal(SIGTERM)
        sleep(0.1)

    signal(SIGTERM, propagate_and_sleep)
    p.wait()
except KeyboardInterrupt:
    # Ctrl-C on docker run ends up here.
    exit(0)
except CalledProcessError as e:
    print(f"Error running ns-3 simulation: {e}")
    exit(1)
except Exception as e:
    print(f"Unexpected error during simulation: {e}")
    exit(1)
