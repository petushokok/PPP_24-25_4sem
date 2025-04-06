import socket
import struct
import time
from datetime import datetime
import sys

CMD_CLIENT_REQUEST = 1
CMD_SERVER_RESPONSE = 2
CMD_FILE = 3


def recv_exactly(sock, size, timeout=5):
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

def client_main(host='127.0.0.1', port=4200):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((host, port))
            print(f"Подключено к {host}:{port}. Введите команды (Ctrl+C для выхода).")

            while True:
                try:
                    cmd = input("> ")
                    if not cmd:
                        continue
                    cmd_encoded = cmd.encode()
                    client_data = struct.pack(f'II{len(cmd_encoded)}s', CMD_CLIENT_REQUEST, len(cmd_encoded), cmd_encoded)
                    client.sendall(client_data)
                    data = recv_exactly(client, 8)
                    cmd, length = struct.unpack("II", data)
                    if cmd == CMD_SERVER_RESPONSE:
                        data = recv_exactly(client, length)
                        data = struct.unpack(f"{length}s", data)[0].decode()
                        print("Ответ сервера:")
                        print(data)
                    elif cmd == CMD_FILE:
                        data = recv_exactly(client, length)
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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        client_main(host=sys.argv[1])
    elif len(sys.argv) == 3:
        client_main(host=sys.argv[1], port=int(sys.argv[2]))
    else:
        client_main()
