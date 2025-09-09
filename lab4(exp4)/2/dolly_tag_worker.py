# =========================================================
# 实验名称（单线程）：JSONL → 单线程模型调用 → 七类打标 → 导出
# 面向对象：大二学生（掌握函数、文件读写与基础异常处理）
#
# 实验目标：
# 1) 学会从 JSONL 读取数据（每行一个样本：instruction + context）。
# 2) 使用 OpenAI 官方 SDK（DashScope 兼容）完成单条分类调用，并实现简单重试。
# 3) 实现单线程函数 tag_records(records, model, show_progress=True)：
#    - 输入：若干条样本记录（包含 id/instruction/context/dolly_category）
#    - 输出：为每条样本预测 {"tag","tag_reason"}，返回列表供并发脚本复用
# 4) 脚本可直接执行：读取 --in_jsonl，单线程完成所有调用，写出 JSONL/CSV。
#
# 评分建议（可调）：
# - 必做 (60%)
#   A. 正确初始化客户端（_make_client）
#   B. 正确拼接 messages 并完成一次调用（_classify_one）
#   C. 正确遍历 records，逐条分类并收集结果（tag_records）
# - 进阶 (40%)
#   D. 实现调用重试与基础异常兜底
#   E. 写出 JSONL 与 CSV（_write_outputs），并在 main 中打印标签分布
#
# 运行依赖：
#   pip install openai==1.* pandas tqdm
#   export DASHSCOPE_API_KEY=sk-xxx
#   !!!: Windows PowerShell 使用 $env:DASHSCOPE_API_KEY="sk-xxx"
#        cmd使用 set DASHSCOPE_API_KEY=sk-xxx（不需要引号！！）
# 运行示例：
#   python dolly_tag_worker.py --in_jsonl ./your_dataset.jsonl --model qwen-plus --n 200
#   python d:/大学/人工智能工程实践（2025暑）/lab4-exp5/2/dolly_tag_worker.py --in_jsonl d:/大学/人工智能工程实践（2025暑）/lab4-exp5/2/exp2.jsonl --model qwen-plus --n 200
# 注意：
# - 本文件中的关键实现已“挖空”，请按中文注释补全。
# - 多线程脚本会调用本文件的 tag_records，请保持函数签名不变。
# =========================================================

# dolly_tag_worker.py
# 依赖：pip install openai==1.* pandas tqdm
import os, json, argparse, time, re
import pandas as pd
from tqdm import tqdm
from openai import OpenAI

# 按要求（含重复项）
TAGS = [
    "open_qa", "creative_writing", "creative_writing",
    "information_extraction", "classification",
    "closeqa", "brainstorming", "general_qa"
]
# 实际用于约束与校验的去重列表
ALLOWED_TAGS = list(dict.fromkeys(TAGS))

SYSTEM_PROMPT = f"""你是一个严格一致性的文本分类器。
任务：仅根据给定文本（由 instruction 与 context 拼接）判断其类型，并在以下集合中“只选一个标签”：
{ALLOWED_TAGS}

标签参考（不需要输出这些说明）：
- open_qa：开放式知识问答/百科型提问，答案开放可多样。
- closeqa：封闭式问答，有明确单一答案，常可直接从材料或固定知识点得到。
- general_qa：一般性问答（非明显百科、非封闭单一答案），如日常咨询、操作指南等。
- information_extraction：从文本中抽取结构化要素（实体/字段/键值）。
- classification：对文本做类别/情感/立场/合规性等判定（输出标签/类别）。
- creative_writing：创意写作/续写/文案/诗歌/故事等创造性生成。
- brainstorming：点子构思/列表式建议/方案罗列（产生多个想法/方向）。

只返回 JSON（无多余文字、无代码块围栏），格式：
{{"tag": "<{ '|'.join(ALLOWED_TAGS) }>", "reason": "<简述依据，尽量短>"}}
"""

