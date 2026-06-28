# Product Requirements Document: AI Review Insight Tool

## 1. Product Overview

AI Review Insight Tool is an AI-powered consumer review insight tool designed for brand operations, e-commerce operations, content operations, and product operations teams.

The product helps operators turn user reviews into actionable business insights, including purchase motivations, churn barriers, key pain points, content topics, product page optimization ideas, and customer service FAQ suggestions.

Published demo:

```text
https://Sophia7877.github.io/ai-review-insight-tool/
```

## 2. Product Positioning

This product is not a general-purpose text summarization tool. It is positioned as an operations workflow tool that helps teams understand:

- Why users choose a product
- Why users hesitate or give up
- Which product messages should be amplified
- Which user concerns should be addressed before purchase
- How user feedback can be converted into content, product page, and service actions

## 3. Problem Statement

Operations teams often receive large volumes of customer reviews, but the review analysis process is usually manual, slow, and hard to reuse.

Key problems:

| Problem | Current Situation | Product Solution |
| --- | --- | --- |
| Too many reviews to process manually | Operators read and copy comments one by one | Automatically extract sentiment, themes, and pain points |
| Hard to understand purchase motivation | Teams only look at ratings and sales data | Identify why users buy or hesitate |
| Content topics rely on guesswork | Content planning depends heavily on personal experience | Generate content ideas from real user concerns |
| AI output is hard to trust | Generic AI summaries can be vague | Add human review criteria and adoption metrics |
| Insights are hard to reuse | Reports are not connected to actions | Export review reports, JSON data, FAQ, and optimization ideas |

## 4. Target Users

### Brand Operations

Need to identify user perception, product selling points, pain points, and communication angles.

### E-commerce Operations

Need to optimize product titles, product detail pages, promotion rules, customer service responses, and conversion barriers.

### Content Operations

Need to convert user concerns into Xiaohongshu, Douyin, WeChat article, livestream, and FAQ topics.

### User Operations

Need to identify negative feedback, repurchase opportunities, user needs, and service improvement areas.

## 5. Core Use Cases

### Use Case 1: New Product Launch Review

After a new product launch, operators need to understand whether users understand the core selling points and whether early negative feedback appears.

Expected output:

- Core selling point perception
- Early negative feedback
- Product page optimization ideas
- Content angles for launch follow-up

### Use Case 2: Promotion Campaign Review

After a campaign or major promotion, operators need to identify issues related to pricing, gifts, logistics, and customer service.

Expected output:

- Conversion barriers
- Promotion rule confusion
- Customer service FAQ
- Campaign review summary

### Use Case 3: Content Topic Planning

Content teams need to find content topics based on real user questions rather than assumptions.

Expected output:

- Xiaohongshu topic ideas
- Douyin short video angles
- Livestream FAQ topics
- WeChat article ideas

### Use Case 4: Product Detail Page Optimization

E-commerce teams need to place high-frequency user concerns in product detail pages before users make a purchase decision.

Expected output:

- Key concerns to place above the fold
- Suitable/unsuitable user scenarios
- Ingredient or feature explanation
- Price and promotion clarification

## 6. Product Goals

### Business Goal

Help operations teams convert user reviews into actionable operations decisions that improve user understanding, trust, and purchase intent.

### User Goal

Allow operators to upload or paste user reviews and quickly receive a structured review insight report.

### Product Goal

Build a lightweight, easy-to-use workflow from review input to AI analysis, human review, output adoption, and performance measurement.

## 7. MVP Scope

### 7.1 Review Input

Users can input reviews through:

- Sample data
- Text area
- CSV/TXT file upload

### 7.2 Review Analysis

The product analyzes reviews and outputs:

- Sentiment distribution
- High-frequency themes
- Representative pain points
- Purchase motivations
- Conversion barriers

### 7.3 Operations Output

The product converts insights into:

- Content topic ideas
- Product detail page suggestions
- Customer service FAQ ideas
- Campaign review recommendations

