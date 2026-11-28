"""Tái lập số liệu hậu kiểm CP3 từ bản dữ liệu BTC lưu cục bộ."""

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


DATA = Path(__file__).resolve().parents[1] / "data-btc" / "preclass" / "answers.csv"


def main():
    with DATA.open(encoding="utf-8-sig", newline="") as file:
        rows = [
            row for row in csv.DictReader(file)
            if row["nguon"] == "pre_post_post" and row["was_correct"].lower() in {"true", "false"}
        ]
    learners = {row["hv"] for row in rows}
    wrong = [row for row in rows if row["was_correct"].lower() == "false"]
    missed_topics = defaultdict(set)
    day_two = []
    for row in wrong:
        if row["kc_code"]:
            missed_topics[row["hv"]].add(row["kc_code"])
        if row["module_code"].startswith("program-day02:"):
            day_two.append(row)
    print(f"Lượt sai: {len(wrong)}/{len(rows)} ({100 * len(wrong) / len(rows):.1f}%)")
    affected = len({row["hv"] for row in wrong})
    print(f"Học viên sai ít nhất một lượt: {affected}/{len(learners)} ({100 * affected / len(learners):.1f}%)")
    missed_counts = [len(topics) for topics in missed_topics.values()]
    all_counts = missed_counts + [0] * (len(learners) - len(missed_counts))
    print(f"Trung vị số mã kiến thức sai trên toàn mẫu: {median(all_counts):g}")
    print(f"Trung vị trong nhóm có ít nhất một mã sai: {median(missed_counts):g}")

    topics = Counter(row["kc_code"] for row in day_two if row["kc_code"])
    print("Ví dụ bản ghi Ngày 2 · mã dòng | mã kiến thức | kết quả | số lượt sai cùng mã")
    for topic, count in sorted(topics.items(), key=lambda item: (-item[1], item[0]))[:5]:
        example = min((row for row in day_two if row["kc_code"] == topic), key=lambda row: row["id"])
        print(f'{example["id"]} | {topic} | {example["was_correct"]} | {count}')


if __name__ == "__main__":
    main()
