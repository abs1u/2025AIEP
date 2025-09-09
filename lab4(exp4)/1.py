# =========================================================
# 实验名称：基于 DashScope 兼容接口的终端聊天（基础版）
# 面向对象：大二学生（已学 Python 基础 I/O）
#
# 实验目标：
# 1) 学会使用 百炼的api 调用对话模型（如 qwen-plus）。
# 2) 掌握最基本的对话循环：读取输入 → 调用接口 → 输出答案 → 维护历史 messages。
# 3) 能正确处理用户退出命令与异常（网络、鉴权失败等）。
#
# 任务与评分建议（可按需调整）：
# - 必做 (60%)：
#   A. 正确初始化客户端（api_key 与 base_url）；
#   B. 维护 messages（含一条 system 提示词）；
#   C. 循环读取用户输入并调用接口，打印模型回复；
#   D. 支持 /exit 退出；异常时不崩溃。
# - 进阶 (40%)：
#   E. 新增 /reset 指令（清空对话但保留 system）；
#   F. 将对话历史追加保存为 JSONL（/save chat_xxx.jsonl）。
#
# 运行前准备：
#   pip install openai==1.*
#   export DASHSCOPE_API_KEY=sk-xxx
#
# 运行示例：
#   python chat_simple.py
#
# 注意：
# - 本文件已在关键位置“挖空”。请按中文注释补全代码后再运行。
# =========================================================

import os
from openai import OpenAI
import json
from datetime import datetime

# TODO: 1) 初始化 OpenAI 客户端（DashScope 兼容）
#   - 使用环境变量 DASHSCOPE_API_KEY 或直接写入 api_key="sk-xxx"
#   - base_url 必须是 "https://dashscope.aliyuncs.com/compatible-mode/v1"
#   - 参考：
#       client = OpenAI(api_key=..., base_url=...)
api = os.getenv("DASHSCOPE_API_KEY")
client = OpenAI(api_key=api, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")  # ← 在这里创建客户端对象

# TODO: 2) 选择模型名（可从环境变量 MODEL 读取，默认 "qwen-plus"）
MODEL = os.getenv("MODEL", "qwen-plus")   # 例如：os.getenv("MODEL", "qwen-plus")

def main():
    # TODO: 3) 初始化 messages，并包含一条 system 提示词
    #   messages 示例：[{"role": "system", "content": "You are a helpful assistant."}]
    sys_msg = {"role": "system", "content": "You are a helpful assistant."}
    messages = [sys_msg]  # ← 创建并赋值一个列表

    # TODO: 4) 打印提示信息，例如“已就绪，输入 /exit 退出”
    print(f"你好啊，我是{MODEL}，你可以随时问我任何问题！如果想说再见，就输入 /exit 退出")

    while True:
        try:
            # TODO: 5) 从终端读取一行用户输入（去掉首尾空格）
            # q = input(...).strip()
            q = input("请输入您的问题或要求：").strip()
        except (KeyboardInterrupt, EOFError):
            # TODO: 6) 处理 Ctrl+C / EOF 退出：打印提示后 break
            print("\n\n啊哦，系统被中断。再见！")
            break

        # TODO: 7) 忽略空输入（continue），支持 '/exit'/'exit'/'quit' 主动退出
        # if not q: ...
        # if q.lower() in ("/exit", "exit", "quit"): ...
        if not q:
            continue
        if q.lower() in ("/exit", "exit", "quit", "/quit"):
            print("Ade! 再见！")
            break
        elif q.lower() == "/reset":
            messages = [sys_msg]
            print("对话已重置。")
            continue
        elif q.lower().startswith("/save"):
            filename = q[6:].strip()
            if not filename:
                time = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_{time}.jsonl"
                print("将使用默认文件名：", filename)
            
            history = messages[1:]  # 不保存 system 提示词
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    for msg in history:
                        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
                print(f"对话已保存到 {filename}")
            except Exception as e:
                print(f"保存失败：{e}")
            continue

        # TODO: 8) 将用户输入追加到 messages（role="user"）
        # messages.append({...})
        messages.append({"role": "user", "content": q})

        try:
            # TODO: 9) 发起一次 Chat Completion 调用
            # resp = client.chat.completions.create(model=MODEL, messages=messages)
            resp = client.chat.completions.create(model=MODEL, messages=messages)
            # print(resp)  # 可选：打印完整响应，便于调试

            # TODO: 10) 从 resp 中取出 assistant 文本
            # a = resp.choices[0].message.content
            a = resp.choices[0].message.content

        except Exception as e:
            # TODO: 11) 调用失败时打印错误，并回滚刚刚追加的 user 消息
            # print(f"调用失败：{e}")
            # messages.pop()
            print(f"Oh no! 调用失败：{e}")
            messages.pop()
            continue

        # TODO: 12) 打印 assistant 文本到终端
        # print(f"助理：{a}")
        print(f"<{MODEL}>助理：{a}")

        # TODO: 13) 将 assistant 回复也追加进 messages（role="assistant"）
        # messages.append({...})
        messages.append({"role": "assistant", "content": a})

if __name__ == "__main__":
    main()
