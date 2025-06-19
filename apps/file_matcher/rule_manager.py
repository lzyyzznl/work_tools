import json
import os
import sys
from typing import List, Dict, Any
from pathlib import Path


class RuleManager:
    """文件匹配规则管理器 - 使用统一配置文件"""
    
    def __init__(self, config_path: str = None):
        # 设置配置文件路径
        if config_path is None:
            # 优先尝试打包后的资源路径
            if os.path.exists("resources/config.json"):
                self.config_path = "resources/config.json"
            else:
                # 开发环境路径
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                self.config_path = os.path.join(base_path, "apps", "file_matcher", "resources", "config.json")
        else:
            self.config_path = config_path
            
        self.config = {}  # 存储完整配置
        self.rules = []  # 存储合并后的规则列表
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 创建默认配置
                self.config = {
                    "version": "1.0",
                    "settings": {
                        "auto_save": True,
                        "default_export_format": "xlsx",
                        "window_geometry": {"x": 100, "y": 100, "width": 1200, "height": 800},
                        "table_column_widths": [60, 250, 200, 120, 80, 80, 180, 110],
                        "search_history": [],
                        "last_export_path": "",
                        "theme": "default"
                    },
                    "rules": {
                        "default": [],
                        "user": []
                    }
                }
                self.save_config()
            
            # 合并规则
            self.merge_rules()
            
        except Exception as e:
            # 静默处理加载失败，使用空配置
            self.config = {
                "version": "1.0",
                "settings": {},
                "rules": {"default": [], "user": []}
            }
            self.rules = []
    
    def merge_rules(self):
        """合并默认规则和用户规则"""
        try:
            default_rules = self.config.get('rules', {}).get('default', [])
            user_rules = self.config.get('rules', {}).get('user', [])
            
            # 合并规则：用户规则按code覆盖默认规则
            merged_rules = {}
            
            # 先添加默认规则
            for rule in default_rules:
                if self._is_valid_rule(rule):
                    key = self._generate_rule_key(rule, merged_rules)
                    merged_rules[key] = {**rule, 'source': 'default'}
            
            # 再添加用户规则，按code覆盖
            for rule in user_rules:
                if self._is_valid_rule(rule):
                    code = rule.get('code', '')
                    # 查找是否有相同code的默认规则需要覆盖
                    for key in list(merged_rules.keys()):
                        if merged_rules[key].get('code') == code:
                            del merged_rules[key]
                            break
                    
                    # 添加用户规则
                    key = self._generate_rule_key(rule, merged_rules)
                    merged_rules[key] = {**rule, 'source': 'user'}
            
            # 转换为列表
            self.rules = list(merged_rules.values())
            
        except Exception:
            self.rules = []
    
    def _is_valid_rule(self, rule: Dict) -> bool:
        """检查规则是否有效"""
        return (rule.get('code', '').strip() and 
                rule.get('match_rules') and 
                len(rule.get('match_rules', [])) > 0)
    
    def _generate_rule_key(self, rule: Dict, existing_rules: Dict) -> str:
        """生成规则的唯一键"""
        code = rule.get('code', '')
        counter = 0
        key = code
        while key in existing_rules:
            counter += 1
            key = f"{code}_{counter}"
        return key
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def get_all_rules(self) -> List[Dict]:
        """获取所有规则"""
        # 返回规则副本，去除source字段
        return [{k: v for k, v in rule.items() if k != 'source'} for rule in self.rules]
    
    def add_rule(self, code: str, thirty_d: str, match_rules: List[str]) -> bool:
        """添加新规则"""
        try:
            new_rule = {
                'code': code.strip(),
                '30d': thirty_d.strip(),
                'match_rules': [rule.strip() for rule in match_rules if rule.strip()]
            }
            
            if not self._is_valid_rule(new_rule):
                return False
            
            # 添加到用户规则
            if 'rules' not in self.config:
                self.config['rules'] = {'default': [], 'user': []}
            if 'user' not in self.config['rules']:
                self.config['rules']['user'] = []
            
            self.config['rules']['user'].append(new_rule)
            
            # 重新合并规则
            self.merge_rules()
            
            return self.save_config()
        except Exception:
            return False
    
    def update_rule(self, index: int, code: str, thirty_d: str, match_rules: List[str]) -> bool:
        """更新指定索引的规则"""
        try:
            if 0 <= index < len(self.rules):
                updated_rule = {
                    'code': code.strip(),
                    '30d': thirty_d.strip(),
                    'match_rules': [rule.strip() for rule in match_rules if rule.strip()]
                }
                
                if not self._is_valid_rule(updated_rule):
                    return False
                
                # 获取当前规则的来源
                current_rule = self.rules[index]
                rule_source = current_rule.get('source', 'user')
                rule_code = current_rule.get('code', '')
                
                if rule_source == 'default':
                    # 如果是默认规则，则将更新的规则添加到用户规则中
                    if 'rules' not in self.config:
                        self.config['rules'] = {'default': [], 'user': []}
                    if 'user' not in self.config['rules']:
                        self.config['rules']['user'] = []
                    
                    # 检查用户规则中是否已存在同code的规则
                    user_rules = self.config['rules']['user']
                    found = False
                    for i, rule in enumerate(user_rules):
                        if rule.get('code') == rule_code:
                            user_rules[i] = updated_rule
                            found = True
                            break
                    
                    if not found:
                        user_rules.append(updated_rule)
                else:
                    # 如果是用户规则，直接更新
                    user_rules = self.config['rules']['user']
                    for i, rule in enumerate(user_rules):
                        if rule.get('code') == rule_code:
                            user_rules[i] = updated_rule
                            break
                
                # 重新合并规则
                self.merge_rules()
                
                return self.save_config()
            return False
        except Exception:
            return False
    
    def delete_rule(self, index: int) -> bool:
        """删除指定索引的规则"""
        try:
            if 0 <= index < len(self.rules):
                current_rule = self.rules[index]
                rule_source = current_rule.get('source', 'user')
                rule_code = current_rule.get('code', '')
                
                if rule_source == 'default':
                    # 如果是默认规则，添加一个空的用户规则来覆盖它
                    if 'rules' not in self.config:
                        self.config['rules'] = {'default': [], 'user': []}
                    if 'user' not in self.config['rules']:
                        self.config['rules']['user'] = []
                    
                    # 添加一个标记为删除的规则
                    deleted_rule = {
                        'code': rule_code,
                        '30d': '',
                        'match_rules': [],
                        'deleted': True
                    }
                    self.config['rules']['user'].append(deleted_rule)
                else:
                    # 如果是用户规则，直接删除
                    user_rules = self.config['rules']['user']
                    self.config['rules']['user'] = [
                        rule for rule in user_rules 
                        if rule.get('code') != rule_code
                    ]
                
                # 重新合并规则
                self.merge_rules()
                
                return self.save_config()
            return False
        except Exception:
            return False
    
    def match_filename(self, filename: str) -> tuple:
        """
        匹配文件名，返回 (是否匹配, 匹配的规则信息)
        """
        for index, rule in enumerate(self.rules):
            # 跳过被删除的规则
            if rule.get('deleted', False):
                continue
                
            match_rules = rule.get('match_rules', [])
            
            for match_rule in match_rules:
                if match_rule and match_rule in filename:
                    return True, {
                        'index': index,
                        'code': rule.get('code', ''),
                        '30d': rule.get('30d', ''),
                        'matched_rule': match_rule
                    }
        
        return False, None
    
    def reset_to_default(self) -> bool:
        """重置用户规则（清空用户规则，只保留默认规则）"""
        try:
            if 'rules' in self.config:
                self.config['rules']['user'] = []
            
            # 重新合并规则
            self.merge_rules()
            
            return self.save_config()
            
        except Exception:
            return False
    
    def load_rules(self):
        """重新加载配置文件（兼容性方法）"""
        self.load_config()
    
    # 保持兼容性的方法
    def get_match_rule_columns(self) -> List[str]:
        """获取匹配规则列名（兼容性方法）"""
        return ['match_rules']
    
    def get_next_match_rule_column(self) -> str:
        """获取下一个可用的匹配规则列名（兼容性方法）"""
        return 'match_rules'
    
    # 新增配置管理方法
    def get_setting(self, key: str, default=None):
        """获取设置值"""
        return self.config.get('settings', {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """设置配置值"""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        self.config['settings'][key] = value
        return self.save_config()
    
    def get_all_settings(self) -> Dict:
        """获取所有设置"""
        return self.config.get('settings', {}).copy()