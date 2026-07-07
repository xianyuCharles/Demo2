@echo off
chcp 65001 >nul
echo ========================================
echo Demo2 电商订单发货处理系统 - 打包脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python环境正常
echo.

REM 安装依赖
echo 正在安装依赖...
pip install -r ..\requirements.txt -q
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

REM 打包
echo 正在打包为EXE...
cd ..
pyinstaller --onefile --name "电商订单发货工具" --add-data "modules;modules" --hidden-import pandas --hidden-import openpyxl --console scripts/process.py
if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

REM 准备交付包
echo.
echo 正在准备交付包...
mkdir 交付包 2>nul
copy dist\电商订单发货工具.exe 交付包\ >nul
mkdir 交付包\input 2>nul
mkdir 交付包\output 2>nul

REM 创建示例文件
echo 订单号,收件人,手机号,地址,商品名,数量,订单金额,下单时间,状态 > 交付包\input\示例订单.csv
echo 2026070001,张三,13800138000,北京市朝阳区xxx街道,商品A,2,199.00,2026-07-07,待发货 >> 交付包\input\示例订单.csv

echo 商品名称,SKU,库存数量 > 交付包\input\库存表.xlsx

echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 交付包位置: 交付包\
echo.
echo 使用说明:
echo 1. 将客户的订单CSV和库存表放入input目录
echo 2. 双击运行"电商订单发货工具.exe"
echo 3. 结果自动保存到output目录
echo.
pause
