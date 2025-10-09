# AIOps Agent 部署指南

## 测试环境信息
- **IP地址**: 10.0.0.201
- **用户名**: root
- **密码**: 123456

## 部署步骤

### 1. 复制项目到测试环境
```bash
# 从本地复制到测试环境
scp -r /home/app/project/AIOps/agent root@10.0.0.201:/opt/

# 或者使用rsync
rsync -avz /home/app/project/AIOps/agent/ root@10.0.0.201:/opt/aiops-agent/
```

### 2. 在测试环境安装依赖
```bash
# 连接到测试环境
ssh root@10.0.0.201

# 进入项目目录
cd /opt/aiops-agent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行部署测试
```bash
# 在测试环境运行部署测试
chmod +x deploy_test.sh
./deploy_test.sh
```

### 4. 启动服务器
```bash
# 在测试环境启动服务器
source venv/bin/activate
python src/server.py
```

### 5. 运行API测试
```bash
# 在另一个终端运行API测试
source venv/bin/activate
python scripts/test_api.py
```

## 验证步骤

### 1. 检查服务器状态
```bash
# 检查服务器是否正常运行
curl -k https://localhost:8443/health
```

### 2. 测试API接口
```bash
# 获取认证令牌
curl -k -X POST https://localhost:8443/auth/token \
  -H "Content-Type: application/json" \
  -d '{"api_key": "test-key", "token": "test-token"}'

# 执行命令
curl -k -X POST https://localhost:8443/exec/command \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la", "user": "root"}'
```

## 故障排除

### 1. 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep 8443

# 杀死占用进程
kill -9 <PID>
```

### 2. 权限问题
```bash
# 确保有执行权限
chmod +x scripts/*.py
chmod +x deploy_test.sh
```

### 3. 依赖问题
```bash
# 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 打包部署

### RPM包（RedHat/CentOS）
```bash
# 构建RPM包
python setup.py bdist_rpm

# 安装RPM包
rpm -ivh dist/aiops-agent-1.0.0-1.noarch.rpm
```

### Windows EXE
```bash
# 构建Windows可执行文件
pyinstaller pyinstaller.spec

# 在Windows上运行
dist/aiops-agent.exe
```