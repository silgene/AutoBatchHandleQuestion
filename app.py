# -*- coding: UTF-8 -*-
'''
@Project :webProject
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/05 20:41
@Describe:
'''
import json
import time

import pandas as pd
from openai import OpenAI
import gradio as gr
from datetime import datetime
import os
from dotenv import load_dotenv
import re

import threading
processing_lock = threading.Lock()
stop_event = threading.Event()  # 终止事件标志
current_process = None  # 当前处理线程


load_dotenv()
# 配置OpenAI


client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("OPENAI_API_URL"))
prompts_path='./prompts.json'
with open(prompts_path,'r',encoding='utf-8') as f:
    prompts=json.load(f)


def process_question(system_prompt, user_prompt, question, model="gpt-4.0"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt}\n{question}"}
            ]
        )
        print(response)
        return question,response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


# 新增终止函数
def stop_processing():
    stop_event.set()
    return "终止请求已发送，正在安全退出..."

import concurrent.futures

def process_excel(file, system_prompt, user_prompt, model):
    try:
        with processing_lock:
            # 读取Excel
            df = pd.read_excel(file.name, usecols=['序号', '问题'])
            results = []
            output_path = None

            # 处理进度
            total = len(df)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures=[]
                for index, row in df.iterrows():
                    if stop_event.is_set():

                        break

                    # 处理问题
                    if pd.isna(row['问题']):
                        continue


                    task=executor.submit(process_question,system_prompt, user_prompt, row['问题'], model)
                   # answer = process_question(system_prompt, user_prompt, row['问题'], model)
                    futures.append(task)

                for future in concurrent.futures.as_completed(futures):
                    answer=future.result()


                    pattern = r'<think>.*?</think>'
                    question,answer=re.sub(pattern, "", answer,flags=re.DOTALL)

                    # 收集结果
                    results.append({
                        '序号': row['序号'],
                        '系统提示词':system_prompt,
                        '提示词':user_prompt,
                        '问题': question,
                        '处理结果': answer,
                        '完成时间':time.ctime()
                    })

                    # 生成临时DataFrame用于实时显示
                    temp_df = pd.DataFrame(results)
                    progress = f"正在处理第 {index + 1}/{total} 条..."
                    yield progress, temp_df, None

            # 保存最终文件
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = f"output_{timestamp}.xlsx"
            final_df = pd.DataFrame(results)
            final_df.to_excel(output_path, index=False)

            yield "处理完成！", final_df, output_path

    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        yield error_msg, pd.DataFrame(), None
    finally:
        stop_event.clear()




if __name__ == "__main__":


    # Gradio界面
    with gr.Blocks(title="Excel批量问题处理器") as demo:
        gr.Markdown("""
# Excel批量问题处理器
**功能描述**  
- **输入**：  
  - Excel表格（含待处理excel表 表中一定包含序号、问题两个字段）  
  - 问题（需AI执行的具体任务的Prompt）  
- **输出**：  
- 输出批量处理后的结果并保存在excel表中 
        """)




        with gr.Row():
            file_input = gr.File(label="上传Excel文件", file_types=[".xlsx", ".xls"])
            model_select = gr.Dropdown(
                choices=["deepseek-v3", "deepseek-r1"],
                value="deepseek-v3",
                label="选择模型"
            )

        with gr.Row():
            system_input = gr.Textbox(
                label="System Prompt",
                placeholder="输入系统角色设定11...",
                value=prompts.get('SystemPrompt', '你是一个专业助手'),
                lines=3
            )
            prompt_input = gr.Textbox(
                label="User Prompt",
                placeholder="输入处理指令...",
                lines=3
            )

        status_output = gr.Textbox(label="处理状态")

        result_output = gr.Dataframe(
            label="实时处理结果",
            headers=["序号", "问题", "处理结果"],
            interactive=False,

        )
        download_output = gr.File(label="结果文件下载")

        process_btn = gr.Button("开始处理", variant="primary")

        # 新增终止按钮
        stop_btn = gr.Button("终止处理", variant="stop", visible=False)


        # 修改点击事件
        def toggle_buttons():
            return {
                process_btn: gr.update(visible=False),
                stop_btn: gr.update(visible=True)
            }


        process_btn.click(
            fn=toggle_buttons,
            outputs=[process_btn, stop_btn]
        ).then(
            fn=process_excel,
            inputs=[file_input, system_input, prompt_input, model_select],
            outputs=[status_output, result_output, download_output]
        )

        stop_btn.click(
            fn=stop_processing,
            outputs=status_output
        ).then(
            fn=lambda: {process_btn: True, stop_btn: False},
            outputs=[process_btn, stop_btn]
        )

    # 启动应用
    demo.launch(
        server_name="0.0.0.0",
        server_port=7864,
        show_error=True
    )
