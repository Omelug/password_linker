import argparse
import ipaddress
import json
import logging
import os
import subprocess
import sys
import time

from gevent.testing import skipUnless

from lib import io_tubes

__author__ = 'Omelug'
__date__ = '2024'
__description__ = """Scaners nmap,brutespray"""

__in_format__ = {"RANGES_TXT": "IP_TXT", "IP_TXT":"SCAN_FOLDER", "SCAN_FOLDER": True}
__out_format__ = {"TXT_LIST": True}

ARGS = None

default_ports = {
    "mysql": {3306},
    "ssh": {22},
    "http": {80, 443},
    "postgres": {5432}
}

def get_args(args):
    parser = argparse.ArgumentParser()
    io_tubes.parse(parser, __in_format__, __out_format__)
    #parser.add_argument('--chunk', type=str, help="Scan only one chunk")
    parser.add_argument('--service', type=str, help="Service to scan", required=True)
    parser.add_argument('--time_limit', type=str, default=None)
    parser.add_argument('--nmap', action="store_true", help="Arguments for nmap",default=None)
    parser.add_argument('--brutespray', action="store_true", default=None)
    parser.add_argument('--masscan', action="store_true", default=None)
    parser.add_argument('--openssh_scanner', action="store_true", default=None)
    return parser.parse_args(args)

def ips_to_ranges(ip_file_path):
    with open(ip_file_path, 'r') as file:
        ips = [line.strip() for line in file.readlines()]

    ip_list = [ipaddress.IPv4Address(ip) for ip in ips]
    ranges = ipaddress.collapse_addresses(ip_list)
    return ranges

#TODO add conversion support
#https://github.com/dogasantos/masstomap
def get_meta(metadata_path):
    with open(metadata_path, 'r') as metadata_file:
        metadata = json.load(metadata_file)
    return metadata

def run_cmd(command,metadata,run_time,time_limit=None, metadata_path=None, out=False) -> bool: #True if finish
    start_time = time.time()
    cmd_list = metadata.get('commands')
    if cmd_list is None:
        cmd_list = []
    if command not in cmd_list:
        print(command, file=sys.stderr)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if out:
            stdout = result.stdout
            stderr = result.stderr

            # Print the outputs
            print("Standard Output:")
            print(stdout)

            print("Standard Error:")
            print(stderr)

    metadata['commands'] = cmd_list.append(command)

    end_time = time.time()
    time_duration = end_time - start_time

    run_time += time_duration

    if metadata_path is not None:
        with open(metadata_path, 'w') as file:
            json.dump(metadata, file, indent=4)
    if time_limit is not None and run_time > time_limit:
        return True
    return False

def run(args, config=None):
    script_name = os.path.basename(__file__)
    logging.info(f"--> {script_name}")
    global ARGS
    ARGS = get_args(args[2:])
    io_tubes.change_input(ARGS.in_format,__in_format__)

    ARGS.time_limit = io_tubes.parse_time_limit(ARGS.time_limit)

    base_dir = os.path.dirname(__file__)
    scans_dir = os.path.join(base_dir, '../../scans')
    chunks_dir = os.path.join(scans_dir, 'chunks')

    run_time = 0
    for chunk_folder in os.listdir(chunks_dir):
        chunk_folder_path = os.path.join(chunks_dir, chunk_folder)
        if not os.path.isdir(chunk_folder_path):
            raise FileNotFoundError(f"Chunk folder {chunk_folder_path} not found")

        metadata_path = os.path.join(chunk_folder_path, 'metadata.json')
        metadata = get_meta(metadata_path)
        ranges_str = ' '.join(metadata['ranges'])
        ports_str = ','.join(map(str, default_ports.get(ARGS.service)))

        if ARGS.nmap:
            nmap_out = f"{chunk_folder_path}/nmap_{ARGS.service}.xml"
            command = f"nmap {ranges_str} -p {ports_str} -oX {nmap_out} -T3"
            if not os.path.exists(nmap_out):
                print(".", file=sys.stderr, end="")
                continue
            if run_cmd(command, metadata, run_time, time_limit=ARGS.time_limit, metadata_path=metadata_path):
                break

        if ARGS.brutespray:
            nmap_out = f"{chunk_folder_path}/nmap_{ARGS.service}.xml"
            brute_out = f"{chunk_folder_path}/brutespray_{ARGS.service}.txt"
            if not os.path.exists(nmap_out) or os.path.exists(brute_out):
                print(".", file=sys.stderr, end="")
                continue
            command = f"brutespray -q -f {nmap_out} -C {scans_dir}/lists/{ARGS.service}/default_combo.txt -t 5 | tee {brute_out}"
            if run_cmd(command, metadata, run_time, time_limit=ARGS.time_limit, metadata_path=metadata_path):
                break

        if ARGS.masscan:
            mass_out = f"{chunk_folder_path}/masscan_{ARGS.service}.txt"
            command = f"masscan {ranges_str} -p{ports_str} --rate=10000 > {mass_out}"
            if run_cmd(command, metadata, run_time, time_limit=ARGS.time_limit, metadata_path=metadata_path):
                break
        if ARGS.openssh_scanner:
            mass_out = f"{chunk_folder_path}/masscan_{ARGS.service}.txt"
            mass_out_parsed = f"{chunk_folder_path}/masscan_openssh_parsed.txt"
            if not os.path.exists(mass_out):
                print(".", file=sys.stderr, end="")
                continue
            if not os.path.exists(mass_out_parsed):
                awk_part = "awk '{print $6\":\"$4}'"
                grep_part = "grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+'"
                command = f"cat {mass_out} | {awk_part} | {grep_part} > {mass_out_parsed}"
                subprocess.run(command, shell=True, capture_output=True, text=True)
            open_ssh_out = f"{chunk_folder_path}/open_ssh.out"
            if os.path.exists(open_ssh_out):
                print(".", file=sys.stderr, end="")
                continue
            #TODO external tools
            path = "/root/OpenSSH-Scanner/ssh.py"
            command = f"python3 {path} -f {mass_out_parsed} --output {open_ssh_out} -t 3"
            if run_cmd(command, metadata, run_time, time_limit=ARGS.time_limit, metadata_path=metadata_path, out=True):
                break

def parse_masscan_output(output_file, result_file):
    with open(output_file, 'r') as file:
        data = json.load(file)

    active_ips_ports = []
    for entry in data:
        ip = entry['ip']
        for port_info in entry['ports']:
            port = port_info['port']
            active_ips_ports.append(f"{ip}:{port}")

    with open(result_file, 'w') as file:
        for ip_port in active_ips_ports:
            file.write(f"{ip_port}\n")