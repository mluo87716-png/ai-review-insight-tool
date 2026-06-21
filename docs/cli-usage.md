# CLI Usage

## 基础命令

```bash
python analyze_reviews.py --demo
```

生成：

- `output/insight_report.md`
- `output/insight_data.json`

## 参数说明

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--demo` | 关闭 | 使用本地规则演示模式，不需要 API Key |
| `--input` | `data/sample_reviews.csv` | 输入 CSV 文件路径 |
| `--output` | `output/insight_report.md` | Markdown 报告输出路径 |
| `--json-output` | `output/insight_data.json` | JSON 结构化数据输出路径 |

## 自定义输入输出

```bash
python analyze_reviews.py \
  --demo \
  --input data/sample_reviews.csv \
  --output output/my_report.md \
  --json-output output/my_data.json
```

## AI 模式

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_api_key"
python analyze_reviews.py
```

## 输入 CSV 格式

必须包含以下字段：

```csv
review_id,product_name,rating,review_text
1,玉肌焕颜精华,5,成分表写得很清楚，会回购
```

## 输出 JSON 字段

```json
{
  "generated_at": "2026-06-21 12:00",
  "mode": "demo",
  "sample_size": 25,
  "sentiment_distribution": {},
  "theme_distribution": {},
  "representative_pain_points": [],
  "summary": "",
  "content_topics": [],
  "action_items": [],
  "metrics": [],
  "reviews": []
}
```
