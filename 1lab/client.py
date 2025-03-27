import socket
#import readline
import struct
import time
from datetime import datetime

HOST = "127.0.0.1"
PORT = 4200

CMD_CLIENT_REQUEST = 1
CMD_SERVER_RESPONSE = 2
CMD_FILE = 3

def recv_exactly(sock, size, timeout=5):
    """Принимает ровно `size` байт через сокет, ожидая при необходимости, но не дольше `timeout` секунд."""
    sock.settimeout(timeout)  # Устанавливаем таймаут на операции recv()
    data = b""
    start_time = time.time()

    while len(data) < size:
        try:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Соединение закрыто до получения всех данных.")
            data += chunk
        except socket.timeout:
            raise TimeoutError(f"Превышен таймаут {timeout} сек, получено {len(data)} байт.")

        # Проверяем, не вышло ли время ожидания
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Превышен таймаут {timeout} сек, получено {len(data)} байт.")

    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    try:
        client.connect((HOST, PORT))
        print(f"Подключено к {HOST}:{PORT}. Введите команды (Ctrl+C для выхода).")

        while True:
            try:
                cmd = input("> ")
                if not cmd:
                    continue
                client_data = struct.pack(f'II{len(cmd)}s', CMD_CLIENT_REQUEST, len(cmd), cmd.encode())
                client.sendall(client_data)
                data = recv_exactly(client,8)
                cmd,length = struct.unpack("II", data)
                if cmd == CMD_SERVER_RESPONSE:
                    data = recv_exactly(client,length)
                    data = struct.unpack(f"{length}s", data)[0]
                    print("Ответ сервера: ", data.decode(), end="")
                elif cmd == CMD_FILE: 
                    data = recv_exactly(client,length)
                    filename = datetime.now().strftime("%Y%m%d%H%M%S")+"-state.json"
                    print(f"Сервер прислал файл. Сохраняю в {filename}")
                    with open(filename, 'wb') as file:
                        file.write(data)
                else: 
                    print("Неизвестный ответ сервера")

            except KeyboardInterrupt:
                print("\nОтключение...")
                break

    except ConnectionRefusedError:
        print("Ошибка: не удалось подключиться к серверу.")