### 7.4 Export and Reuse

Users can:

- Copy weekly report summary
- Download Markdown report
- Download structured JSON data

### 7.5 Early Adoption Templates

The demo includes three activation templates:

- New product launch review
- Promotion campaign review
- Negative review and customer service FAQ analysis

## 8. Non-MVP Scope

The current version does not include:

- Direct integration with e-commerce platforms
- Automatic review scraping
- Real-time data dashboards
- Automatic content publishing
- Replacement of human business judgment
- Enterprise-level user permission management

## 9. User Journey

```text
Open demo page
  ↓
Select an operations scenario template
  ↓
Load sample reviews or upload own reviews
  ↓
Generate insight report
  ↓
Review sentiment, themes, pain points, content topics, and suggestions
  ↓
Copy summary or download report/data
  ↓
Apply insights to content planning, product detail page optimization, FAQ, or campaign review
```

## 10. Key Features

| Feature | Description | User Value |
| --- | --- | --- |
| Sentiment analysis | Classifies reviews into positive, neutral, and negative | Quickly understand user attitude |
| Theme detection | Identifies topics such as price, product effect, ingredients, packaging, logistics, and customer service | Find what users care about most |
| Pain point extraction | Extracts representative negative comments | Support weekly reports and improvement plans |
| Purchase motivation analysis | Identifies why users choose the product | Amplify effective selling points |
| Conversion barrier analysis | Identifies why users hesitate or churn | Reduce decision friction |
| Content topic generation | Converts review insights into content ideas | Support content operations and growth |
| Exportable report | Generates Markdown and JSON outputs | Make insights reusable |
| Human review framework | Defines adoption and correction criteria | Improve trust in AI output |

## 11. Success Metrics

| Metric | Target |
| --- | --- |
| Review analysis completion rate | 80%+ |
| Insight adoption rate | 30%+ |
| Content topic conversion rate | 20%+ |
| Report copy/download rate | 25%+ |
| Manual correction rate | Below 40% |
| 7-day reuse rate | 25%+ |

## 12. Early Adoption Strategy

The early adoption strategy focuses on a clear, low-friction hook:

> Upload 30 reviews and understand why users buy or hesitate within 10 minutes.

Early target users:

- E-commerce operators
- Content operators
- Brand operators
- User/customer service operators

Early activation methods:

- Show sample report before asking users to input data
- Provide fixed scenario templates
- Allow copy-paste review input
- Avoid requiring platform integration
- Provide reusable outputs such as reports, content ideas, product page suggestions, and FAQ drafts

## 13. Risks and Assumptions

### Assumptions

- Operators are willing to paste or upload review data if the output is immediately useful.
- Small sample review analysis is valuable for early-stage product validation.
- Human review is necessary before AI insights enter business workflows.

### Risks

- AI-generated insights may be too generic.
- Review samples may not represent the full customer base.
- Users may need industry-specific templates.
- Without real platform data integration, long-term retention may be limited.

## 14. Future Roadmap

### V0.2: Operations Workspace

- Better visualization for sentiment and themes
- More scenario templates
- One-click copy for content topics and FAQ

### V0.3: Human Review Loop

- Mark each insight as adopted, edited, or rejected
- Track manual correction reasons
- Improve prompt and output structure based on feedback

### V0.4: Competitor Review Comparison

- Compare reviews across multiple products
- Identify competitive advantages and weaknesses
- Generate differentiated content strategy

### V1.0: Lightweight Review Insight Platform

- Historical report management
- Team collaboration
- Multi-industry templates
- Dashboard for insight adoption and reuse

## 15. Open Questions

- Which industry should be prioritized after the skincare/e-commerce demo scenario?
- Should the next version focus on content operations, e-commerce operations, or brand operations?
- What review sample size is enough for reliable early-stage insights?
- Which exported format is most useful for real operations teams: Markdown, spreadsheet, JSON, or dashboard?

