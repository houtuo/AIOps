# AIOps Agent 部署手册

## 目录
- [系统要求](#系统要求)
- [在线部署](#在线部署)
- [离线部署](#离线部署)
- [配置说明](#配置说明)
- [启动与停止](#启动与停止)
- [故障排除](#故障排除)

---

## 系统要求

### 硬件要求
- **CPU**: 2核或以上
- **内存**: 2GB或以上
- **磁盘**: 500MB可用空间

### 软件要求
- **操作系统**:
  - Linux: CentOS 7+, Ubuntu 18.04+, RHEL 7+
  - Windows: Windows Server 2012+, Windows 10+
- **Python**: 3.8或以上版本
- **网络**:
  - 在线部署需要访问互联网
  - 离线部署需要提前准备依赖包

### 端口要求
- **默认端口**: 8443 (HTTPS)
- 确保防火墙允许该端口的入站连接

---

## 在线部署

### 1. 环境准备

#### Linux环境

```bash
# 检查Python版本
python3 --version  # 应显示 Python 3.8+

# 如果没有Python 3，安装Python 3
# CentOS/RHEL
sudo yum install -y python3 python3-pip

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip
```

#### Windows环境

1. 从 https://www.python.org/downloads/ 下载Python 3.8+安装包
2. 安装时勾选"Add Python to PATH"
3. 验证安装：
```cmd
python --version
```

### 2. 获取源码

```bash
# 方式1：从Git仓库克隆
git clone <repository_url> /opt/aiops-agent
cd /opt/aiops-agent

# 方式2：解压安装包
tar -xzf aiops-agent-1.0.0.tar.gz -C /opt/
cd /opt/aiops-agent
```

### 3. 安装依赖

#### Linux环境

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 如果遇到网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Windows环境

```cmd
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 生成密钥和证书

```bash
# 生成AES密钥、JWT密钥和SSL证书
python scripts/generate_keys.py

# 查看生成的配置
cat config/default.yaml
```

### 5. 启动服务

#### Linux环境

```bash
# 前台启动（用于测试）
python src/server.py

# 后台启动（生产环境）
nohup python src/server.py > logs/server.log 2>&1 &

# 查看进程
ps aux | grep server.py
```

#### Windows环境

```cmd
# 前台启动
python src\server.py

# 后台启动（使用Windows服务或任务计划程序）
pythonw src\server.py
```

### 6. 验证部署

```bash
# 检查健康状态
curl -k https://localhost:8443/health

# 预期输出：
# {"service":"aiops-agent","status":"healthy"}
```

---

## 离线部署

### 1. 准备离线安装包

在有网络的环境中准备依赖包：

```bash
# 创建离线包目录
mkdir -p offline-packages

# 下载Python依赖包
pip download -r requirements.txt -d offline-packages/

# 如果使用预编译的Python环境
# 将Python3.11_redhat7.tar.gz放入offline-packages目录

# 打包整个项目
tar -czf aiops-agent-offline-1.0.0.tar.gz \
    aiops-agent/ \
    offline-packages/
```

### 2. 传输到目标环境

```bash
# 使用scp传输
scp aiops-agent-offline-1.0.0.tar.gz root@target-host:/opt/

# 或使用U盘/移动硬盘物理传输
```

### 3. 在目标环境解压

```bash
# 解压安装包
cd /opt
tar -xzf aiops-agent-offline-1.0.0.tar.gz

# 进入目录
cd aiops-agent
```

### 4. 离线安装Python（如需要）

```bash
# 如果目标环境没有合适的Python版本
cd offline-packages
tar -xzf Python3.11_redhat7.tar.gz -C /opt/

# 设置环境变量
export PATH=/opt/Python3.11/bin:$PATH
export PYTHONPATH=/opt/aiops-agent

# 验证
python3.11 --version
```

### 5. 离线安装依赖

```bash
# 从本地包安装
cd /opt/aiops-agent
pip install --no-index --find-links=offline-packages/ -r requirements.txt

# 或者使用Python3.11自带的pip
/opt/Python3.11/bin/pip3.11 install --no-index \
    --find-links=offline-packages/ -r requirements.txt
```

### 6. 配置和启动

```bash
# 生成密钥和证书
/opt/Python3.11/bin/python3.11 scripts/generate_keys.py

# 启动服务
cd /opt/aiops-agent
export PYTHONPATH=/opt/aiops-agent
nohup /opt/Python3.11/bin/python3.11 src/server.py > logs/server.log 2>&1 &

# 验证
curl -k https://localhost:8443/health
```

---

## 配置说明

### 配置文件位置
主配置文件：`config/default.yaml`

### 配置项说明

```yaml
# 服务器配置
server:
  host: 0.0.0.0           # 监听地址，0.0.0.0表示所有网卡
  port: 8443              # 监听端口
  debug: false            # 调试模式，生产环境设为false

# 安全配置
security:
  tls_enabled: true       # 是否启用TLS/SSL
  cert_file: config/server.crt   # SSL证书路径
  key_file: config/server.key    # SSL私钥路径
  jwt_secret: <自动生成>  # JWT签名密钥
  jwt_expire_hours: 24    # JWT令牌过期时间（小时）
  aes_key: <自动生成>     # AES加密密钥

# 执行配置
execution:
  timeout: 300            # 命令执行超时（秒）
  max_output_size: 1048576  # 最大输出大小（字节）
  temp_dir: /tmp/aiops    # 临时文件目录

# 日志配置
logging:
  level: INFO             # 日志级别：DEBUG, INFO, WARNING, ERROR
  file: logs/aiops-agent.log  # 日志文件路径
  max_size: 10485760      # 日志文件最大大小（字节）
  backup_count: 5         # 日志文件备份数量

# 用户切换配置
user_switch:
  linux:
    sudo_enabled: true    # 是否启用sudo
    su_enabled: true      # 是否启用su
  windows:
    runas_enabled: true   # 是否启用runas
```

### 环境变量覆盖

可以通过环境变量覆盖配置文件中的设置：

```bash
export AIOPS_HOST=192.168.1.100
export AIOPS_PORT=9443
export AIOPS_JWT_SECRET=your-secret-key
export AIOPS_AES_KEY=your-aes-key
export AIOPS_LOG_LEVEL=DEBUG
```

---

## 启动与停止

### Linux环境

#### 方式1：直接启动

```bash
# 启动
cd /opt/aiops-agent
export PYTHONPATH=/opt/aiops-agent
nohup python3 src/server.py > logs/server.log 2>&1 &
echo $! > /var/run/aiops-agent.pid

# 停止
kill $(cat /var/run/aiops-agent.pid)

# 重启
kill $(cat /var/run/aiops-agent.pid)
sleep 2
nohup python3 src/server.py > logs/server.log 2>&1 &
echo $! > /var/run/aiops-agent.pid
```

#### 方式2：使用systemd服务

创建服务文件：`/etc/systemd/system/aiops-agent.service`

```ini
[Unit]
Description=AIOps Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aiops-agent
Environment="PYTHONPATH=/opt/aiops-agent"
ExecStart=/usr/bin/python3 /opt/aiops-agent/src/server.py
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

管理服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start aiops-agent

# 停止服务
sudo systemctl stop aiops-agent

# 重启服务
sudo systemctl restart aiops-agent

# 查看状态
sudo systemctl status aiops-agent

# 设置开机自启
sudo systemctl enable aiops-agent

# 查看日志
sudo journalctl -u aiops-agent -f
```

### Windows环境

#### 方式1：直接启动

```cmd
# 启动（前台）
cd C:\aiops-agent
set PYTHONPATH=C:\aiops-agent
python src\server.py

# 启动（后台）
pythonw src\server.py
```

#### 方式2：使用Windows服务

使用NSSM (Non-Sucking Service Manager)：

```cmd
# 下载NSSM：https://nssm.cc/download

# 安装服务
nssm install AIOpsAgent "C:\Python310\python.exe" "C:\aiops-agent\src\server.py"
nssm set AIOpsAgent AppDirectory "C:\aiops-agent"
nssm set AIOpsAgent AppEnvironmentExtra "PYTHONPATH=C:\aiops-agent"

# 启动服务
nssm start AIOpsAgent

# 停止服务
nssm stop AIOpsAgent

# 查看状态
nssm status AIOpsAgent
```

---

## 故障排除

### 1. 端口被占用

**症状**：启动时报错 `Address already in use`

**解决方案**：

```bash
# Linux - 查找占用端口的进程
sudo netstat -tlnp | grep 8443
# 或
sudo lsof -i :8443

# 杀死进程
sudo kill -9 <PID>

# Windows - 查找占用端口的进程
netstat -ano | findstr :8443

# 杀死进程
taskkill /PID <PID> /F
```

### 2. SSL证书错误

**症状**：客户端连接时报SSL错误

**解决方案**：

```bash
# 重新生成证书
cd /opt/aiops-agent
python scripts/generate_keys.py

# 验证证书
openssl x509 -in config/server.crt -text -noout

# 如果使用自签名证书，客户端需要使用 -k 或 --insecure 选项
curl -k https://localhost:8443/health
```

### 3. 权限问题

**症状**：无法创建临时文件或日志文件

**解决方案**：

```bash
# 创建必要的目录并设置权限
mkdir -p /opt/aiops-agent/logs
mkdir -p /tmp/aiops
chmod 755 /opt/aiops-agent/logs
chmod 777 /tmp/aiops

# 或以root用户运行
sudo python3 src/server.py
```

### 4. 模块导入错误

**症状**：`ModuleNotFoundError: No module named 'src'`

**解决方案**：

```bash
# 设置PYTHONPATH环境变量
export PYTHONPATH=/opt/aiops-agent

# 或在启动脚本中添加
cd /opt/aiops-agent
export PYTHONPATH=$(pwd)
python3 src/server.py
```

### 5. 依赖包缺失

**症状**：导入模块时报错

**解决方案**：

```bash
# 检查已安装的包
pip list

# 重新安装依赖
pip install -r requirements.txt

# 检查特定包
pip show flask
```

### 6. 日志查看

```bash
# 实时查看日志
tail -f logs/aiops-agent.log

# 查看最近的错误
grep ERROR logs/aiops-agent.log | tail -20

# 查看服务状态日志（systemd）
sudo journalctl -u aiops-agent -n 50
```

### 7. 网络连接问题

**症状**：无法访问服务

**解决方案**：

```bash
# 检查服务是否运行
ps aux | grep server.py
netstat -tlnp | grep 8443

# 检查防火墙
# CentOS/RHEL
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=8443/tcp --permanent
sudo firewall-cmd --reload

# Ubuntu
sudo ufw status
sudo ufw allow 8443/tcp

# 测试本地连接
curl -k https://localhost:8443/health

# 测试远程连接
curl -k https://<server-ip>:8443/health
```

### 8. Python版本问题

**症状**：语法错误或模块不兼容

**解决方案**：

```bash
# 检查Python版本
python3 --version

# 确保使用Python 3.8+
# 如果版本过低，需要安装新版本Python
# 或使用提供的Python3.11环境
```

---

## 安全建议

### 1. 生产环境配置

- ✅ 使用正式的SSL证书（如Let's Encrypt）
- ✅ 定期轮换JWT密钥和AES密钥
- ✅ 限制服务器监听地址（不使用0.0.0.0）
- ✅ 配置防火墙规则
- ✅ 使用非root用户运行服务
- ✅ 定期更新依赖包
- ✅ 启用日志审计

### 2. 密钥管理

```bash
# 备份密钥
cp config/default.yaml config/default.yaml.backup

# 限制配置文件权限
chmod 600 config/default.yaml

# 不要将密钥提交到版本控制系统
echo "config/default.yaml" >> .gitignore
```

### 3. 访问控制

- 使用强密码和复杂的API密钥
- 配置JWT令牌过期时间
- 实施IP白名单（如需要）
- 定期审查用户权限

---

## RPM包部署（CentOS/RHEL）

### 构建RPM包

```bash
# 安装构建工具
sudo yum install -y rpm-build

# 构建RPM包
python setup.py bdist_rpm

# 生成的包位于
ls -l dist/*.rpm
```

### 安装RPM包

```bash
# 安装
sudo rpm -ivh dist/aiops-agent-1.0.0-1.noarch.rpm

# 卸载
sudo rpm -e aiops-agent

# 查询
rpm -qi aiops-agent
```

---

## Docker部署（可选）

### 构建Docker镜像

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /opt/aiops-agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python scripts/generate_keys.py

EXPOSE 8443

CMD ["python", "src/server.py"]
```

### 运行容器

```bash
# 构建镜像
docker build -t aiops-agent:1.0.0 .

# 运行容器
docker run -d \
  --name aiops-agent \
  -p 8443:8443 \
  -v /opt/aiops-agent/logs:/opt/aiops-agent/logs \
  aiops-agent:1.0.0

# 查看日志
docker logs -f aiops-agent
```

---

## 升级指南

### 在线升级

```bash
# 备份当前版本
cp -r /opt/aiops-agent /opt/aiops-agent.backup

# 停止服务
sudo systemctl stop aiops-agent

# 更新代码
cd /opt/aiops-agent
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 备份配置
cp config/default.yaml /tmp/default.yaml.backup

# 重新生成配置（如有新配置项）
# 手动合并旧配置到新配置

# 启动服务
sudo systemctl start aiops-agent

# 验证
curl -k https://localhost:8443/health
```

### 离线升级

与离线部署流程类似，准备新版本的离线包，传输并安装。

---

## 联系支持

如有问题，请查看：
- 项目文档
- GitHub Issues
- 技术支持邮箱

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-09
