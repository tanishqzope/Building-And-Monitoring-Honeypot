import os
import time
import re

def tail_f(filename, interval=1.0, from_beginning=False):
    """Tails a file in real-time."""
    if not os.path.exists(filename):
        # Create empty log file if it doesn't exist yet
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as f:
            pass

    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        if not from_beginning:
            # Go to the end of the file
            f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(interval)
                continue
            yield line

def parse_log_line(line):
    """Parses a log line and extracts relevant information."""
    log_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - - \[(.*?)\] \"(\S+) (\S+) HTTP/(\S+)\" (\d+) (\S+)"
    command_pattern = r"(?:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - )?Received command:\s*(.+)"
    command_output_pattern = r"(?:(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - )?Command output:\s*(.*)"

    match = re.search(log_pattern, line)
    if match:
        timestamp, ip_address, request_time, method, path, http_version, status, reason = match.groups()
        command = None
        command_output = None
        return timestamp, ip_address, method, path, status, reason, command, command_output

    match = re.search(command_pattern, line)
    if match:
        timestamp, command = match.groups()
        return timestamp, None, None, None, None, None, command, None

    match = re.search(command_output_pattern, line)
    if match:
        timestamp, command_output = match.groups()
        return timestamp, None, None, None, None, None, None, command_output

    return None, None, None, None, None, None, None, None

def print_table_header(column_widths):
    """Prints the table header with dynamic column widths."""
    header_row = ""
    separator_row = ""
    for column, width in column_widths.items():
        header_row += f"{column:<{width}} | "
        separator_row += f"{'-' * width}-+-"
    print(header_row[:-3])  # Remove trailing ' | '
    print(separator_row[:-3])

def colorize_output(output_line, status):
    """Colorizes the output line based on status code."""
    if status == '404':
        return f"\033[93m{output_line}\033[0m"  # Yellow for 404
    elif status in ('401', '403'):
        return f"\033[91m{output_line}\033[0m"  # Red for 401/403
    elif status == '200':
        return f"\033[92m{output_line}\033[0m"  # Green for 200
    return output_line

def monitor_log_file(logfile):
    """Monitors the log file and prints new entries in a table format."""
    print(f"Monitoring {logfile} for new entries...\n")

    column_names = ["Timestamp", "IP Address", "Method", "Path", "Status", "Reason", "Command", "Command Output"]
    column_widths = {column: len(column) for column in column_names}
    
    # Print header once
    print_table_header(column_widths)

    for line in tail_f(logfile):
        line = line.strip()
        timestamp, ip_address, method, path, status, reason, command, command_output = parse_log_line(line)
        
        if any((timestamp, ip_address, method, path, status, reason, command, command_output)):
            # Update column widths dynamically
            for column, value in zip(column_names, (timestamp, ip_address, method, path, status, reason, command, command_output)):
                if value:
                    column_widths[column] = max(column_widths[column], len(str(value)))
            
            # Build output line
            output_line = ""
            for column in column_names:
                value = locals().get(column.lower().replace(" ", "_"))
                output_line += f"{str(value) if value else '':<{column_widths[column]}} | "
            output_line = output_line[:-3]  # Remove trailing ' | '

            # Colorize based on status
            output_line = colorize_output(output_line, status)
            print(output_line)

if __name__ == "__main__":
    # Path to your honeypot log file
    log_file_path = os.environ.get('HONEYPOT_LOG')
    if not log_file_path:
        if os.path.exists('/var/log/honeypot.log'):
            log_file_path = '/var/log/honeypot.log'
        else:
            log_file_path = os.path.abspath('honeypot.log')

    monitor_log_file(log_file_path)
