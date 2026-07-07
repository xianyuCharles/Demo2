"""
Demo2: 电商订单发货处理系统
主入口脚本

功能：
1. 读取电商订单CSV
2. 读取库存表
3. 生成发货单
4. 更新库存
5. 输出异常订单
"""
import sys
from pathlib import Path

# 兼容PyInstaller打包后的路径
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(BASE_DIR))

import os
os.chdir(BASE_DIR)

from modules.order_reader import OrderReader
from modules.inventory_manager import InventoryManager
from modules.fulfillment_generator import FulfillmentGenerator


def main():
    print("=" * 60)
    print("电商订单发货处理系统 v1.0")
    print("=" * 60)
    print()
    
    # 检查输入文件
    input_dir = Path("input")
    if not input_dir.exists():
        input_dir.mkdir(parents=True)
        print("❌ input目录不存在，已自动创建")
        print("请将电商订单CSV和库存表放入input目录")
        input("按回车键退出...")
        return
    
    # 查找订单文件
    order_files = list(input_dir.glob("*.csv"))
    if not order_files:
        print("❌ 未找到订单CSV文件")
        print("请将电商订单CSV放入input目录")
        input("按回车键退出...")
        return
    
    order_file = order_files[0]
    print(f"📦 读取订单文件: {order_file.name}")
    
    # 查找库存文件
    inventory_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls")) + list(input_dir.glob("*.csv"))
    inventory_files = [f for f in inventory_files if f != order_file]
    
    if not inventory_files:
        print("❌ 未找到库存文件")
        print("请将库存表（xlsx或csv）放入input目录")
        input("按回车键退出...")
        return
    
    inventory_file = inventory_files[0]
    print(f"📊 读取库存文件: {inventory_file.name}")
    print()
    
    # 处理订单
    try:
        print("正在处理订单...")
        reader = OrderReader(str(order_file))
        orders = reader.read()
        valid_orders = reader.get_valid_orders()
        
        summary = reader.get_order_summary()
        print(f"  ✓ 平台: {summary.get('平台', '未知')}")
        print(f"  ✓ 总订单数: {summary.get('总订单数', 0)}")
        print(f"  ✓ 有效订单: {len(valid_orders)}")
        print()
        
        # 加载库存
        print("正在加载库存...")
        inventory = InventoryManager(str(inventory_file))
        inventory.load()
        
        stock_summary = inventory.get_stock_summary()
        print(f"  ✓ 商品总数: {stock_summary.get('商品总数', 0)}")
        print(f"  ✓ 总库存量: {stock_summary.get('总库存量', 0)}")
        print()
        
        # 生成发货单
        print("正在生成发货单...")
        generator = FulfillmentGenerator()
        result = generator.generate(valid_orders, inventory)
        
        shipping_df = result["shipping_list"]
        exceptions_df = result["exceptions"]
        stats = result["stats"]
        
        print(f"  ✓ 可发货订单: {stats.get('可发货订单', 0)}")
        print(f"  ✓ 异常订单: {stats.get('异常订单数', 0)}")
        print(f"  ✓ 成功率: {stats.get('成功率', '0%')}")
        print()
        
        # 扣减库存
        if not shipping_df.empty:
            print("正在扣减库存...")
            deduct_result = inventory.batch_deduct(shipping_df)
            print(f"  ✓ 成功扣减: {deduct_result['success_count']} 单")
            if deduct_result['failed_count'] > 0:
                print(f"  ⚠ 扣减失败: {deduct_result['failed_count']} 单")
            print()
        
        # 保存结果
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        print("正在保存结果...")
        
        # 保存发货单
        shipping_path = output_dir / "发货单.csv"
        generator.save_shipping_list(str(shipping_path))
        print(f"  ✓ 发货单: {shipping_path.name} ({len(shipping_df)} 条)")
        
        # 保存异常订单
        exception_path = output_dir / "异常订单.txt"
        generator.save_exceptions(str(exception_path))
        print(f"  ✓ 异常订单: {exception_path.name} ({len(exceptions_df)} 条)")
        
        # 保存更新后的库存
        inventory_path = output_dir / "库存更新.xlsx"
        inventory.save(str(inventory_path))
        print(f"  ✓ 库存更新: {inventory_path.name}")
        
        print()
        print("=" * 60)
        print("✅ 处理完成！")
        print("=" * 60)
        print()
        print(f"结果已保存到: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"\n❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    # 打包模式下不等待
    if not getattr(sys, 'frozen', False):
        input("按回车键退出...")


if __name__ == "__main__":
    main()
