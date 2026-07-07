"""
订单读取模块
支持淘宝/拼多多/抖店等电商平台导出的CSV订单文件
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional


class OrderReader:
    """电商订单读取器"""
    
    # 各平台标准字段映射
    PLATFORM_MAPPINGS = {
        "taobao": {
            "订单号": ["买家会员名", "买家会员ID"],
            "收件人": ["收件人姓名", "收货人姓名", "收货人"],
            "手机号": ["手机号码", "买家电话", "收货人电话", "收货人手机"],
            "地址": ["收货地址", "买家地址", "详细地址"],
            "商品名": ["宝贝标题", "商品名称", "商品标题"],
            "数量": ["购买数量", "商品数量", "数量"],
            "订单金额": ["实付金额", "订单金额", "买家实付金额"],
            "下单时间": ["订单创建时间", "创建时间", "下单时间"],
            "状态": ["订单状态", "交易状态"]
        },
        "pdd": {
            "订单号": ["订单号"],
            "收件人": ["收货人"],
            "手机号": ["收货人手机号", "手机号"],
            "地址": ["收货地址", "详细地址"],
            "商品名": ["商品名称", "商品标题"],
            "数量": ["数量", "商品数量"],
            "订单金额": ["订单金额", "实付金额"],
            "下单时间": ["下单时间", "创建时间"],
            "状态": ["订单状态"]
        },
        "douyin": {
            "订单号": ["订单编号", "子订单编号"],
            "收件人": ["收货人"],
            "手机号": ["收货人手机号", "联系电话"],
            "地址": ["收货地址", "详细地址"],
            "商品名": ["商品名称", "商品标题"],
            "数量": ["商品数量", "数量"],
            "订单金额": ["订单金额", "支付金额"],
            "下单时间": ["下单时间", "创建时间"],
            "状态": ["订单状态"]
        }
    }
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df = None
        self.platform = None
        
    def read(self) -> pd.DataFrame:
        """读取订单CSV文件"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"订单文件不存在: {self.csv_path}")
        
        # 尝试不同编码读取
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                self.df = pd.read_csv(self.csv_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if self.df is None:
            raise ValueError(f"无法读取CSV文件，请检查编码格式: {self.csv_path}")
        
        # 自动识别平台
        self.platform = self._detect_platform()
        
        # 标准化字段
        self.df = self._normalize_fields()
        
        return self.df
    
    def _detect_platform(self) -> str:
        """自动识别电商平台"""
        columns = set(self.df.columns)
        
        # 根据特征字段判断平台
        if '买家会员名' in columns or '宝贝标题' in columns:
            return "taobao"
        elif '订单号' in columns and '收货人' in columns:
            return "pdd"
        elif '订单编号' in columns or '子订单编号' in columns:
            return "douyin"
        else:
            return "generic"
    
    def _normalize_fields(self) -> pd.DataFrame:
        """标准化字段名称"""
        if self.platform == "generic":
            return self._normalize_generic()
        
        mapping = self.PLATFORM_MAPPINGS.get(self.platform, {})
        rename_map = {}
        
        for standard_name, possible_names in mapping.items():
            for name in possible_names:
                if name in self.df.columns:
                    rename_map[name] = standard_name
                    break
        
        return self.df.rename(columns=rename_map)
    
    def _normalize_generic(self) -> pd.DataFrame:
        """通用字段映射（无法识别平台时）"""
        # 尝试模糊匹配常见字段
        column_mapping = {}
        
        for col in self.df.columns:
            col_lower = str(col).lower()
            if '订单' in col_lower and ('号' in col_lower or '编' in col_lower):
                column_mapping[col] = '订单号'
            elif '收件' in col_lower or '收货' in col_lower:
                if '人' in col_lower or '姓名' in col_lower:
                    column_mapping[col] = '收件人'
                elif '地址' in col_lower:
                    column_mapping[col] = '地址'
                elif '电话' in col_lower or '手机' in col_lower:
                    column_mapping[col] = '手机号'
            elif '商品' in col_lower or '宝贝' in col_lower:
                column_mapping[col] = '商品名'
            elif '数量' in col_lower:
                column_mapping[col] = '数量'
            elif '金额' in col_lower or '金额' in col_lower:
                column_mapping[col] = '订单金额'
        
        return self.df.rename(columns=column_mapping)
    
    def get_valid_orders(self) -> pd.DataFrame:
        """获取有效订单（排除已取消的）"""
        if '状态' not in self.df.columns:
            return self.df
        
        invalid_states = ['已取消', '已关闭', '退款成功', '交易关闭']
        mask = ~self.df['状态'].isin(invalid_states)
        return self.df[mask].copy()
    
    def get_order_count(self) -> int:
        """获取订单总数"""
        return len(self.df) if self.df is not None else 0
    
    def get_order_summary(self) -> Dict:
        """获取订单摘要信息"""
        if self.df is None:
            return {}
        
        summary = {
            "总订单数": len(self.df),
            "平台": self.platform or "未知",
            "文件": self.csv_path.name
        }
        
        if '订单金额' in self.df.columns:
            summary["总金额"] = f"¥{self.df['订单金额'].sum():.2f}"
        
        return summary
