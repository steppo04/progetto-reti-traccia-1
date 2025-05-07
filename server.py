from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
import os
import mimetypes
import logging
from datetime import datetime

# configurazione server
HOST = ''
PORT = 8080
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')
LOG_FILE = os.path.join(BASE_DIR, 'server_requests.log')

# configuriamo il file di logging 
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((HOST, PORT))
serverSocket.listen(1)
print(f"The web server is up on port: {PORT}")
logging.info(f"Server started on port {PORT}")

# introduzione del mimetypes per riconoscere i vari tipi di file
mimetypes.init()

def get_content_type(file_path):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

while True:
    logging.info("Waiting for new connection...")
    connectionSocket, addr = serverSocket.accept()
    client_ip, client_port = addr
    print(f"Connection from {addr}")
    logging.info(f"Connection accepted from {client_ip}:{client_port}")
    try:
        request = connectionSocket.recv(1024).decode()
        if not request:
            connectionSocket.close()
            logging.warning(f"Empty request from {client_ip}:{client_port}, connection closed")
            continue

        request_line = request.splitlines()[0]
        parts = request_line.split()
        if len(parts) < 2 or parts[0] != 'GET':
            connectionSocket.close()
            logging.warning(f"Invalid request line from {client_ip}:{client_port}: {request_line}")
            continue

        method, raw_path = parts[0], parts[1]
        path = raw_path.split('?', 1)[0]
        logging.info(f"Request: {method} {path} from {client_ip}:{client_port}")

        if path == '/':
            path = '/trails.html'

        filename = path.lstrip('/')  
        file_path = os.path.join(BASE_DIR, filename)

        # Verifica solo l'esistenza del file senza controlli di percorso
        if not os.path.exists(file_path):
            status_line = 'HTTP/1.1 404 Not Found'
            body = (f"<html><body><h1>404 Not Found</h1>"
                    f"<p>No page for {path}</p></body></html>")
            response = f"{status_line}\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{body}".encode('utf-8')
            logging.info(f"Response to {client_ip}:{client_port}: 404 Not Found for {path}")
        else:
            with open(file_path, 'rb') as f:
                body = f.read()
            content_type = get_content_type(file_path)
            status_line = 'HTTP/1.1 200 OK'
            headers = [
                status_line,
                f'Content-Type: {content_type}; charset=utf-8',
                f'Content-Length: {len(body)}',
                '\r\n'
            ]
            header = '\r\n'.join(headers).encode('utf-8')
            response = header + body
            logging.info(f"Response to {client_ip}:{client_port}: 200 OK, served {filename}")

        connectionSocket.sendall(response)
    except Exception as e:
        logging.error(f"Error handling request from {client_ip}:{client_port}: {e}")
        print(f"Error: {e}")
    finally:
        connectionSocket.close()
        logging.info(f"Connection closed for {client_ip}:{client_port}")

serverSocket.close()
sys.exit()
