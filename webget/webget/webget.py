import socket
#t3
import sys
#t3
def main():
    # T3：命令行参数解析
    if len(sys.argv) < 3:
        print("用法：python webget.py host path [port]")
        print("示例：python webget.py www.bjfu.edu.cn / 80")
        return
    host = sys.argv[1]
    path = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) >= 4 else 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)  # T1：10秒超时
#t3注释掉
#host = "www.bjfu.edu.cn"
#port = 80
    s.connect((host, port))

# 带上 Connection: close
#req = b"GET / HTTP/1.1\r\nHost: www.bjfu.edu.cn\r\nConnection: close\r\n\r\n"
    req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
    s.sendall(req)

    buf = b""
    count = 0
    record = []
    content_len = None

    while True:
       chunk = s.recv(4096)
       count += 1
       record.append(len(chunk))
       if not chunk:
            break
       buf += chunk

    # 解析Content-Length
       if content_len is None and b"\r\n\r\n" in buf:
            header = buf.split(b"\r\n\r\n")[0]
            for line in header.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    content_len = int(line.split(b":")[1].strip())
    
    # 收够内容就退出
       if content_len is not None:
            header_end = buf.find(b"\r\n\r\n") + 4
            body_len = len(buf) - header_end
            if body_len >= content_len:
                break

# T1：把 recv放进循环，直到收完。结束条件只有两种：响应头里有Content-Length，就照它收够为止；没有就收到对端关闭为止（所以请求里要带
#Connection: close）。给socket设settimeout(10)，防止挂在坏服务器上。
    print("完整响应")
    print(buf.decode("utf-8", errors="ignore"))
    print("\nrecv统计")
    print(f"recv调用次数：{count}")
    for i, n in enumerate(record, 1):
        print(f"第{i}次recv：{n} 字节")
#T2：按空行把状态行、响应头、body分开。打印状态码和全部响应头；body用二进制模式（wb）写文件保存。
    split_pos = buf.find(b"\r\n\r\n")
    header_bytes = buf[:split_pos]
    body_bytes = buf[split_pos + 4:]
# 解析状态码
    status_line = header_bytes.split(b"\r\n")[0].decode("utf-8", errors="ignore")
    status_code = status_line.split()[1]

    print("\n状态码 ")
    print(status_code)
    print("\n 全部响应头")
    print(header_bytes.decode("utf-8", errors="ignore"))

# 二进制wb保存body
    with open("body.bin", "wb") as f:
        f.write(body_bytes)
    print("\nbody 已经保存到 body.bin")

    s.close()
if __name__ == "__main__":
    main()