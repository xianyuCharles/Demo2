"""
发货单生成模块
根据订单和库存生成标准发货单
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class FulfillmentGenerator:
    """发货单生成器"""
    
    def __init__(self):
        self.shipping_list = []
        self.exceptions = []
        
    def generate(self, orders: pd.DataFrame, inventory_manager) -> Dict:
        """
        生成发货单
        返回: {发货单数据, 异常订单数据, 统计信息}
        """
        self.shipping_list = []
        self.exceptions = []
        
        for _, order in orders.iterrows():
            order_no = order.get('订单号', '未知订单')
            product = order.get('商品名', '')
            quantity = int(order.get('数量', 1))
            recipient = order.get('收件人', '')
            phone = order.get('手机号', '')
            address = order.get('地址', '')
            
            # 检查库存
            has_stock, current_stock = inventory_manager.check_stock(product, quantity)
            
            if has_stock:
                # 库存充足，生成发货单
                self.shipping_list.append({
                    "订单号": order_no,
                    "收件人": recipient,
                    "手机号": phone,
                    "地址": address,
                    "商品名称": product,
                    "数量": quantity,
                    "订单金额": order.get('订单金额', ''),
                    "下单时间": order.get('下单时间', ''),
                    "状态": "待发货"
                })
            else:
                # 库存不足，标记异常
                self.exceptions.append({
                    "订单号": order_no,
                    "收件人": recipient,
                    "商品名称": product,
                    "需求数量": quantity,
                    "当前库存": current_stock,
                    "异常类型": "缺货"
                })
        
        # 检查地址异常
        self._check_address_issues()
        
        # 检查重复订单
        self._check_duplicates()
        
        result = {
            "shipping_list": pd.DataFrame(self.shipping_list) if self.shipping_list else pd.DataFrame(),
            "exceptions": pd.DataFrame(self.exceptions) if self.exceptions else pd.DataFrame(),
            "stats": self._get_stats(orders)
        }
        
        return result
    
    def _check_address_issues(self):
        """检查地址异常"""
        for item in self.shipping_list:
            address = item.get('地址', '')
            phone = item.get('手机号', '')
            
            issues = []
            
            # 地址过短
            if len(address) < 10:
                issues.append("地址不完整")
            
            # 手机号格式异常
            if not phone or len(str(phone)) < 11:
                issues.append("手机号异常")
            
            if issues:
                self.exceptions.append({
                    "订单号": item['订单号'],
                    "收件人": item['收件人'],
                    "商品名称": item['商品名称'],
                    "需求数量": item['数量'],
                    "当前库存": "",
                    "异常类型": "；".join(issues)
                })
    
    def _check_duplicates(self):
        """检查重复订单"""
        if not self.shipping_list:
            return
        
        order_nos = [item['订单号'] for item in self.shipping_list]
        seen = set()
        duplicates = []
        
        for order_no in order_nos:
            if order_no in seen:
                duplicates.append(order_no)
            seen.add(order_no)
        
        if duplicates:
            self.exceptions.append({
                "订单号": "重复订单",
                "收件人": "",
                "商品名称": "",
                "需求数量": "",
                "当前库存": "",
                "异常类型": f"发现重复订单: {', '.join(set(duplicates))}"
            })
    
    def _get_stats(self, orders: pd.DataFrame) -> Dict:
        """生成统计信息"""
        total_orders = len(orders)
        success_orders = len(self.shipping_list)
        exception_orders = len(set(e['订单号'] for e in self.exceptions if e.get('订单号')))
        
        stats = {
            "总订单数": total_orders,
            "可发货订单": success_orders,
            "异常订单数": exception_orders,
            "处理时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "成功率": f"{success_orders / total_orders * 100:.1f}%" if total_orders > 0 else "0%"
        }
        
        return stats
    
    def save_shipping_list(self, output_path: str):
        """保存发货单"""
        if not self.shipping_list:
            return None
        
        df = pd.DataFrame(self.shipping_list)
        output_path = Path(output_path)
        
        if output_path.suffix == '.csv':
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(output_path, index=False)
        
        return output_path
    
    def save_exceptions(self, output_path: str):
        """保存异常订单"""
        if not self.exceptions:
            return None
        
        df = pd.DataFrame(self.exceptions)
        output_path = Path(output_path)
        
        if output_path.suffix == '.txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("异常订单清单\n")
                f.write("=" * 60 + "\n\n")
                
                for _, row in df.iterrows():
                    f.write(f"订单号: {row['订单号']}\n")
                    f.write(f"收件人: {row['收件人']}\n")
                    f.write(f"商品: {row['商品名称']}\n")
                    f.write(f"异常类型: {row['异常类型']}\n")
                    if row.get('当前库存'):
                        f.write(f"当前库存: {row['当前库存']}\n")
                    f.write("-" * 40 + "\n\n")
        elif output_path.suffix == '.csv':
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(output_path, index=False)
        
        return output_path
