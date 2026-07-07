"""
库存管理模块
读取库存表，扣减发货数量，生成更新后的库存
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
import json


class InventoryManager:
    """库存管理器"""
    
    def __init__(self, inventory_path: str):
        self.inventory_path = Path(inventory_path)
        self.df = None
        self.original_stock = None
        
    def load(self) -> pd.DataFrame:
        """加载库存表"""
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"库存文件不存在: {self.inventory_path}")
        
        # 根据文件扩展名选择读取方式
        if self.inventory_path.suffix in ['.xlsx', '.xls']:
            self.df = pd.read_excel(self.inventory_path)
        else:
            self.df = pd.read_csv(self.inventory_path)
        
        # 保存原始库存（用于异常回滚）
        self.original_stock = self.df.copy()
        
        # 标准化字段
        self._normalize_fields()
        
        return self.df
    
    def _normalize_fields(self):
        """标准化库存字段"""
        column_mapping = {}
        
        for col in self.df.columns:
            col_lower = str(col).lower()
            if '商品' in col_lower or 'sku' in col_lower or '名称' in col_lower:
                if 'sku' in col_lower:
                    column_mapping[col] = 'SKU'
                elif '名称' in col_lower or '商品' in col_lower:
                    column_mapping[col] = '商品名称'
            elif '库存' in col_lower or '数量' in col_lower or '存量' in col_lower:
                column_mapping[col] = '库存数量'
        
        self.df = self.df.rename(columns=column_mapping)
    
    def check_stock(self, product_name: str, quantity: int) -> Tuple[bool, int]:
        """
        检查库存是否充足
        返回: (是否充足, 当前库存)
        """
        # 先尝试按商品名称匹配
        match = None
        if '商品名称' in self.df.columns:
            match = self.df[self.df['商品名称'] == product_name]
        
        # 如果商品名称没匹配到，再尝试SKU
        if match is None or match.empty:
            if 'SKU' in self.df.columns:
                match = self.df[self.df['SKU'] == product_name]
        
        if match is None or match.empty:
            return False, 0
        
        current_stock = match['库存数量'].iloc[0]
        return current_stock >= quantity, int(current_stock)
    
    def deduct_stock(self, product_name: str, quantity: int) -> bool:
        """
        扣减库存
        返回: 是否成功
        """
        # 先尝试按商品名称匹配
        idx = None
        if '商品名称' in self.df.columns:
            idx = self.df[self.df['商品名称'] == product_name].index
        
        # 如果商品名称没匹配到，再尝试SKU
        if idx is None or len(idx) == 0:
            if 'SKU' in self.df.columns:
                idx = self.df[self.df['SKU'] == product_name].index
        
        if idx is None or len(idx) == 0:
            return False
        
        # 扣减库存
        current = self.df.loc[idx[0], '库存数量']
        if current < quantity:
            return False
        
        self.df.loc[idx[0], '库存数量'] = current - quantity
        return True
    
    def batch_deduct(self, orders: pd.DataFrame) -> Dict:
        """
        批量扣减库存
        返回: {成功订单数, 失败订单数, 缺货清单}
        """
        result = {
            "success_count": 0,
            "failed_count": 0,
            "out_of_stock": []
        }
        
        for _, order in orders.iterrows():
            # 兼容不同的列名
            product = order.get('商品名称', '') or order.get('商品名', '')
            quantity = int(order.get('数量', 1))
            
            if self.deduct_stock(product, quantity):
                result["success_count"] += 1
            else:
                result["failed_count"] += 1
                result["out_of_stock"].append({
                    "订单号": order.get('订单号', ''),
                    "商品": product,
                    "需求数量": quantity,
                    "原因": "库存不足或商品不存在"
                })
        
        return result
    
    def save(self, output_path: str = None):
        """保存更新后的库存表"""
        if output_path is None:
            output_path = self.inventory_path.with_stem(self.inventory_path.stem + "_更新")
        
        output_path = Path(output_path)
        
        if output_path.suffix in ['.xlsx', '.xls']:
            self.df.to_excel(output_path, index=False)
        else:
            self.df.to_csv(output_path, index=False)
        
        return output_path
    
    def get_stock_summary(self) -> Dict:
        """获取库存摘要"""
        if self.df is None:
            return {}
        
        summary = {
            "商品总数": len(self.df),
            "总库存量": int(self.df['库存数量'].sum())
        }
        
        # 低库存预警（库存<10）
        low_stock = self.df[self.df['库存数量'] < 10]
        summary["低库存商品数"] = len(low_stock)
        
        return summary
