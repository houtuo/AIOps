"""
服务器模块

负责启动和管理代理程序的HTTP服务器。
"""

import logging
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from src.executor import CommandExecutor
from src.script_executor import ScriptExecutor
from src.security import SecurityManager
from src.user_switch import UserSwitch


class AgentServer:
    """代理服务器类"""

    def __init__(self, config):
        self.config = config
        self.app = None
        self.logger = logging.getLogger(__name__)

        # 初始化各个模块
        self.executor = CommandExecutor(config)
        self.script_executor = ScriptExecutor(config)
        self.security_manager = SecurityManager(config)
        self.user_switch = UserSwitch(config)

    def create_app(self):
        """创建Flask应用"""
        app = Flask(__name__)

        # 配置应用
        server_config = self.config.get('server', {})
        app.config['DEBUG'] = server_config.get('debug', False)
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB文件上传限制

        # 注册蓝图和路由
        self._register_routes(app)

        # 注册错误处理器
        self._register_error_handlers(app)

        # 注册请求处理器
        self._register_request_handlers(app)

        return app

    def _register_routes(self, app):
        """注册路由"""
        # 健康检查
        @app.route('/health', methods=['GET'])
        def health_check():
            return {'status': 'healthy', 'service': 'aiops-agent'}

        # 状态查询
        @app.route('/status', methods=['GET'])
        def get_status():
            import platform
            return {
                'status': 'running',
                'version': '1.0.0',
                'platform': platform.system().lower(),
                'hostname': platform.node()
            }

        # 命令执行
        @app.route('/exec/command', methods=['POST'])
        def exec_command():
            return self._handle_command_execution()

        # 脚本内容执行
        @app.route('/exec/script/content', methods=['POST'])
        def exec_script_content():
            return self._handle_script_content_execution()

        # 脚本文件执行
        @app.route('/exec/script/file', methods=['POST'])
        def exec_script_file():
            return self._handle_script_file_execution()

        # 动态脚本封装执行
        @app.route('/exec/script/dynamic', methods=['POST'])
        def exec_script_dynamic():
            return self._handle_dynamic_script_execution()

        # 用户信息查询
        @app.route('/users', methods=['GET'])
        def get_users():
            return self._handle_get_users()

        # 用户信息查询
        @app.route('/users/<username>', methods=['GET'])
        def get_user_info(username):
            return self._handle_get_user_info(username)

        # 生成API密钥
        @app.route('/auth/api-key', methods=['POST'])
        def generate_api_key():
            return self._handle_generate_api_key()

        # 验证API密钥
        @app.route('/auth/verify', methods=['POST'])
        def verify_api_key():
            return self._handle_verify_api_key()

    def _register_error_handlers(self, app):
        """注册错误处理器"""

        @app.errorhandler(404)
        def not_found(error):
            return {'error': '接口不存在'}, 404

        @app.errorhandler(500)
        def internal_error(error):
            return {'error': '服务器内部错误'}, 500

        @app.errorhandler(413)
        def request_entity_too_large(error):
            return {'error': '请求体过大'}, 413

    def _register_request_handlers(self, app):
        """注册请求处理器"""

        @app.before_request
        def before_request():
            # 这里可以添加认证和授权逻辑
            # 例如检查API密钥、JWT令牌等
            pass

    def _handle_command_execution(self):
        """处理命令执行请求"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '请求体必须是JSON格式'}, 400

            command = data.get('command')
            user = data.get('user')
            working_dir = data.get('working_dir')
            env = data.get('env')

            if not command:
                return {'error': '缺少命令参数'}, 400

            # 验证命令安全性
            if not self.executor.validate_command(command):
                return {'error': '命令安全检查失败'}, 400

            # 执行命令
            result = self.executor.execute(command, user, working_dir, env)

            return jsonify(result)

        except Exception as e:
            self.logger.error(f"命令执行处理失败: {e}")
            return {'error': str(e)}, 500

    def _handle_script_content_execution(self):
        """处理脚本内容执行请求"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '请求体必须是JSON格式'}, 400

            script = data.get('script')
            user = data.get('user')
            working_dir = data.get('working_dir')
            env = data.get('env')

            if not script:
                return {'error': '缺少脚本参数'}, 400

            # 执行脚本内容
            result = self.script_executor.execute_script_content(script, user, working_dir, env)

            return jsonify(result)

        except Exception as e:
            self.logger.error(f"脚本内容执行处理失败: {e}")
            return {'error': str(e)}, 500

    def _handle_script_file_execution(self):
        """处理脚本文件执行请求"""
        try:
            # 检查文件上传
            if 'file' not in request.files:
                return {'error': '缺少文件参数'}, 400

            file = request.files['file']
            if file.filename == '':
                return {'error': '未选择文件'}, 400

            # 获取其他参数
            user = request.form.get('user')
            working_dir = request.form.get('working_dir')

            # 保存上传的文件
            filename = secure_filename(file.filename)
            temp_dir = self.config.get('execution', {}).get('temp_dir', '/tmp/aiops')
            os.makedirs(temp_dir, exist_ok=True)

            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)

            # 执行脚本文件
            result = self.script_executor.execute_script_file(file_path, user, working_dir)

            # 清理临时文件
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.warning(f"清理临时文件失败: {e}")

            return jsonify(result)

        except Exception as e:
            self.logger.error(f"脚本文件执行处理失败: {e}")
            return {'error': str(e)}, 500

    def _handle_dynamic_script_execution(self):
        """处理动态脚本封装执行请求"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '请求体必须是JSON格式'}, 400

            script = data.get('script')
            user = data.get('user')
            working_dir = data.get('working_dir')
            env = data.get('env')

            if not script:
                return {'error': '缺少脚本参数'}, 400

            # 执行动态脚本封装
            result = self.script_executor.execute_dynamic_wrapper(script, user, working_dir, env)

            return jsonify(result)

        except Exception as e:
            self.logger.error(f"动态脚本执行处理失败: {e}")
            return {'error': str(e)}, 500

    def _handle_get_users(self):
        """处理获取用户列表请求"""
        try:
            users = self.user_switch.get_available_users()
            return {'users': users}

        except Exception as e:
            self.logger.error(f"获取用户列表失败: {e}")
            return {'error': str(e)}, 500

    def _handle_get_user_info(self, username):
        """处理获取用户信息请求"""
        try:
            user_info = self.user_switch.get_user_info(username)
            if not user_info:
                return {'error': f'用户不存在: {username}'}, 404

            return user_info

        except Exception as e:
            self.logger.error(f"获取用户信息失败: {e}")
            return {'error': str(e)}, 500

    def _handle_generate_api_key(self):
        """处理生成API密钥请求"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '请求体必须是JSON格式'}, 400

            user_id = data.get('user_id')
            permissions = data.get('permissions', [])

            if not user_id:
                return {'error': '缺少用户ID参数'}, 400

            # 生成API密钥
            api_key_info = self.security_manager.generate_api_key(user_id, permissions)

            return jsonify(api_key_info)

        except Exception as e:
            self.logger.error(f"生成API密钥失败: {e}")
            return {'error': str(e)}, 500

    def _handle_verify_api_key(self):
        """处理验证API密钥请求"""
        try:
            data = request.get_json()
            if not data:
                return {'error': '请求体必须是JSON格式'}, 400

            api_key = data.get('api_key')
            token = data.get('token')

            if not api_key or not token:
                return {'error': '缺少API密钥或令牌参数'}, 400

            # 验证API密钥
            is_valid = self.security_manager.verify_api_key(api_key, token)

            return {'valid': is_valid}

        except Exception as e:
            self.logger.error(f"验证API密钥失败: {e}")
            return {'error': str(e)}, 500

    def start(self):
        """启动服务器"""
        self.app = self.create_app()

        server_config = self.config.get('server', {})
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 8443)

        # 安全配置
        security_config = self.config.get('security', {})
        ssl_context = None

        if security_config.get('tls_enabled', True):
            cert_file = security_config.get('cert_file')
            key_file = security_config.get('key_file')

            if cert_file and key_file:
                import os
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    ssl_context = (cert_file, key_file)
                else:
                    self.logger.warning("证书文件不存在，使用HTTP协议")

        self.logger.info(f"启动服务器: {host}:{port}")

        try:
            self.app.run(
                host=host,
                port=port,
                debug=server_config.get('debug', False),
                ssl_context=ssl_context,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"服务器启动失败: {e}")
            raise

    def stop(self):
        """停止服务器"""
        self.logger.info("正在停止服务器...")
        # 这里可以添加清理逻辑
        pass