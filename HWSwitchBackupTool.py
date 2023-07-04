# coding: utf-8
import time
import pandas as pd
import paramiko
import argparse
from datetime import date


def executeCommand(ip, port, username, password, command):
    # SSH连接
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


    try:
        ssh.connect(ip, port, username, password)
        print(f"成功连接到 {ip}")
        command1 = "screen-length 0 temporary\n"
        # 打开一个SSH的Channel
        channel = ssh.invoke_shell()
        # 发送命令并读取输出
        text = ''
        try:
            # 发送第一个命令
            channel.send(command1)
            time.sleep(1)

            # 循环读取输出，直到没有更多内容可读取
            while channel.recv_ready():
                output = channel.recv(65535).decode()
                text += output
                time.sleep(0.5)
            # 发送第二个命令
            channel.send(command+"\n")
            time.sleep(2)
            # 循环读取输出，直到没有更多内容可读取
            while channel.recv_ready():
                output = channel.recv(65535).decode()
                text += output
                time.sleep(0.5)
            # 关闭SSH连接
            channel.close()
            ssh.close()
            # 保存结果到文件
            with open(f'{ip}_{current_date}.txt', 'w') as file:
                file.write(text)

        except Exception as e:
            text = '获取配置失败！' + str(e)
            print(text)

        # 返回输出结果
        return text

    except paramiko.ssh_exception.AuthenticationException:
        print(f"连接到 {ip} 失败！用户名或密码错误。")


def processCommands(filepath, command):
    # 读取 Excel 表格
    df = pd.read_excel(filepath)

    # 遍历每一行
    for index, row in df.iterrows():
        # 获取连接信息
        ip = str(row['IP'])
        port = int(row['端口'])
        username = str(row['账号'])
        password = str(row['密码'])
        print(ip, port, username, password)

        # 执行命令并获取输出结果
        output = executeCommand(ip, port, username, password, command)

        # 输出结果
        if output:
            print(f"在 {ip} 上执行命令: {command}")
            print("输出结果:")
            print(f"在 {ip} 上执行完毕！！\n")
            print(output)

# 示例调用
if __name__ == '__main__':
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='执行命令并将结果写入文件')
    parser.add_argument('-f', '--file', type=str, help='连接信息的Excel文件路径')
    parser.add_argument('-c', '--command', type=str, help='需要执行的命令')

    # 解析命令行参数
    args = parser.parse_args()

    # 检查参数是否为空
    if not args.file or not args.command:
        parser.print_help()
        exit()

    filepath = args.file
    command = args.command
    # 获取当前日期
    current_date = date.today().strftime("%Y-%m-%d")
    processCommands(filepath, command)
