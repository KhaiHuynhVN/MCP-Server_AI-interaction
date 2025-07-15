# Configuration management for AI Interaction Tool
import json
import os
import sys
from ..constants import CONFIG_FILENAME, DEFAULT_LANGUAGE

class ConfigManager:
    """
    Quản lý cấu hình cho AI Interaction Tool
    """
    
    def __init__(self):
        """
        Khởi tạo ConfigManager với đường dẫn file cấu hình
        """
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            CONFIG_FILENAME
        )
        self.config = self._load_default_config()
        self.load_config()
        
        # Ensure config file exists - create it if this is first run
        if not os.path.exists(self.config_path):
            print(f"[ConfigManager] First run detected, creating config file at {self.config_path}", file=sys.stderr)
            self.save_config()
    
    def _load_default_config(self):
        """
        Trả về cấu hình mặc định
        
        Returns:
            dict: Dictionary chứa cấu hình mặc định
        """
        return {
            'language': DEFAULT_LANGUAGE,
            'window_size': {
                'width': 900,
                'height': 750
            },
            'ui_preferences': {
                'continue_chat_default': True,
                'remember_last_path': True,
                'auto_expand_folders': True,
                'auto_keepalive_default': False
            }
        }
    
    def load_config(self):
        """
        Tải cấu hình từ file config.json nếu tồn tại
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge với config mặc định để đảm bảo có đủ các key
                    # Use recursive merge để preserve nested structure
                    self._deep_merge(self.config, loaded_config)
                    print(f"[ConfigManager] Đã tải cấu hình từ {self.config_path}", file=sys.stderr)
            else:
                print(f"[ConfigManager] File cấu hình không tồn tại, sử dụng cấu hình mặc định", file=sys.stderr)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"[ConfigManager] Lỗi khi tải cấu hình: {str(e)}", file=sys.stderr)
            print(f"[ConfigManager] Sử dụng cấu hình mặc định", file=sys.stderr)
            # Reset to default config on any error
            self.config = self._load_default_config()
        except Exception as e:
            print(f"[ConfigManager] Lỗi không mong đợi khi tải cấu hình: {str(e)}", file=sys.stderr)
            # Sử dụng cấu hình mặc định nếu có lỗi
            self.config = self._load_default_config()
    
    def _deep_merge(self, base_dict, update_dict):
        """
        Merge two dictionaries recursively, with update_dict taking precedence
        
        Args:
            base_dict (dict): Base dictionary to merge into
            update_dict (dict): Dictionary with updates
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self):
        """
        Lưu cấu hình vào file config.json
        
        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            # Validate config before saving
            if not isinstance(self.config, dict):
                print(f"[ConfigManager] Cấu hình không hợp lệ (không phải dict)", file=sys.stderr)
                return False
            
            # Tạo thư mục nếu chưa tồn tại
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = self.config_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            # Atomic rename to prevent corruption
            if os.path.exists(self.config_path):
                # Backup existing config before replace
                backup_path = self.config_path + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(self.config_path, backup_path)
            
            os.rename(temp_path, self.config_path)
            
            print(f"[ConfigManager] Đã lưu cấu hình vào {self.config_path}", file=sys.stderr)
            return True
            
        except (PermissionError, OSError) as e:
            print(f"[ConfigManager] Lỗi quyền truy cập khi lưu cấu hình: {str(e)}", file=sys.stderr)
            # Clean up temp file if exists
            temp_path = self.config_path + '.tmp'
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False
        except Exception as e:
            print(f"[ConfigManager] Lỗi không mong đợi khi lưu cấu hình: {str(e)}", file=sys.stderr)
            # Clean up temp file if exists
            temp_path = self.config_path + '.tmp'
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False
    
    def get(self, key, default=None):
        """
        Lấy giá trị cấu hình theo key
        
        Args:
            key (str): Key cấu hình (có thể dùng dot notation như 'ui_preferences.continue_chat_default')
            default: Giá trị mặc định nếu key không tồn tại
            
        Returns:
            Giá trị cấu hình hoặc default
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key, value):
        """
        Đặt giá trị cấu hình
        
        Args:
            key (str): Key cấu hình (có thể dùng dot notation)
            value: Giá trị cần đặt
        """
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set the value
            config_ref[keys[-1]] = value
        except Exception as e:
            print(f"[ConfigManager] Lỗi khi đặt cấu hình {key}: {str(e)}", file=sys.stderr)
    
    def get_language(self):
        """
        Lấy ngôn ngữ hiện tại
        
        Returns:
            str: Mã ngôn ngữ
        """
        return self.get('language', DEFAULT_LANGUAGE)
    
    def set_language(self, language):
        """
        Đặt ngôn ngữ và lưu cấu hình
        
        Args:
            language (str): Mã ngôn ngữ
        """
        self.set('language', language)
        self.save_config()
    
    def get_window_size(self):
        """
        Lấy kích thước cửa sổ
        
        Returns:
            tuple: (width, height)
        """
        size = self.get('window_size', {'width': 900, 'height': 750})
        return size.get('width', 900), size.get('height', 750)
    
    def set_window_size(self, width, height):
        """
        Đặt kích thước cửa sổ
        
        Args:
            width (int): Chiều rộng
            height (int): Chiều cao
        """
        self.set('window_size', {'width': width, 'height': height})
        self.save_config()
    
    def get_last_workspace(self):
        """
        Lấy workspace được sử dụng lần cuối
        
        Returns:
            str: Đường dẫn workspace hoặc None
        """
        return self.get('last_workspace.path')
    
    def set_last_workspace(self, workspace_path):
        """
        Lưu workspace được sử dụng lần cuối
        
        Args:
            workspace_path (str): Đường dẫn workspace hoặc None để clear
        """
        if workspace_path:
            workspace_name = os.path.basename(workspace_path)
            self.set('last_workspace', {
                'path': workspace_path,
                'name': workspace_name
            })
        else:
            # Clear workspace
            self.set('last_workspace', None)
        self.save_config()
    
    def get_last_workspace_name(self):
        """
        Lấy tên workspace được sử dụng lần cuối
        
        Returns:
            str: Tên workspace hoặc None
        """
        return self.get('last_workspace.name')
    
    def get_last_attached_files(self):
        """
        Lấy danh sách files đã attach lần cuối
        
        Returns:
            list: Danh sách attached files hoặc []
        """
        return self.get('last_workspace.attached_files', [])
    
    def set_last_attached_files(self, attached_files):
        """
        Lưu danh sách files đã attach
        
        Args:
            attached_files (list): Danh sách attached files
        """
        if attached_files is None:
            attached_files = []
        self.set('last_workspace.attached_files', attached_files)
        self.save_config() 