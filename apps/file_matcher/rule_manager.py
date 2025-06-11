import pandas as pd
import os
import sys
from typing import List, Dict, Any


class RuleManager:
    """文件匹配规则管理器"""
    
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            # 获取默认CSV路径
            try:
                base_path = sys._MEIPASS
            except AttributeError:
                # 从rule_manager.py -> src/file_matcher -> src -> apps/file_matcher -> apps -> 项目根目录
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            # 优先检查新结构路径 apps/file_matcher/resources/content.csv
            app_resources_path = os.path.join(base_path, "apps", "file_matcher", "resources", "content.csv")
            if os.path.exists(app_resources_path):
                self.csv_path = app_resources_path
            else:
                # 尝试旧结构兼容路径
                old_path = os.path.join(base_path, "apps", "file_matcher", "src", "resource", "content.csv")
                if os.path.exists(old_path):
                    self.csv_path = old_path
                else:
                    # 默认使用新结构路径（即使文件不存在，稍后会创建）
                    self.csv_path = app_resources_path
        else:
            self.csv_path = csv_path
            
        self.df_rules = None
        self.load_rules()
    
    def load_rules(self):
        """加载规则文件"""
        try:
            print(f"尝试加载规则文件: {self.csv_path}")  # 调试信息
            if os.path.exists(self.csv_path):
                self.df_rules = pd.read_csv(self.csv_path)
                print(f"成功加载规则文件，共{len(self.df_rules)}条规则")  # 调试信息
                
                # 确保至少有基本列
                required_columns = ['code', '30d', 'match_rule1']
                for col in required_columns:
                    if col not in self.df_rules.columns:
                        self.df_rules[col] = ""
                
                # 清理所有空值、nan值和空字符串
                self.df_rules = self.df_rules.fillna('')  # 将NaN填充为空字符串
                
                # 对于所有列，将空字符串、仅包含空白字符的值设为空字符串
                for col in self.df_rules.columns:
                    self.df_rules[col] = self.df_rules[col].apply(
                        lambda x: '' if pd.isna(x) or str(x).strip() == '' or str(x).strip().lower() == 'nan' else str(x).strip()
                    )
                
                # 检查是否为空的规则集，如果是则加载默认规则
                if self.df_rules.empty or len(self.df_rules) == 0:
                    print("规则文件为空，加载默认规则...")
                    self.reset_to_default()
            else:
                print(f"规则文件不存在，创建默认规则: {self.csv_path}")
                # 文件不存在，直接加载默认规则
                self.reset_to_default()
        except Exception as e:
            print(f"加载规则文件失败: {e}")
            print("尝试加载默认规则...")
            # 创建空的DataFrame作为备选
            self.df_rules = pd.DataFrame(columns=['code', '30d', 'match_rule1'])
            # 尝试加载默认规则
            self.reset_to_default()
    
    def save_rules(self):
        """保存规则到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            self.df_rules.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"保存规则文件失败: {e}")
            return False
    
    def get_all_rules(self) -> pd.DataFrame:
        """获取所有规则"""
        return self.df_rules.copy()
    
    def add_rule(self, code: str, thirty_d: str, match_rules: Dict[str, str]) -> bool:
        """添加新规则"""
        try:
            new_rule = {'code': code, '30d': thirty_d}
            
            # 添加所有匹配规则
            for rule_key, rule_value in match_rules.items():
                new_rule[rule_key] = rule_value
            
            # 确保列存在
            for col in new_rule.keys():
                if col not in self.df_rules.columns:
                    self.df_rules[col] = ""
            
            # 添加新行
            new_index = len(self.df_rules)
            for col, value in new_rule.items():
                self.df_rules.at[new_index, col] = value
            
            return self.save_rules()
        except Exception as e:
            print(f"添加规则失败: {e}")
            return False
    
    def update_rule(self, index: int, code: str, thirty_d: str, match_rules: Dict[str, str]) -> bool:
        """更新指定索引的规则"""
        try:
            if 0 <= index < len(self.df_rules):
                self.df_rules.at[index, 'code'] = code
                self.df_rules.at[index, '30d'] = thirty_d
                
                # 更新所有匹配规则
                for rule_key, rule_value in match_rules.items():
                    if rule_key not in self.df_rules.columns:
                        self.df_rules[rule_key] = ""
                    self.df_rules.at[index, rule_key] = rule_value
                
                return self.save_rules()
            return False
        except Exception as e:
            print(f"更新规则失败: {e}")
            return False
    
    def delete_rule(self, index: int) -> bool:
        """删除指定索引的规则"""
        try:
            if 0 <= index < len(self.df_rules):
                self.df_rules = self.df_rules.drop(index).reset_index(drop=True)
                return self.save_rules()
            return False
        except Exception as e:
            print(f"删除规则失败: {e}")
            return False
    
    def get_match_rule_columns(self) -> List[str]:
        """获取所有匹配规则列名"""
        columns = [col for col in self.df_rules.columns if col.startswith('match_rule')]
        # 按数字排序
        def sort_key(col):
            try:
                return int(col.replace('match_rule', ''))
            except:
                return 999
        return sorted(columns, key=sort_key)
    
    def get_next_match_rule_column(self) -> str:
        """获取下一个可用的匹配规则列名"""
        existing_columns = self.get_match_rule_columns()
        if not existing_columns:
            return 'match_rule1'
        
        # 找到最大的数字
        max_num = 0
        for col in existing_columns:
            try:
                num = int(col.replace('match_rule', ''))
                max_num = max(max_num, num)
            except:
                continue
        
        return f'match_rule{max_num + 1}'
    
    def match_filename(self, filename: str) -> tuple:
        """
        匹配文件名，返回 (是否匹配, 匹配的规则信息)
        """
        for index, rule in self.df_rules.iterrows():
            # 检查所有匹配规则列
            match_columns = self.get_match_rule_columns()
            
            for col in match_columns:
                if col in rule and pd.notna(rule[col]) and str(rule[col]).strip():
                    rule_value = str(rule[col]).strip()
                    if rule_value in filename:
                        return True, {
                            'index': index,
                            'code': rule['code'],
                            '30d': rule['30d'],
                            'matched_rule': rule_value,
                            'matched_column': col
                        }
        
        return False, None
    
    def reset_to_default(self) -> bool:
        """重置为默认的规则配置"""
        try:
            # 定义默认规则数据
            default_rules_data = [
                {"code": "01.33.06.01", "30d": "N", "match_rule1": "Confidential Disclosure Agreements", "match_rule2": "CDA"},
                {"code": "01.33.06.02", "30d": "N", "match_rule1": "one way letter"},
                {"code": "01.33.10.02", "30d": "N", "match_rule1": "Privacy notice", "match_rule2": "PN"},
                {"code": "02.02.03", "30d": "N", "match_rule1": "FDC"},
                {"code": "02.03.03", "30d": "Y", "match_rule1": "Local Destruction", "match_rule2": "493847"},
                {"code": "02.03.04", "30d": "Y", "match_rule1": " Extension Expiry Date Memo", "match_rule2": "药品有效期延长说明"},
                {"code": "02.03.06", "30d": "Y", "match_rule1": "Final Investigational Product Reconciliation Statement Form", "match_rule2": "000539 "},
                {"code": "02.03.08", "30d": "N", "match_rule1": "000541"},
                {"code": "02.03.08", "30d": "N", "match_rule1": "081612"},
                {"code": "02.03.14", "30d": "N", "match_rule1": "001512"},
                {"code": "02.03.15", "30d": "N", "match_rule1": "Temperature Log"},
                {"code": "02.03.18", "30d": "N", "match_rule1": "DV", "match_rule2": "DPW"},
                {"code": "02.05.02", "30d": "N", "match_rule1": "EC approval", "match_rule2": "伦理批件"},
                {"code": "02.05.02", "30d": "N", "match_rule1": "EC notification", "match_rule2": "伦理意见"},
                {"code": "02.05.03", "30d": "N", "match_rule1": "EC Member", "match_rule2": "伦理委员会成员"},
                {"code": "02.05.03", "30d": "", "match_rule1": "statement of compliance", "match_rule2": "伦理委员会声明"},
                {"code": "02.05.04", "30d": "N", "match_rule1": "EC submission letter", "match_rule2": "伦理签收", "match_rule3": "伦理接收", "match_rule4": "递交信-PI to EC"},
                {"code": "02.05.04", "30d": "N", "match_rule1": "EC applications form", "match_rule2": "伦理申请表"},
                {"code": "02.05.04", "30d": "N", "match_rule1": "annual report", "match_rule2": "年度报告"},
                {"code": "02.06.01", "30d": "N", "match_rule1": "Lab certificate", "match_rule2": "室间质评"},
                {"code": "02.06.03", "30d": "N", "match_rule1": "Local lab normal range", "match_rule2": "正常值范围"},
                {"code": "02.07.03", "30d": "Y", "match_rule1": "SEV  follow up letter"},
                {"code": "02.07.05", "30d": "Y", "match_rule1": "SIV/RMV/FMV/SEV confirmation letter"},
                {"code": "02.07.05", "30d": "Y", "match_rule1": "CRA transition letter"},
                {"code": "02.07.06", "30d": "N", "match_rule1": "Site Recruitment Plan", "match_rule2": "招募计划"},
                {"code": "02.07.08", "30d": "N", "match_rule1": "Training Record", "match_rule2": "培训记录"},
                {"code": "02.07.09", "30d": "N", "match_rule1": "MV follow up letter"},
                {"code": "02.07.10", "30d": "Y", "match_rule1": "000551", "match_rule2": "Sponsor Visit Log", "match_rule3": "访视登记表"},
                {"code": "02.07.12", "30d": "Y", "match_rule1": "492536", "match_rule2": "IIR", "match_rule3": "Investigator Initiation Report"},
                {"code": "02.07.12", "30d": "Y", "match_rule1": "493981", "match_rule2": "EDC Survey", "match_rule3": "Electronic Data Capture (EDC) Site Survey & Site IT Capability Verification Form", "match_rule4": "501678"},
                {"code": "02.07.13", "30d": "N", "match_rule1": "SIV follow up letter"},
                {"code": "02.07.22", "30d": "Y", "match_rule1": "Site Closure Memorandum"},
                {"code": "02.07.24", "30d": "Y", "match_rule1": "494231", "match_rule2": "Source Document Identity Form", "match_rule3": "SDIF"},
                {"code": "02.07.25", "30d": "Y", "match_rule1": "EMR Checklist"},
                {"code": "02.07.26", "30d": "Y", "match_rule1": "504077", "match_rule2": "Clinical Site Digital Signature Application Checklist"},
                {"code": "02.08.01", "30d": "Y", "match_rule1": "492316", "match_rule2": "NTF"},
                {"code": "02.08.02", "30d": "N", "match_rule1": "495099", "match_rule2": "Investigator File Note Form", "match_rule3": "Investigator NTF"},
                {"code": "02.11.01", "30d": "Y", "match_rule1": "IB 签收", "match_rule2": "IB接收", "match_rule3": "receive of IB"},
                {"code": "02.11.02", "30d": "N", "match_rule1": "CRF 签收", "match_rule2": "CRF接收", "match_rule3": "receive of CRF"},
                {"code": "02.11.03", "30d": "N", "match_rule1": "PI submission letter of", "match_rule2": "PI 签收条", "match_rule3": "PI接收"},
                {"code": "02.11.03", "30d": "N", "match_rule1": "CRC receive"},
                {"code": "02.11.05", "30d": "Y", "match_rule1": "Protocol Signature Page", "match_rule2": "方案签字页"},
                {"code": "02.12.01", "30d": "Y", "match_rule1": "site selection letter"},
                {"code": "02.13.01", "30d": "N", "match_rule1": "Main ICF"},
                {"code": "02.13.02", "30d": "Y", "match_rule1": "494429"},
                {"code": "02.15.03.03", "30d": "N", "match_rule1": "SSR"},
                {"code": "02.15.03.04", "30d": "Y", "match_rule1": "internal commination email"},
                {"code": "02.15.04.03", "30d": "N", "match_rule1": "Equipment Calibration", "match_rule2": "校准证书"},
                {"code": "02.16.02/ 03/ 04", "30d": "N", "match_rule1": "CV"},
                {"code": "02.16.05", "30d": "N", "match_rule1": "DoA", "match_rule2": "DOA", "match_rule3": "授权表"},
                {"code": "02.16.08", "30d": "N", "match_rule1": "GCP", "match_rule2": "资质"},
                {"code": "1.2", "30d": "Y", "match_rule1": "123"}
            ]
            
            # 创建新的DataFrame
            self.df_rules = pd.DataFrame(default_rules_data)
            
            # 保存到文件
            return self.save_rules()
            
        except Exception as e:
            print(f"重置规则失败: {e}")
            return False 