USER_TMPL = """待判定文本（instruction + context 已拼接）：
{content}

仅返回 JSON。"""

def _json_fix(s: str):
    s = s.strip()
    s = re.sub(r"^```(?:json)?", "", s, flags=re.I).strip()
    s = re.sub(r"```$", "", s).strip()
    if "{" in s and "}" in s:
        s = s[s.find("{"): s.rfind("}")+1]
    return json.loads(s)

def _make_client():
    """
    TODO：初始化 OpenAI 客户端（DashScope 兼容）
    要求：
      - 从环境变量 DASHSCOPE_API_KEY 读取 key（或直接写死测试 key）
      - base_url 固定为 "https://dashscope.aliyuncs.com/compatible-mode/v1"
      - 返回 OpenAI(...) 客户端实例
    示例：
      client = OpenAI(api_key=..., base_url=...)
      return client
    """
    # === 在这里完成客户端初始化 ===
    api = os.getenv("DASHSCOPE_API_KEY")
    if not api:
        raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
    client = OpenAI(api_key=api, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    return client    
    # raise NotImplementedError("请在 _make_client 中初始化并返回客户端")

def _classify_one(client, model, content, temperature=0.0, max_retries=4):
    """
    TODO：单条样本分类
    步骤：
      1) 构造 messages：
         [
           {"role":"system","content": SYSTEM_PROMPT},
           {"role":"user","content": USER_TMPL.format(content=content)}
         ]
      2) 使用 client.chat.completions.create(...) 发起请求
         - 传入 model、messages、temperature
      3) 解析返回：
         - 取出文本 resp.choices[0].message.content
         - 用 _json_fix(...) 转为 dict，并读取 tag / reason
      4) 归一化与兜底：
         - tag = tag.replace("-", "_").lower()
         - 若 tag 不在 ALLOWED_TAGS：
             · 尝试依据 reason 关键词落到最接近类
             · 否则设为 "general_qa"
      5) 返回 (tag, reason)
    要求：
      - 加入最多 max_retries 次重试；失败等待指数退避（如 1.5s → 2.7s → ...）
      - 异常最终兜底：返回 ("general_qa", f"model_error: {e}")
    """
    # === 在这里完成单条分类的实现 ===
    # 1)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TMPL.format(content=content)}]
    
    for i in range(max_retries):
        try:
            # 2)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            # 3)
            resp_text = response.choices[0].message.content
            resp_dict = _json_fix(resp_text)
            tag = resp_dict.get("tag", "")
            reason = resp_dict.get("reason", "no_reason_provided").strip()
            # 4)
            tag = tag.replace("-", "_").lower()
            if tag not in ALLOWED_TAGS:
                reason_lower = reason.lower()
                if "open" in reason_lower or "百科" in reason_lower or "开放" in reason_lower or "多样" in reason_lower:
                    tag = "open_qa"
                elif "close" in reason_lower or "封闭" in reason_lower or "单一" in reason_lower:
                    tag = "closeqa"
                elif "提取" in reason_lower or "抽取" in reason_lower or "实体" in reason_lower or "字段" in reason_lower:
                    tag = "information_extraction"
                elif "分类" in reason_lower or "类别" in reason_lower or "情感" in reason_lower or "立场" in reason_lower or "合规" in reason_lower:
                    tag = "classification"
                elif "创意" in reason_lower or "写作" in reason_lower or "续写" in reason_lower or "文案" in reason_lower or "诗歌" in reason_lower or "故事" in reason_lower:
                    tag = "creative_writing"
                elif "点子" in reason_lower or "建议" in reason_lower or "方案" in reason_lower or "想法" in reason_lower or "构思" in reason_lower:
                    tag = "brainstorming"
                else:
                    tag = "general_qa"
            # 5)
            return tag, reason
        except Exception as e:
            print(f"请求失败 (第 {i+1}/{max_retries} 次): {e}，等待 {wait_time:.2f} 秒后重试...")
            wait_time = 1.5 ** i
            time.sleep(wait_time)
            if i == max_retries - 1:
                return "general_qa", f"model_error: {e}"
            continue
    return "general_qa", "model_error: unknown"
    # raise NotImplementedError("请在 _classify_one 中完成模型调用与解析")

def _load_jsonl(path, limit=None):
    """读取 JSONL：需要 instruction，可选 context/category/id。"""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if line.strip() == "":
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            records.append({
                "id": obj.get("id", idx),
                "instruction": obj.get("instruction", "") or "",
                "context": obj.get("context", "") or "",
                "dolly_category": obj.get("category", obj.get("dolly_category", "")) or ""
            })
            if limit is not None and len(records) >= limit:
                break
    return records

def tag_records(records, model="qwen-plus", show_progress=True):
    """
    单线程函数：对给定 records（列表[{'id','instruction','context','dolly_category'}]）逐条打标。
    返回 rows 列表（字典），不负责落盘。可被多线程脚本并发调用。
    TODO：
      - 使用 _make_client() 初始化客户端
      - 逐条遍历 records，拼接 content：instruction 或 instruction + "\n\n" + context
      - 调用 _classify_one(...) 得到 (tag, reason)
      - 组装并 append：
        {
          "id": r.get("id"),
          "instruction": instruction,
          "context": context,
          "dolly_category": r.get("dolly_category", ""),
          "tag": tag,
          "tag_reason": reason
        }
      - 返回 rows
    """
    # === 在这里实现单线程遍历与调用 ===
    client = _make_client()
    rows = []
    if show_progress:
        iterator = tqdm(records, desc="单线程分类中...")
    else:
        iterator = records
    
    for r in iterator:
        instruction = r.get("instruction", "")
        context = r.get("context", "")
        if context:
            content = instruction + "\n\n" + context
        else:
            content = instruction
        
        tag, reason = _classify_one(client, model, content)

        rows.append({
            "id": r.get("id"),
            "instruction": instruction,
            "context": context,
            "dolly_category": r.get("dolly_category", ""),
            "tag": tag,
            "tag_reason": reason
        })
    return rows
    # raise NotImplementedError("请在 tag_records 中实现遍历与调用")

def _write_outputs(rows, out_jsonl, out_csv):
    """
    TODO：落盘结果
      - 写 JSONL：逐行 json.dumps(..., ensure_ascii=False)
      - 写 CSV：pd.DataFrame(rows).to_csv(out_csv, index=False)
    """
    # === 在这里写出 JSONL 与 CSV ===
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    # raise NotImplementedError("请在 _write_outputs 中写出文件")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_jsonl", required=True, help="输入数据集（JSONL，每行一个样本）")
    parser.add_argument("--model", default="qwen-plus")
    parser.add_argument("--n", type=int, default=None, help="最多处理前 N 条（默认全量）")
    parser.add_argument("--out_jsonl", default="tag_results.jsonl")
    parser.add_argument("--out_csv", default="tag_results.csv")
    args = parser.parse_args()

    # 加载数据
    records = _load_jsonl(args.in_jsonl, limit=args.n)
    if not records:
        print("未读取到样本，请检查 JSONL 格式与路径。")
        return

    # 单线程执行（调用你在上面完成的 tag_records）
    # TODO：rows = tag_records(records, model=args.model, show_progress=True)
    # === 在这里调用单线程函数 ===
    print(f"共读取 {len(records)} 条样本，进行单线程分类...")
    rows = tag_records(records, model=args.model, show_progress=True)
    # raise NotImplementedError("请在 main 中调用 tag_records 并接收结果 rows")

    # TODO：落盘与统计
    _write_outputs(rows, args.out_jsonl, args.out_csv)
    dist = pd.Series([r["tag"] for r in rows]).value_counts().to_dict()
    print(f"✅ 已写入 {args.out_jsonl} 和 {args.out_csv}")
    print("标签分布：", dist)

if __name__ == "__main__":
    main()
