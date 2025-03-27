import socket
import os
import json
import struct
import time
"""
От клиента может прийти только один тип сообщений:
1 + строка  - это команда от клиента (HELP, UPDATE,...)

От сервера к клиенту может прийти два вида ответов:
2 + строка - ответ на команду
3 + бинарные данные  - содержимое файла состояния (env + executables)
"""
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

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

        



class MyServer():

    def __init__(self, host="0.0.0.0", port=4200):
        self.host = host
        self.port = port
        self.update_info()

    def get_executables(self):
        """Анализирует PATH и собирает список исполняемых файлов"""
        path_dirs = os.getenv("PATH", "").split(os.pathsep)
        executables = {}
        
        for directory in path_dirs:
            if os.path.isdir(directory):
                try:
                    files = [f for f in os.listdir(directory) if os.access(os.path.join(directory, f), os.X_OK)]
                    executables[directory] = files
                except PermissionError:
                    executables[directory] = []
        
        return executables

    
    def save_to_json(self, filename="state.json"):
        """Сохраняет данные в JSON-файл"""
        state = {}
        state["env"] = dict(self.env)
        state["exe"] = self.executables
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)

    

    def update_info(self):
        self.env = os.environ
        self.executables = self.get_executables()
        self.save_to_json()





    def client_work(self, conn):
        while True:
            try:
                data = recv_exactly(conn, 8)
            except TimeoutError as e:
                print("TimeOut:", e)
                continue
            except ConnectionError as e:
                print("Ошибка:", e)
                break

            cmd,length = struct.unpack("II", data)

            if cmd != CMD_CLIENT_REQUEST:
                conn.sendall('Неизвестная команда\n'.encode())
                continue
            data = recv_exactly(conn, length)
            data = struct.unpack(f"{length}s", data)[0].decode().strip()

            response = f"Вы ввели: {data}\n"
            print(response)

            if data == "ENV":
                for key, value in self.env.items():
                    response += f"{key}: {value}\n"
            elif data == "EXE":
                response += str(self.executables)
            elif data ==  "UPDATE":
                self.update_info() 
                response += "Информация обновлена"
            elif data == "GET_FILE":
                file_data = read_file("state.json")
                response = struct.pack("IIs", CMD_FILE, len(file_data), file_data)
                conn.sendall(response)
                continue
            elif data == "HELP":
                response += """
Список комнанд: 
0. HELP -- справка
1. UPDATE -- обновление информации на сервере
2. GET_FILE -- получеие файла с информацией 
3. SET -- установка перемнной окружения                         
"""
            else: 
                response += "Неизвестная команда. Используйте HELP для справки"
            print("Отправляю ответ")
            print(response)
            response = struct.pack(f'II{len(response)}s', CMD_SERVER_RESPONSE, len(response), response.encode())
            print(f"Отправляю {len(response)} упакованных байтов")
            conn.sendall(response)
          



    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()
            print(f"Server listening on {self.host}:{self.port}")
            
            while True:
                conn, addr = server.accept()
                with conn:
                    self.client_work(conn)

def main():
    server = MyServer()
    server.start_server()
    pass

if __name__ == "__main__":
    main()

