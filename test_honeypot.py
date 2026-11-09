import os
import unittest
from app import app, LOG_FILE
from monitor_honeypot import parse_log_line

class HoneypotTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Organisation Management', response.data)
        self.assertIn(b'Admin Login', response.data)

    def test_login_page_get(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username:', response.data)
        self.assertIn(b'Password:', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data={'username': 'wrong', 'password': 'bad'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

    def test_login_valid_credentials(self):
        response = self.client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/admin'))

    def test_admin_dashboard(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)
        self.assertIn(b'List Files', response.data)
        self.assertIn(b'Who Am I', response.data)
        self.assertIn(b'Disk Usage', response.data)

    def test_logout(self):
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))

    def test_vulnerable_no_cmd(self):
        response = self.client.get('/vulnerable')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No command provided', response.data)

    def test_vulnerable_with_cmd(self):
        # Test with echo or whoami which works across platforms
        response = self.client.get('/vulnerable?cmd=whoami')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Command Output', response.data)
        # Check that log file exists and contains the command log
        self.assertTrue(os.path.exists(LOG_FILE))
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            self.assertIn('Received command: whoami', content)

    def test_log_parser_http(self):
        sample_log = '2026-11-09 23:15:00,123 - 127.0.0.1 - - [09/Nov/2026 23:15:00] "GET /login HTTP/1.1" 200 -'
        timestamp, ip, method, path, status, reason, cmd, out = parse_log_line(sample_log)
        self.assertEqual(timestamp, '2026-11-09 23:15:00,123')
        self.assertEqual(ip, '127.0.0.1')
        self.assertEqual(method, 'GET')
        self.assertEqual(path, '/login')
        self.assertEqual(status, '200')

    def test_log_parser_command(self):
        sample_log = '2026-11-09 23:15:01,456 - Received command: whoami'
        timestamp, ip, method, path, status, reason, cmd, out = parse_log_line(sample_log)
        self.assertEqual(timestamp, '2026-11-09 23:15:01,456')
        self.assertEqual(cmd, 'whoami')

    def test_log_parser_command_multiword(self):
        sample_log = '2026-11-09 23:15:02,789 - Received command: cat /etc/passwd'
        timestamp, ip, method, path, status, reason, cmd, out = parse_log_line(sample_log)
        self.assertEqual(timestamp, '2026-11-09 23:15:02,789')
        self.assertEqual(cmd, 'cat /etc/passwd')

    def test_log_parser_command_output(self):
        sample_log = '2026-11-09 23:15:03,101 - Command output: root'
        timestamp, ip, method, path, status, reason, cmd, out = parse_log_line(sample_log)
        self.assertEqual(timestamp, '2026-11-09 23:15:03,101')
        self.assertEqual(out, 'root')

    def test_end_to_end_log_processing(self):
        # Generate an HTTP request and command execution
        self.client.get('/login')
        self.client.get('/vulnerable?cmd=whoami')
        
        # Read the generated honeypot.log
        self.assertTrue(os.path.exists(LOG_FILE))
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        parsed_entries = [parse_log_line(line.strip()) for line in lines]
        valid_entries = [e for e in parsed_entries if any(e)]
        
        # Ensure we captured both HTTP traffic and command traffic
        commands_found = [e[6] for e in valid_entries if e[6] is not None]
        http_paths_found = [e[3] for e in valid_entries if e[3] is not None]
        
        self.assertIn('whoami', commands_found)
        self.assertIn('/login', http_paths_found)

if __name__ == '__main__':
    unittest.main()
