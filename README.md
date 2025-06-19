# Silgene-AIBatchHandle

> Excel批量问题处理器。输入Excel表格（含序号、问题字段）和AI任务Prompt，输出批量处理结果到新的Excel表。

## 简介

本项目旨在提供一个便捷的工具，用于批量处理Excel表格中的特定问题。用户可以提供一个包含“序号”和“问题”字段的Excel文件，并指定一个针对这些问题的人工智能处理指令（Prompt）。脚本将逐行读取问题，利用AI模型根据给定的Prompt生成答案或处理结果，并将这些结果整合后输出到一个新的Excel文件中。


## 快速开始

1.  **克隆仓库**

    ````bash
    # git clone https://github.com/silgene/Silgene-AIBatchHandle
    # cd Silgene-AIBatchHandle
    ````

2.  **环境准备**：
    *   Python 3.8+

3.  **运行脚本**：
    ````bash
    python app.py
    ````

## 项目结构


`````text
├── app.py             # 主执行脚本
├── requirements.txt    # Python依赖包列表
└── README.md           # 项目说明文档
`````

## 开发状态
- 当前阶段：开发中 (请根据实际情况选择：开发中 / 测试中 / 已上线 / 原型验证)
- 版本号：v0.1.0 (或根据实际情况填写)
- 最近更新：YYYY-MM-DD (请填写实际日期)
## 负责人
开发负责人：杨灏
