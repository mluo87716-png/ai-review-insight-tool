"""
AI消费者评论洞察分析工具 (AI Consumer Review Insight Analyzer)
=================================================================
作者：罗茂婷
项目背景：
  在消费品品牌实习期间，我曾负责人工整理消费者评论、用SPSS做交叉分析来提炼用户洞察。
  这个过程通常需要人工逐条阅读评论、手动分类痛点，耗时且难以规模化。
  这个项目用 Claude API 把"读评论 -> 找情绪/痛点 -> 提炼可执行洞察"这套流程自动化，
  把过去需要几个小时人工完成的工作，压缩到几分钟内，并保留人工复核的空间。

用法：
  1) 演示模式（无需 API Key，开箱即用）：
       python analyze_reviews.py --demo
  2) 真实AI模式（需要设置环境变量 ANTHROPIC_API_KEY）：
       python analyze_reviews.py

输出：
  output/insight_report.md  —— 结构化消费者洞察报告（情感分布 / 高频痛点 / 行动建议）
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output", "insight_report.md")

# 用于demo模式的关键词词典（无需调用AI，纯本地规则，方便没有API Key时也能跑通整个流程）
THEME_KEYWORDS = {
    "成分透明度": ["成分", "配料", "致敏", "安全", "孕期", "备孕"],
    "价格/性价比": ["价格", "贵", "涨", "性价比", "便宜", "划算", "韭菜"],
    "产品效果": ["效果", "提亮", "暗沉", "泛红", "起疹", "闭口", "过敏", "紧绷"],
    "包装设计": ["包装", "瓶口", "破损", "设计感"],
    "物流配送": ["物流", "配送", "发货", "等了"],
    "客服体验": ["客服", "退换货", "态度", "回复"],
}

NEGATIVE_HINTS = ["差", "慢", "冷淡", "破损", "过敏", "起疹", "泛红", "割韭菜", "紧绷", "一般", "犹豫"]
POSITIVE_HINTS = ["好评", "放心", "回购", "推荐", "安利", "明显", "值得", "良心", "专业", "提亮"]


def load_reviews(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify_review_demo(text, rating):
    """演示模式：基于评分+关键词的规则打分，不调用任何外部API。"""
    score = int(rating)
    if score >= 4:
        sentiment = "正面"
    elif score == 3:
        sentiment = "中性"
    else:
        sentiment = "负面"

    matched_themes = [theme for theme, kws in THEME_KEYWORDS.items() if any(k in text for k in kws)]
    if not matched_themes:
        matched_themes = ["其他"]
    return sentiment, matched_themes


def classify_review_ai(client, model, text, rating):
    """真实AI模式：调用 Claude API 对单条评论做结构化情感与主题抽取。"""
    prompt = f"""你是消费者洞察分析师。请阅读这条产品评论，输出严格的JSON，不要任何多余文字：
{{"sentiment": "正面/中性/负面", "themes": ["从[成分透明度,价格/性价比,产品效果,包装设计,物流配送,客服体验,其他]中选择1-2个最相关的"], "pain_point": "用一句话概括用户的核心诉求或痛点，没有则填'无'"}}

评分：{rating}/5
评论内容：{text}
"""
    resp = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 兜底：AI偶尔会多输出文字，尝试截取JSON部分
        start, end = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[start:end + 1])
    return data["sentiment"], data.get("themes", ["其他"]), data.get("pain_point", "无")


def generate_summary_ai(client, model, sentiment_counter, theme_counter, sample_pain_points):
    """调用 Claude API，基于聚合后的统计数据生成一段结构化的业务洞察总结。"""
    prompt = f"""你是品牌方的消费者洞察分析师，请基于以下聚合数据，写一段150字以内的中文业务洞察总结，
包含：1) 整体情感倾向 2) 最值得关注的1-2个痛点 3) 一条可执行的产品或运营建议。语气专业、简洁，像写给品牌经理的周报。

情感分布：{dict(sentiment_counter)}
高频主题：{dict(theme_counter)}
代表性痛点：{sample_pain_points[:5]}
"""
    resp = client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def generate_summary_demo(sentiment_counter, theme_counter, sample_pain_points):
    """演示模式的总结生成：基于规则拼接，逻辑与AI模式一致，只是不依赖外部调用。"""
    total = sum(sentiment_counter.values())
    neg_ratio = sentiment_counter.get("负面", 0) / total * 100 if total else 0
    top_theme = theme_counter.most_common(1)[0][0] if theme_counter else "无"
    pain = sample_pain_points[0] if sample_pain_points else "暂无典型痛点"
    return (
        f"本次共分析{total}条评论，负面占比约{neg_ratio:.0f}%，整体情感以正面为主。"
        f"用户提及最频繁的主题是「{top_theme}」，需要重点关注。"
        f"典型痛点如：{pain}。"
        f"建议品牌团队优先核实并改善高频痛点对应的产品/服务环节，并在物料中强化用户认可的成分透明度卖点。"
    )


def run(demo: bool):
    reviews = load_reviews(DATA_PATH)
    sentiment_counter = Counter()
    theme_counter = Counter()
    pain_points = []
    theme_examples = defaultdict(list)

    client = None
    model = "claude-sonnet-4-6"
    if not demo:
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                print("[提示] 未检测到 ANTHROPIC_API_KEY，自动切换为 --demo 模式运行。")
                demo = True
            else:
                client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            print("[提示] 未安装 anthropic 库（pip install anthropic），自动切换为 --demo 模式运行。")
            demo = True

    for row in reviews:
        text, rating = row["review_text"], row["rating"]
        if demo:
            sentiment, themes = classify_review_demo(text, rating)
            pain_point = text if sentiment == "负面" else None
        else:
            sentiment, themes, pain_point = classify_review_ai(client, model, text, rating)
            pain_point = None if pain_point == "无" else pain_point

        sentiment_counter[sentiment] += 1
        for t in themes:
            theme_counter[t] += 1
            theme_examples[t].append(text)
        if pain_point:
            pain_points.append(pain_point)

    if demo:
        summary = generate_summary_demo(sentiment_counter, theme_counter, pain_points)
    else:
        summary = generate_summary_ai(client, model, sentiment_counter, theme_counter, pain_points)

    write_report(reviews, sentiment_counter, theme_counter, pain_points, summary, demo)


def write_report(reviews, sentiment_counter, theme_counter, pain_points, summary, demo):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    lines = []
    lines.append("# AI消费者评论洞察报告")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"运行模式：{'演示模式（本地规则，无需API Key）' if demo else 'AI模式（Claude API）'}")
    lines.append(f"分析样本量：{len(reviews)} 条评论")
    lines.append("")
    lines.append("## 一、情感分布")
    lines.append("")
    for k, v in sentiment_counter.most_common():
        lines.append(f"- {k}：{v} 条（{v / len(reviews) * 100:.0f}%）")
    lines.append("")
    lines.append("## 二、高频主题")
    lines.append("")
    for k, v in theme_counter.most_common():
        lines.append(f"- {k}：{v} 次提及")
    lines.append("")
    lines.append("## 三、代表性痛点")
    lines.append("")
    for p in pain_points[:8]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## 四、AI生成洞察总结")
    lines.append("")
    lines.append(summary)
    lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"分析完成，报告已生成：{OUTPUT_PATH}")
    print("\n--- 洞察总结预览 ---")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI消费者评论洞察分析工具")
    parser.add_argument("--demo", action="store_true", help="使用本地规则演示模式，无需API Key")
    args = parser.parse_args()
    run(demo=args.demo)
