import os
import socket
import threading
import subprocess
import paramiko
from paramiko import RSAKey
from paramiko.sftp_server import (
    SFTPServerInterface, SFTPAttributes,
    SFTP_OK, SFTP_FAILURE, SFTP_NO_SUCH_FILE
)

# 1) إنشاء مفتاح مضيف ثابت في ملف host_key.pem
KEY_FILE = "host_key.pem"
if os.path.exists(KEY_FILE):
    host_key = RSAKey(filename=KEY_FILE)
else:
    host_key = RSAKey.generate(2048)
    host_key.write_private_key_file(KEY_FILE)

# 2) SFTP interface بسيط لإدارة الملفات في المجلد الحالي
class SimpleSFTP(SFTPServerInterface):
    def __init__(self, server, *args, **kwargs):
        super().__init__(server, *args, **kwargs)
        self.root = os.getcwd()
    def _full_path(self, path):
        if path.startswith("/"):
            path = path[1:]
        return os.path.join(self.root, path)
    def list_folder(self, path):
        p = self._full_path(path)
        try:
            names = os.listdir(p)
        except OSError:
            return SFTP_NO_SUCH_FILE
        out = []
        for name in names:
            fp = os.path.join(p, name)
            try:
                st = os.stat(fp)
            except OSError:
                continue
            attr = SFTPAttributes.from_stat(st)
            attr.filename = name
            out.append(attr)
        return out
    def stat(self, path):
        try:
            st = os.stat(self._full_path(path))
            return SFTPAttributes.from_stat(st)
        except OSError:
            return SFTP_NO_SUCH_FILE
    def open(self, path, flags, attr):
        mode = "rb"
        if flags & os.O_WRONLY: mode = "wb"
        elif flags & os.O_RDWR:  mode = "r+b"
        try:
            return open(self._full_path(path), mode)
        except OSError:
            return SFTP_FAILURE
    def remove(self, path):
        try:
            os.remove(self._full_path(path))
            return SFTP_OK
        except OSError:
            return SFTP_FAILURE
    def rename(self, old, new):
        try:
            os.rename(self._full_path(old), self._full_path(new))
            return SFTP_OK
        except OSError:
            return SFTP_FAILURE
    def mkdir(self, path, attr):
        try:
            os.mkdir(self._full_path(path))
            return SFTP_OK
        except OSError:
            return SFTP_FAILURE
    def rmdir(self, path):
        try:
            os.rmdir(self._full_path(path))
            return SFTP_OK
        except OSError:
            return SFTP_FAILURE

# 3) ServerInterface بدون مصادقة، يسمح بكل القنوات
class NoAuthServer(paramiko.ServerInterface):
    def check_auth_none(self, username):
        return paramiko.AUTH_SUCCESSFUL
    def get_allowed_auths(self, username):
        return "none"
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    def check_channel_shell_request(self, channel):
        return True
    def check_channel_subsystem_request(self, channel, name):
        if name == "sftp":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED

# 4) معالج جلسة الشل التفاعلية
def shell_handler(chan):
    chan.send(b"*** SSH Shell (no-auth) ready ***\n")
    while True:
        chan.send(b"$ ")
        cmd = chan.recv(1024).decode("utf-8", "ignore").strip()
        if not cmd or cmd.lower() == "exit":
            chan.send(b"Goodbye!\n")
            break
        try:
            out = subprocess.check_output(
                cmd, shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
        except subprocess.CalledProcessError as e:
            out = e.output or f"Error executing: {cmd}\n"
        if not out:
            out = "Command executed.\n"
        chan.send(out.encode("utf-8"))
    chan.close()

# 5) دالة تشغيل الخادم
def start_server(host="0.0.0.0", port=2122):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(50)
    print(f"[+] SSH/SFTP no-auth server listening on {host}:{port}")

    while True:
        client, addr = sock.accept()
        print(f"[+] Connection from {addr}")
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler("sftp", paramiko.SFTPServer, SimpleSFTP)
        server = NoAuthServer()
        try:
            transport.start_server(server=server)
        except Exception as e:
            print(f"[!] SSH negotiation failed: {e}")
            client.close()
            continue

        chan = transport.accept(20)
        if chan is None:
            print("[!] No channel.")
            continue

        threading.Thread(target=shell_handler, args=(chan,), daemon=True).start()

if __name__ == "__main__":
    start_server()
