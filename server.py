"""
CHAT SERVER (TCP) - Mô hình client-server, hỗ trợ nhiều client bằng threading
Chạy: python server.py
"""
import socket
import threading

HOST = "0.0.0.0"   # Lắng nghe trên mọi địa chỉ IP của máy
PORT = 5555        # Cổng kết nối
BUFFER_SIZE = 1024

clients = {}                 # {socket: tên người dùng}
clients_lock = threading.Lock()  # Khóa tránh xung đột khi nhiều luồng cùng sửa dict


def broadcast(message, sender=None):
    """Gửi message tới tất cả client (trừ người gửi nếu có sender)."""
    with clients_lock:
        for conn in list(clients):
            if conn is sender:
                continue
            try:
                conn.sendall(message.encode("utf-8"))
            except OSError:
                # Client đã mất kết nối -> xóa khỏi danh sách
                clients.pop(conn, None)
                conn.close()


def handle_client(conn, addr):
    """Luồng xử lý riêng cho từng client."""
    name = None
    try:
        # Bước 1: nhận tên người dùng
        conn.sendall("Nhập tên của bạn: ".encode("utf-8"))
        name = conn.recv(BUFFER_SIZE).decode("utf-8").strip() or f"{addr[0]}:{addr[1]}"

        with clients_lock:
            clients[conn] = name
        print(f"[+] {name} đã kết nối từ {addr}")
        conn.sendall(f"Chào {name}! Gõ /list xem người online, /quit để thoát.\n".encode("utf-8"))
        broadcast(f"*** {name} đã tham gia phòng chat ***\n", sender=conn)

        # Bước 2: vòng lặp nhận tin nhắn
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:          # Client đóng kết nối
                break
            msg = data.decode("utf-8").strip()
            if not msg:
                continue
            if msg == "/quit":
                break
            if msg == "/list":
                with clients_lock:
                    online = ", ".join(clients.values())
                conn.sendall(f"Đang online: {online}\n".encode("utf-8"))
                continue
            print(f"[{name}] {msg}")
            broadcast(f"[{name}]: {msg}\n", sender=conn)
    except (ConnectionResetError, OSError):
        pass
    finally:
        # Bước 3: dọn dẹp khi client rời đi
        with clients_lock:
            clients.pop(conn, None)
        conn.close()
        if name:
            print(f"[-] {name} đã ngắt kết nối")
            broadcast(f"*** {name} đã rời phòng chat ***\n")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server đang chạy tại cổng {PORT}... (Ctrl+C để dừng)")

    try:
        while True:
            conn, addr = server.accept()  # Chờ client mới
            # Mỗi client được xử lý bởi 1 luồng riêng
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nĐang tắt server...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
