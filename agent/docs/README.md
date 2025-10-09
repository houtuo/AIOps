# AIOps 自动化运维代理程序

一个跨平台的自动化运维代理程序，支持命令执行、脚本执行、用户身份切换和加密通信。

## 功能特性

- ✅ **跨平台支持**: Windows/Linux
- ✅ **命令执行**: 系统命令执行和结果捕获
- ✅ **脚本执行**: 支持Shell、PowerShell、Python等脚本
- ✅ **用户身份切换**: 支持切换用户执行任务
- ✅ **加密通信**: TLS加密通信，支持双向认证
- ✅ **RESTful API**: 标准HTTP接口
- ✅ **离线部署**: 支持无外网环境部署

## 快速开始

### 环境要求

- Python 3.11+
- Linux (CentOS/Ubuntu) 或 Windows

### 安装

1. 克隆项目
```bash
git clone https://github.com/houtuo/AIOps.git
cd AIOps/agent
```

2. 使用conda虚拟环境
```bash
conda activate /home/app/project/AIOps/agent/venv
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 生成密钥
```bash
python scripts/generate_keys.py
```

5. 启动服务
```bash
python src/main.py
```

### 配置

编辑 `config/default.yaml` 文件进行配置：

```yaml
server:
  host: "0.0.0.0"
  port: 8443

security:
  tls_enabled: true
  cert_file: "config/server.crt"
  key_file: "config/server.key"
```

## API 接口

### 健康检查
```http
GET /health
```

### 状态查询
```http
GET /status
```

### 命令执行
```http
POST /exec/command
Content-Type: application/json

{
  "command": "ls -l",
  "user": "alice"
}
```

### 脚本执行
```http
POST /exec/script/content
Content-Type: application/json

{
  "script": "#!/bin/bash\necho hello",
  "user": "bob"
}
```

## 部署

### Linux RPM包
```bash
# 构建RPM包
python setup.py bdist_rpm

# 安装
rpm -ivh dist/aiops-agent-1.0.0-1.noarch.rpm
```

### Windows EXE
```bash
# 构建EXE
pyinstaller --onefile src/main.py
```

## 开发

### 项目结构
```
agent/
├── src/                    # 源代码
│   ├── main.py            # 主程序
│   ├── config.py          # 配置管理
│   ├── server.py          # 服务器模块
│   ├── executor.py        # 执行器模块
│   └── security.py        # 安全模块
├── tests/                 # 测试代码
├── config/                # 配置文件
├── scripts/               # 工具脚本
├── docs/                  # 文档
└── requirements.txt       # 依赖管理
```

### 测试
```bash
pytest tests/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！