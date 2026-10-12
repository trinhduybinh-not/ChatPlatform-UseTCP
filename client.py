"""
CHAT CLIENT (TCP) - Kết nối tới server để chat
Chạy: python client.py [địa_chỉ_server]
Ví dụ: python client.py 192.168.1.10
"""
import socket
import sys
import threading

SERVER_HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 1024


def receive_messages(sock):
    """Luồng nhận tin nhắn từ server và in ra màn hình."""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("\nServer đã đóng kết nối.")
                break
            print(data.decode("utf-8"), end="", flush=True)
        except OSError:
            break
    sock.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Không kết nối được tới server. Hãy chắc chắn server đang chạy.")
        return

    # Luồng riêng để nhận tin, luồng chính để nhập và gửi tin
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            sock.sendall(msg.encode("utf-8"))
            if msg == "/quit":
                break
    except (KeyboardInterrupt, EOFError, OSError):
        pass
    finally:
        try:
            sock.sendall(b"/quit")
        except OSError:
            pass
        sock.close()
        print("Đã thoát chat.")


if __name__ == "__main__":
    main()
