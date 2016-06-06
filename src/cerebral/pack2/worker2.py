from cerebral import logger as l
import logging


from cerebral.pack2.hippocampus import Android, Crossbar
from theia.eye import Eye
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer
from cerebral.nameserver import ports
import cv2
import ssl
import os
import socket


# Logging.
logger = logging.getLogger('universe')

# Get camera and connect.
camera = Android.camera
eye = Eye(camera)


class ThreadedServer(ThreadingMixIn, HTTPServer):
    pass


class CameraHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()

            frame = eye.get_color_frame()

            # Early exit condition.
            if frame is None:
                return

            encode_param = (cv2.IMWRITE_JPEG_QUALITY, 80)
            data = cv2.imencode('.jpg', frame, encode_param)[1]
            data = data.tobytes()

            self.wfile.write(data)
        except ConnectionAbortedError:
            pass

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    port = ports['worker2']

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((Crossbar.ip, 443))  # connecting to a UDP address doesn't send packets
    ip = s.getsockname()[0]

    server = ThreadedServer((ip, port), CameraHandler)

    script_dir = os.path.dirname(__file__)
    certfile = os.path.join(script_dir, 'server.cer')
    keyfile = os.path.join(script_dir, 'server.pkey')
    server.socket = ssl.wrap_socket(server.socket, certfile=certfile, keyfile=keyfile, server_side=True)

    # Log server event.
    logger.info('Worker 2 started!')

    server.serve_forever()

