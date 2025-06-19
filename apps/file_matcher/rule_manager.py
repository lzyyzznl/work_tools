import json
import os
import sys
from typing import List, Dict, Any
from pathlib import Path


class RuleManager:
    """文件匹配规则管理器"""
    
    def __init__(self, default_rules_path: str = None, user_rules_path: str = None):
        # 设置默认规则文件路径
        if default_rules_path is None:
            try:
                base_path = sys._MEIPASS
            except AttributeError:
                # 从rule_manager.py -> apps/file_matcher -> apps -> 项目根目录
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            self.default_rules_path = os.path.join(base_path, "apps", "file_matcher", "resources", "default_rules.json")
        else:
            self.default_rules_path = default_rules_path
        
        # 设置用户规则文件路径
        if user_rules_path is None:
            user_home = Path.home()
            user_config_dir = user_home / ".file_matcher"
            user_config_dir.mkdir(exist_ok=True)
            self.user_rules_path = user_config_dir / "user_rules.json"
        else:
            self.user_rules_path = Path(user_rules_path)
            
        self.rules = []  # 存储规则列表
        self.load_rules()
    
    def load_default_rules(self) -> List[Dict]:
        """加载默认规则"""
        try:
            print(f"尝试加载默认规则文件: {self.default_rules_path}")
            if os.path.exists(self.default_rules_path):
                with open(self.default_rules_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('rules', [])
            else:
                print("默认规则文件不存在")
                return []
        except Exception as e:
            print(f"加载默认规则失败: {e}")
            return []
    
    def load_user_rules(self) -> List[Dict]:
        """加载用户规则"""
        try:
            print(f"尝试加载用户规则文件: {self.user_rules_path}")
            if self.user_rules_path.exists():
                with open(self.user_rules_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('rules', [])
            else:
                print("用户规则文件不存在")
                return []
        except Exception as e:
            print(f"加载用户规则失败: {e}")
            return []
    
    def load_rules(self):
        """加载并合并规则"""
        try:
            # 1. 加载默认规则
            default_rules = self.load_default_rules()
            print(f"加载了 {len(default_rules)} 条默认规则")
            
            # 2. 加载用户规则
            user_rules = self.load_user_rules()
            print(f"加载了 {len(user_rules)} 条用户规则")
            
            # 3. 合并规则：用户规则按code覆盖默认规则
            merged_rules = {}
            
            # 先添加默认规则
            for rule in default_rules:
                code = rule.get('code', '')
                if code and self._is_valid_rule(rule):
                    # 为每个code创建唯一键，如果有重复code，使用索引区分
                    key = self._generate_rule_key(rule, merged_rules)
                    merged_rules[key] = rule
            
            # 再添加用户规则，按code覆盖
            for rule in user_rules:
                code = rule.get('code', '')
                if code and self._is_valid_rule(rule):
                    # 查找是否有相同code的默认规则需要覆盖
                    for key in list(merged_rules.keys()):
                        if merged_rules[key].get('code') == code:
                            print(f"用户规则覆盖默认规则: {code}")
                            del merged_rules[key]
                            break
                    
                    # 添加用户规则
                    key = self._generate_rule_key(rule, merged_rules)
                    merged_rules[key] = rule
            
            # 转换为列表
            self.rules = list(merged_rules.values())
            print(f"最终合并了 {len(self.rules)} 条规则")
            
        except Exception as e:
            print(f"加载规则失败: {e}")
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
    
    def save_user_rules(self):
        """保存用户规则到文件"""
        try:
            # 确保目录存在
            self.user_rules_path.parent.mkdir(exist_ok=True)
            
            # 只保存用户添加或修改的规则
            user_rules_data = {
                "rules": self.get_user_modified_rules()
            }
            
            with open(self.user_rules_path, 'w', encoding='utf-8') as f:
                json.dump(user_rules_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存用户规则失败: {e}")
            return False
    
    def get_user_modified_rules(self) -> List[Dict]:
        """获取用户修改过的规则"""        # 这里简化处理，所有当前规则都视为用户规则
        # 在实际应用中，可以通过标记来区分用户规则和默认规则
        return self.rules
    
    def get_all_rules(self) -> List[Dict]:
        """获取所有规则"""
        return self.rules.copy()
    
    def add_rule(self, code: str, thirty_d: str, match_rules: List[str]) -> bool:
        """添加新规则"""
        try:
            new_rule = {
                'code': code.strip(),
                '30d': thirty_d.strip(),
                'match_rules': [rule.strip() for rule in match_rules if rule.strip()]
            }
            
            if not self._is_valid_rule(new_rule):
                print("规则无效")
                return False
            
            self.rules.append(new_rule)
            return self.save_user_rules()
        except Exception as e:
            print(f"添加规则失败: {e}")
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
                    print("规则无效")
                    return False
                
                self.rules[index] = updated_rule
                return self.save_user_rules()
            return False
        except Exception as e:
            print(f"更新规则失败: {e}")
            return False
    
    def delete_rule(self, index: int) -> bool:
        """删除指定索引的规则"""
        try:
            if 0 <= index < len(self.rules):
                del self.rules[index]
                return self.save_user_rules()
            return False
        except Exception as e:
            print(f"删除规则失败: {e}")
            return False
    
    def match_filename(self, filename: str) -> tuple:
        """
        匹配文件名，返回 (是否匹配, 匹配的规则信息)
        """
        for index, rule in enumerate(self.rules):
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
        """重置用户规则（删除用户规则文件，重新加载默认规则）"""
        try:
            # 删除用户规则文件
            if self.user_rules_path.exists():
                self.user_rules_path.unlink()
            
            # 重新加载规则
            self.load_rules()
            return True
            
        except Exception as e:
            print(f"重置规则失败: {e}")
            return False
    
    # 保持兼容性的方法，适配原有的UI代码
    def get_match_rule_columns(self) -> List[str]:
        """获取匹配规则列名（兼容性方法）"""
        # 由于新的JSON结构不再使用match_rule1, match_rule2格式
        # 这里返回一个固定的列表以保持兼容性
        return ['match_rules']
    
    def get_next_match_rule_column(self) -> str:
        """获取下一个可用的匹配规则列名（兼容性方法）"""
        return 'match_rules'