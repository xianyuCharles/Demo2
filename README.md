# Demo2: 电商订单发货处理系统

自动处理电商平台订单，生成发货单并更新库存。

## 功能

- ✅ 支持淘宝/拼多多/抖店等平台订单
- ✅ 自动识别订单字段
- ✅ 智能扣减库存
- ✅ 异常订单标记（缺货、地址异常、重复订单）
- ✅ 生成标准发货单

## 使用方法

### 1. 准备输入文件

将以下文件放入 `input` 目录：

- **订单文件**（CSV）：电商平台导出的订单数据
- **库存表**（xlsx/csv）：当前商品库存

### 2. 运行程序

双击运行 `电商订单发货工具.exe`

### 3. 查看结果

结果自动保存到 `output` 目录：

- `发货单.csv` — 待发货订单清单
- `库存更新.xlsx` — 扣减后的最新库存
- `异常订单.txt` — 需要人工处理的订单

## 支持的电商平台

- 淘宝/天猫
- 拼多多
- 抖店
- 其他平台（通用模式）

## 技术栈

- Python 3.11+
- pandas（数据处理）
- openpyxl（Excel读写）
- PyInstaller（打包为exe）

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python scripts/process.py

# 打包
cd build
build.bat
```

## 项目结构

```
demo2-ecommerce-fulfillment/
├── modules/          # 核心模块
│   ├── order_reader.py      # 订单读取
│   ├── inventory_manager.py # 库存管理
│   └── fulfillment_generator.py # 发货单生成
├── scripts/
│   └── process.py   # 主入口
├── build/
│   └── build.bat    # 打包脚本
├── input/           # 输入文件目录
├── output/          # 输出结果目录
└── requirements.txt # 依赖清单
```
