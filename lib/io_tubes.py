import hashlib
import ipaddress
import json
import logging
import os
import re
import sys
import tempfile
from datetime import datetime


def get_default(io_dict):
    if not any(val for val in io_dict.values()):
        raise ValueError(f"No True value found in the dictionary {io_dict}")
    return next(key for key, val in io_dict.items() if val == True)

def parse(parser, in_format, out_format):
    parser.add_argument('--in_format',"-in_for", type=str, default=get_default(in_format))
    parser.add_argument('--out_format',"-out_for", type=str, default=get_default(out_format))

# "valid" -> can be automatically converted, no conversion needed
# True -> base, default format
def change_input(in_format, in_dict):
    conv_in_format = in_format
    while in_dict.get(conv_in_format) not in {True, "valid"}:
        conv_in_format = in_dict[conv_in_format]
    if conv_in_format != in_format:
        logging.info(f"{in_format}-> {conv_in_format}")
        #temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(sys.stdin.read().encode())

        convert_to_format(tmp_file_path,in_format, conv_in_format)
        sys.stdin = open(tmp_file_path, 'r')

def calculate_md5_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def expand_ip_ranges(tmp_file_path):
    def ip_generator(file):
        for line in file:
            line = line.strip()
            if '-' in line:
                start_ip, end_ip = map(ipaddress.IPv4Address, line.split('-'))
                for ip_int in range(int(start_ip), int(end_ip) + 1):
                    yield f"{ipaddress.IPv4Address(ip_int)}\n"
            elif '/' in line:
                network = ipaddress.ip_network(line, strict=False)
                for ip in network.hosts():
                    yield f"{ip}\n"
            else:
                yield f"{line}\n"

    with open(tmp_file_path, 'r') as file:
        with open(tmp_file_path + '.tmp', 'w') as tmp_file:
            for ip in ip_generator(file):
                tmp_file.write(ip)

    os.replace(tmp_file_path + '.tmp', tmp_file_path)


def create_metadata_file(tmp_folder_path):
    metadata = {
        "create_date": datetime.now().isoformat()
    }
    metadata_path = os.path.join(tmp_folder_path, 'metadata.json')
    with open(metadata_path, 'w') as metadata_file:
        json.dump(metadata, metadata_file)

def get_ranges_hash(ranges):
    ranges_str = ''.join([str(r) for r in ranges])
    hash_md5 = hashlib.md5(ranges_str.encode())
    return hash_md5.hexdigest()

def convert_to_format(tmp_file_path, in_format, conv_format):
    if (in_format, conv_format) == ("RANGES_TXT", "SCAN_FOLDER"):
        convert_to_format(tmp_file_path, "RANGES_TXT", "IP_TXT")
        convert_to_format(tmp_file_path, "IP_TXT", "SCAN_FOLDER")
    if (in_format,conv_format) == ("RANGES_TXT","IP_TXT"):
        expand_ip_ranges(tmp_file_path)
    if (in_format, conv_format) == ("IP_TXT", "SCAN_FOLDER"):
        base_dir = os.path.dirname(__file__)
        scans_dir = os.path.join(base_dir, '../scans')
        chunks_dir = os.path.join(scans_dir, 'chunks')
        os.makedirs(chunks_dir, exist_ok=True)

        CHUNK_SIZE = 1000
        chunk_count = 0

        file = sys.stdin if tmp_file_path is None else open(tmp_file_path, 'r')

        with file:
            while True:
                lines = [file.readline() for _ in range(CHUNK_SIZE)]
                lines = [line for line in lines if line]  # Remove empty lines

                if not lines:
                    break

                # Create tmp folder for the current chunk
                tmp_folder_path = os.path.join(chunks_dir, f"tmp_{chunk_count}")
                os.makedirs(tmp_folder_path, exist_ok=True)

                # Convert lines to IP ranges
                ip_list = [ipaddress.IPv4Address(ip.strip()) for ip in lines]
                ranges = list(ipaddress.collapse_addresses(ip_list))

                # Calculate MD5 hash of the ranges
                ranges_str = [str(r) for r in ranges]
                hash_name = get_ranges_hash(ranges_str)
                target_path = os.path.join(chunks_dir, hash_name)

                if os.path.exists(target_path):
                    logging.warning(f"Directory not empty: {target_path}")
                else:
                    # Add ranges to metadata.json
                    metadata = {
                        "create_date": datetime.now().isoformat(),
                        "ranges": ranges_str
                    }
                    metadata_path = os.path.join(tmp_folder_path, 'metadata.json')
                    with open(metadata_path, 'w') as metadata_file:
                        json.dump(metadata, metadata_file)

                    os.rename(tmp_folder_path, target_path)

                chunk_count += 1

        with open(tmp_file_path, 'w') as file:
            file.write(f"{scans_dir}\n")
    return tmp_file_path


def parse_time_limit(time_limit_str):
    if time_limit_str is None:
        return None
    time_formats = {
        's': 1,        # seconds
        'm': 60,       # minutes
        'h': 3600,     # hours
        'd': 86400,    # days
        'w': 604800,   # weeks
        'y': 31536000  # years
    }

    match = re.match(r'^(\d+(\.\d+)?)([smhdyw]?)$', time_limit_str)
    if not match:
        raise ValueError("Invalid time format. Use <number><s|m|h|d|w|y> (e.g., 30s, 5m, 2h, 1d, 1w, 1y).")

    value, _, unit = match.groups()
    unit = unit if unit else 's'  # Default to seconds if no unit is provided
    return float(value) * time_formats[unit]