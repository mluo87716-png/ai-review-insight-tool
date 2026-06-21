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
from collections import Counter
from datetime import datetime

ROOT_DIR = os.path.dirname(__file__)
DEFAULT_DATA_PATH = os.path.join(ROOT_DIR, "data", "sample_reviews.csv")
DEFAULT_OUTPUT_PATH = os.path.join(ROOT_DIR, "output", "insight_report.md")
DEFAULT_JSON_OUTPUT_PATH = os.path.join(ROOT_DIR, "output", "insight_data.json")

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

    pain_point = text if sentiment == "负面" else "无"
    return sentiment, matched_themes, pain_point


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


def run(demo: bool, input_path: str, output_path: str, json_output_path: str):
    reviews = load_reviews(input_path)
    if not reviews:
        raise ValueError("输入文件中没有可分析的评论数据。")

    sentiment_counter = Counter()
    theme_counter = Counter()
    pain_points = []
    analyzed_reviews = []

    client = None
    model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
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
            sentiment, themes, pain_point = classify_review_demo(text, rating)
        else:
            sentiment, themes, pain_point = classify_review_ai(client, model, text, rating)

        normalized_pain_point = None if pain_point == "无" else pain_point

        sentiment_counter[sentiment] += 1
        for t in themes:
            theme_counter[t] += 1
        if normalized_pain_point:
            pain_points.append(normalized_pain_point)

        analyzed_reviews.append(
            {
                "review_id": row.get("review_id", ""),
                "product_name": row.get("product_name", ""),
                "rating": rating,
                "review_text": text,
                "sentiment": sentiment,
                "themes": themes,
                "pain_point": normalized_pain_point or "无",
            }
        )

    if demo:
        summary = generate_summary_demo(sentiment_counter, theme_counter, pain_points)
    else:
        summary = generate_summary_ai(client, model, sentiment_counter, theme_counter, pain_points)

    content_topics = generate_content_topics(theme_counter, pain_points)
    action_items = generate_action_items(theme_counter, pain_points)
    metrics = generate_metric_recommendations()
    write_report(
        reviews,
        sentiment_counter,
        theme_counter,
        pain_points,
        summary,
        content_topics,
        action_items,
        metrics,
        demo,
        output_path,
    )
    write_json_output(
        analyzed_reviews,
        sentiment_counter,
        theme_counter,
        pain_points,
        summary,
        content_topics,
        action_items,
        metrics,
        demo,
        json_output_path,
    )


def generate_content_topics(theme_counter, pain_points):
    """把评论主题转化为运营可用的内容选题。"""
    topics = []
    top_themes = [theme for theme, _ in theme_counter.most_common(3)]
    if "成分透明度" in top_themes:
        topics.append("小红书选题：护肤品成分表到底怎么看？用用户真实评论讲清楚安全感")
    if "价格/性价比" in top_themes:
        topics.append("抖音选题：大促怎么买才不亏？用价格/组合装评论做决策指南")
    if "产品效果" in top_themes:
        topics.append("公众号选题：用户最在意的效果反馈是什么？从评论看功效表达机会")
    if "客服体验" in top_themes or "物流配送" in top_themes:
        topics.append("运营复盘选题：负反馈不只来自产品，也来自客服、物流和规则表达")
    if pain_points and len(topics) < 4:
        topics.append("直播话术选题：把用户最常问的痛点整理成 FAQ，降低购买顾虑")
    return topics[:5]


def generate_action_items(theme_counter, pain_points):
    """生成可直接进入运营复盘的动作建议。"""
    actions = []
    if theme_counter.get("客服体验", 0):
        actions.append("客服侧：建立泛红、过敏、退换货等高频问题的标准回复话术，缩短首次响应时间。")
    if theme_counter.get("物流配送", 0):
        actions.append("履约侧：在大促期间前置物流时效说明，减少用户对等待时间的不确定感。")
    if theme_counter.get("价格/性价比", 0):
        actions.append("电商侧：将组合装、小样、赠品和价格机制做成对比卡，降低用户决策压力。")
    if theme_counter.get("产品效果", 0):
        actions.append("商品侧：在详情页增加适用肤质、使用周期和敏感肌提示，减少效果预期偏差。")
    if theme_counter.get("成分透明度", 0):
        actions.append("内容侧：强化成分透明、温和安心和用户真实反馈，作为种草内容主线。")
    if not actions:
        actions.append("运营侧：先扩大样本量，再判断是否需要进入产品或内容优化。")
    return actions


def generate_metric_recommendations():
    return [
        {"name": "洞察采纳率", "target": "30%+", "definition": "生成洞察中被周报、Brief 或复盘采用的比例"},
        {"name": "内容选题转化率", "target": "20%+", "definition": "AI 生成选题中被实际发布或进入排期的比例"},
        {"name": "人工修正率", "target": "<40%", "definition": "需要运营人员重写或大幅修改的输出比例"},
        {"name": "7日复用率", "target": "25%+", "definition": "同一运营人员 7 天内再次使用工具的比例"},
    ]


def write_report(
    reviews,
    sentiment_counter,
    theme_counter,
    pain_points,
    summary,
    content_topics,
    action_items,
    metrics,
    demo,
    output_path,
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
    lines.append("## 五、内容运营选题建议")
    lines.append("")
    for topic in content_topics:
        lines.append(f"- {topic}")
    lines.append("")
    lines.append("## 六、运营动作建议")
    lines.append("")
    for action in action_items:
        lines.append(f"- {action}")
    lines.append("")
    lines.append("## 七、运营指标建议")
    lines.append("")
    for metric in metrics:
        lines.append(f"- {metric['name']}（目标 {metric['target']}）：{metric['definition']}")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"分析完成，报告已生成：{output_path}")
    print("\n--- 洞察总结预览 ---")
    print(summary)


def write_json_output(
    analyzed_reviews,
    sentiment_counter,
    theme_counter,
    pain_points,
    summary,
    content_topics,
    action_items,
    metrics,
    demo,
    json_output_path,
):
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": "demo" if demo else "ai",
        "sample_size": len(analyzed_reviews),
        "sentiment_distribution": dict(sentiment_counter),
        "theme_distribution": dict(theme_counter),
        "representative_pain_points": pain_points[:8],
        "summary": summary,
        "content_topics": content_topics,
        "action_items": action_items,
        "metrics": metrics,
        "reviews": analyzed_reviews,
    }
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"结构化数据已生成：{json_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI消费者评论洞察分析工具")
    parser.add_argument("--demo", action="store_true", help="使用本地规则演示模式，无需API Key")
    parser.add_argument("--input", default=DEFAULT_DATA_PATH, help="输入CSV路径，默认 data/sample_reviews.csv")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, help="输出报告路径，默认 output/insight_report.md")
    parser.add_argument("--json-output", default=DEFAULT_JSON_OUTPUT_PATH, help="输出JSON路径，默认 output/insight_data.json")
    args = parser.parse_args()
    run(demo=args.demo, input_path=args.input, output_path=args.output, json_output_path=args.json_output)
