import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_questionnaire(df):
    """分析動機、焦慮分數與學習困難類型（支援中文內容）"""
    df = df.dropna(subset=["issues"])
    df["issues"] = df["issues"].astype(str)

    # 統計數據
    motivation_avg = df["motivation"].mean()
    anxiety_avg = df["anxiety"].mean()

    # 中文對應表
    issue_mapping = {
        "unclear study method": "讀書方法不明確",
        "careless": "容易粗心",
        "time management": "時間管理不佳",
        "low motivation": "缺乏動機或專注力",
        "lack of focus": "缺乏動機或專注力",
        "unclear understanding": "對課程內容理解不清",
        "exam anxiety": "考試焦慮或壓力過大",
        "high stress": "考試焦慮或壓力過大",
        "language expression": "語文表達或閱讀能力不足",
        "poor reading ability": "語文表達或閱讀能力不足",
        "weak basic concepts": "基礎觀念不牢固",
        "unsuitable materials": "學習資源不足或不適合",
        "lack of resources": "學習資源不足或不適合"
    }

    # 對應中文標籤並統計
    all_issues = df["issues"].str.split(",").explode().str.strip()
    all_issues_cn = all_issues.map(lambda x: issue_mapping.get(x, x))  # fallback 保留原文字
    issue_counts = all_issues_cn.value_counts().to_dict()

    # 個別建議
    individual_feedback = []
    for _, row in df.iterrows():
        name = row["name"]
        subject = row["subject"]
        motivation_score = row["motivation"]
        anxiety_score = row["anxiety"]
        issues = [i.strip() for i in str(row["issues"]).split(",")]

        suggestions = []
        for issue in issues:
            if "unclear study method" in issue:
                suggestions.append("建議進行學習策略指導與目標設定練習")
            elif "careless" in issue:
                suggestions.append("建議訓練注意力與檢查習慣")
            elif "time management" in issue:
                suggestions.append("建議安排個人讀書計畫與時間分配")
            elif "low motivation" in issue or "lack of focus" in issue:
                suggestions.append("建議設計有趣且具挑戰性的課程活動以提升動機")
            elif "unclear understanding" in issue:
                suggestions.append("建議加強基礎概念釐清與補救教學")
            elif "exam anxiety" in issue or "high stress" in issue:
                suggestions.append("建議教授考試策略與壓力管理方法")
            elif "language expression" in issue or "poor reading ability" in issue:
                suggestions.append("建議強化語文閱讀與表達訓練")
            elif "weak basic concepts" in issue:
                suggestions.append("建議回顧基礎內容與適性補強")
            elif "unsuitable materials" in issue or "lack of resources" in issue:
                suggestions.append("建議提供更適切的補充教材或學習平台")

        feedback = {
            "name": name,
            "subject": subject,
            "motivation": motivation_score,
            "anxiety": anxiety_score,
            "suggestions": "；".join(suggestions)
        }
        individual_feedback.append(feedback)

    return motivation_avg, anxiety_avg, issue_counts, individual_feedback

def plot_issue_distribution(issue_counts, output_dir="static/output", filename="issue_distribution.png"):
    os.makedirs(output_dir, exist_ok=True)

    if not issue_counts:
        print("⚠️ 無資料可產生圖表")
        return None

    # ✅ 強制指定中文字型（Windows）
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    labels = list(issue_counts.keys())
    counts = list(issue_counts.values())

    plt.figure(figsize=(10, 6))
    plt.barh(labels, counts, color='skyblue')
    plt.xlabel("出現次數")
    plt.title("學習困難類型分佈圖")
    plt.tight_layout()

    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)
    plt.close()
    return save_path

def generate_language_report(df):
    motivation_avg, anxiety_avg, issue_counts, individual_feedback = analyze_questionnaire(df)
    plot_path = plot_issue_distribution(issue_counts)
    return {
        "motivation_avg": motivation_avg,
        "anxiety_avg": anxiety_avg,
        "issue_counts": issue_counts,
        "individual_feedback": individual_feedback,
        "plot_path": plot_path
    }

