#!/usr/bin/env python3
"""Validate editorial metadata and render the weekly's Markdown and RSS."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime, time, timedelta
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Shanghai")
STATUSES = {"reviewed", "partial", "unavailable", "not_checked"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def iso(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value),
            f"日期格式错误：{value!r}")
    return date.fromisoformat(value)


def public_url(value):
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username


def validate_github(snapshot, today):
    require(re.fullmatch(r"[\w.-]+/[\w.-]+", snapshot["repository"]), "GitHub 仓库名不合法")
    require(type(snapshot["stars"]) is int and snapshot["stars"] >= 0, "star 快照必须为非负整数")
    require(iso(snapshot["checked_on"]) <= today, "star 查询日期不能在未来")


def validate(issues, config, today=None):
    today = today or datetime.now(TZ).date()
    require(config["timezone"] == "Asia/Shanghai", "排期必须使用 Asia/Shanghai")
    require(re.fullmatch(r"[\w.-]+/[\w.-]+", config["repository"]), "仓库名不合法")
    sources = config["sources"]
    source_ids = {s["id"] for s in sources}
    require(len(source_ids) == len(sources), "信息源 ID 重复")
    for source in sources:
        require(public_url(source["url"]), f"信息源链接错误：{source['id']}")
        if "github" in source:
            validate_github(source["github"], today)
    require(bool(issues), "没有期刊数据")
    news_ids = set()
    previous_end = None
    for number, issue in enumerate(issues, 1):
        issue_id = issue["id"]
        require(issue_id == f"{number:03}", f"期号必须连续：{issue_id}")
        start, end, published = map(iso, (issue["start"], issue["end"], issue["published_on"]))
        require(start.weekday() == 0 and end == start + timedelta(days=6),
                f"{issue_id}: 覆盖范围必须是完整周一至周日")
        require(end < published <= today, f"{issue_id}: 发布日期不正确或覆盖周尚未结束")
        if previous_end:
            require(start == previous_end + timedelta(days=1), f"{issue_id}: 覆盖周有重复或缺失")
        previous_end = end
        require(issue["title"].strip() and issue["summary"].strip(), f"{issue_id}: 缺少标题或导读")
        checks = issue["source_checks"]
        checked_ids = {c["id"] for c in checks}
        require(len(checks) == len(checked_ids) and checked_ids <= source_ids,
                f"{issue_id}: 来源核查记录重复或未知")
        if number == len(issues):
            require(checked_ids == source_ids, f"{issue_id}: 每个配置来源必须有核查状态")
        for check in checks:
            require(check["status"] in STATUSES and check["note"].strip(), "缺少来源状态说明")
            require(iso(check["checked_on"]) <= today, "来源核查日期不能在未来")
        entry_ids = set()
        for section in issue["sections"]:
            require(section["title"].strip() and section["entries"], "不保留空栏目")
            for entry in section["entries"]:
                key = entry["id"]
                require(key not in entry_ids, f"{issue_id}: 条目 ID 重复：{key}")
                entry_ids.add(key)
                for field in ("title", "summary", "why", "limits"):
                    require(bool(entry[field].strip()), f"{key}: 缺少 {field}")
                require(type(entry["evergreen"]) is bool, f"{key}: evergreen 必须为布尔值")
                event_date = iso(entry["date"]) if entry["date"] else None
                require(event_date is None or event_date <= today, f"{key}: 事件日期不能在未来")
                if not entry["evergreen"]:
                    require(event_date is not None and start <= event_date <= end,
                            f"{key}: 新闻日期不在覆盖周内；旧文应标记 evergreen")
                    require(key not in news_ids, f"重复报道同一新闻事件：{key}")
                    news_ids.add(key)
                require(bool(entry["links"]), f"{key}: 缺少原始来源")
                for link in entry["links"]:
                    require(link["label"].strip() and public_url(link["url"]), f"{key}: 来源链接错误")
                verification = entry["verification"]
                if "github" in entry:
                    validate_github(entry["github"], today)
                require(verification["level"] in {"source-reviewed", "reproduced"}, f"{key}: 核查等级错误")
                checked = iso(verification["checked_on"])
                require(checked <= today and (event_date is None or checked >= event_date), f"{key}: 核查日期错误")
                if verification["level"] == "reproduced":
                    require(bool(verification.get("reproduction")), f"{key}: 缺少复现条件和结果记录")
        require(issue["lead_id"] in entry_ids if entry_ids else issue["lead_id"] is None,
                f"{issue_id}: 导读指向不存在的条目")
        require(issue["exercise"].strip(), f"{issue_id}: 缺少实践建议")
        for correction in issue["corrections"]:
            require(published <= iso(correction["date"]) <= today and correction["text"].strip(),
                    f"{issue_id}: 更正记录错误")


def load(root=ROOT):
    config = json.loads((root / "data/sources.json").read_text())
    files = sorted((root / "data/issues").glob("*.json"), key=lambda p: int(p.stem))
    issues = []
    for path in files:
        issue = json.loads(path.read_text())
        require(path.stem == issue["id"], f"文件名与期号不一致：{path.name}")
        issues.append(issue)
    validate(issues, config)
    return issues, config


def entries(issue):
    return [entry for section in issue["sections"] for entry in section["entries"]]


def render_issue(issue, source_names=None):
    source_names = source_names or {}
    issue_id = issue["id"]
    lines = [f"# Agent & LLM 前沿周报 · 第 {issue_id} 期", "", f"## {issue['title']}", "",
             f"> 覆盖：{issue['start']} — {issue['end']}｜发布：{issue['published_on']}｜排期：北京时间", "",
             "[返回首页](../README.md) · [往期归档](../ARCHIVE.md) · [信息源](../SOURCES.md)", "", issue["summary"], ""]
    if issue["lead_id"]:
        lead = next(e for e in entries(issue) if e["id"] == issue["lead_id"])
        lines += [f"**本周值得先看：[{lead['title']}]({lead['links'][0]['url']})**。{lead['why']}", ""]
    lines += ["## 本期目录", ""]
    for index, section in enumerate(issue["sections"], 1):
        lines.append(f"- [{section['title']}](#section-{index})")
    lines += ["- [本期动手](#practice)", "- [核查范围](#coverage)", ""]
    count = 0
    for index, section in enumerate(issue["sections"], 1):
        lines += [f'<a id="section-{index}"></a>', "", f"## {section['title']}", ""]
        for entry in section["entries"]:
            count += 1
            label = "长期参考 · 非本周新闻" if entry["evergreen"] else entry.get("date_label", "事件日期") + " " + entry["date"]
            if entry["evergreen"] and entry["date"]:
                label += f" · 原文 {entry['date']}"
            lines += [f"### {count}. {entry['title']}", "", f"`{label}` · " + " / ".join(entry["tags"]), "",
                      *([f"⭐ **{entry['github']['stars']:,}** · 查询日期 {entry['github']['checked_on']} · [{entry['github']['repository']}](https://github.com/{entry['github']['repository']})", ""] if "github" in entry else []),
                      entry["summary"], "", f"**为什么值得看：** {entry['why']}", "",
                      f"**适用范围与限制：** {entry['limits']}", "",
                      " · ".join(f"[{link['label']}]({link['url']})" for link in entry["links"]), ""]
    lines += ['<a id="practice"></a>', "", "## 本期动手", "", issue["exercise"], "",
              '<a id="coverage"></a>', "", "## 核查范围", ""]
    counts = Counter(c["status"] for c in issue["source_checks"])
    lines += [f"配置 {len(issue['source_checks'])} 个信息源；完成约定范围检查 {counts['reviewed']} 个、部分检查 {counts['partial']} 个、访问失败 {counts['unavailable']} 个、未检查 {counts['not_checked']} 个。精选不代表全网穷尽。", "",
              "“完成检查”指完成下表注明的范围，不代表读完该网站全部内容；“部分检查”表示只检查入口、目录或部分材料。", "",
              f"条目证据与来源检查说明见 [本期数据](../data/issues/{issue_id}.json)。除条目另有说明外，均为原始材料核查，未独立复现实验或执行软件升级。", ""]
    gaps = [c for c in issue["source_checks"] if c["status"] in {"unavailable", "not_checked"}]
    if gaps:
        lines += ["本期缺口：" + "；".join(f"{c['id']}：{c['note']}" for c in gaps) + "。", ""]
    status_names = {"reviewed": "完成范围检查", "partial": "部分检查", "unavailable": "访问失败", "not_checked": "未检查"}
    lines += ["<details>", "<summary>展开本期来源检查说明</summary>", "", "| 来源 | 状态 | 范围 |", "| --- | --- | --- |"]
    lines += [f"| {source_names.get(c['id'], c['id'])} | {status_names[c['status']]} | {c['note']} |" for c in issue["source_checks"]]
    lines += ["", "</details>", ""]
    lines += ["## 更正记录", ""]
    lines += [f"- {c['date']}：{c['text']}" for c in issue["corrections"]] or ["暂无更正。"]
    lines += ["", "---", "", "本刊由 AI 辅助编写，技术结论请结合原始证据与自己的任务判断。", ""]
    return "\n".join(lines)


def build_outputs(issues, config, readme):
    repo_url = "https://github.com/" + config["repository"]
    source_names = {s["id"]: s["name"] for s in config["sources"]}
    outputs = {f"content/{i['id']}.md": render_issue(i, source_names) for i in issues}
    latest = issues[-1]
    news_count = sum(not e["evergreen"] for e in entries(latest))
    latest_block = (f"<!-- LATEST:START -->\n"
                    f"### [第 {latest['id']} 期｜{latest['title']}](content/{latest['id']}.md)\n\n"
                    f"覆盖 {latest['start']} — {latest['end']} · 发布 {latest['published_on']} · {news_count} 条本周更新\n\n"
                    f"{latest['summary']}\n\n<!-- LATEST:END -->")
    pattern = r"<!-- LATEST:START -->.*?<!-- LATEST:END -->"
    require(len(re.findall(pattern, readme, re.S)) == 1, "README 最新一期标记缺失或重复")
    outputs["README.md"] = re.sub(pattern, lambda _: latest_block, readme, flags=re.S)
    archive = ["# 往期归档", "", "[返回首页](README.md)", "", "| 期号 | 覆盖时间 | 主题 | 发布日期 |", "| --- | --- | --- | --- |"]
    archive += [f"| [{i['id']}](content/{i['id']}.md) | {i['start']} — {i['end']} | {i['title']} | {i['published_on']} |" for i in reversed(issues)]
    outputs["ARCHIVE.md"] = "\n".join(archive) + "\n"
    source_lines = ["# 信息源目录", "", "[返回首页](README.md) · [高 star 项目池](PROJECTS.md) · [编辑准则](docs/EDITORIAL.md)", "",
                    "下面是计划追踪的入口。每期实际检查情况记录在该期 JSON 的 source_checks 中；列入目录不代表每期都能完整访问。优先级 1 每周优先检查，优先级 2 用于补充。", ""]
    for category in dict.fromkeys(s["category"] for s in config["sources"]):
        source_lines += [f"## {category}", "", "| 来源 | 优先级 | 检查方式 |", "| --- | --- | --- |"]
        source_lines += [f"| [{s['name']}]({s['url']}) | {s['priority']} | {s['method']} |" for s in config["sources"] if s["category"] == category]
        source_lines.append("")
    outputs["SOURCES.md"] = "\n".join(source_lines)
    project_lines = ["# 高 star 项目追踪池", "", "[返回首页](README.md) · [信息源目录](SOURCES.md)", "",
                     "项目栏目优先选择 50,000 star 以上的活跃项目，通常不低于 30,000；先有实质技术变化，再决定是否入刊。论文和评测不受 star 门槛约束。", "",
                     "以下数值来自 GitHub REST API 的查询日快照，不是历史周末值。最近推送只能说明仓库有活动，不能独立证明维护质量。合集的 star 不属于其收录的子项目。", ""]
    tracked = [s for s in config["sources"] if "github" in s]
    for collections in (False, True):
        project_lines += ["## 项目发现合集" if collections else "## 重点项目", "", "| 项目 | Star | 查询日期 | 关注方向 | 最近推送（UTC） |", "| --- | ---: | --- | --- | --- |"]
        for source in sorted(tracked, key=lambda s: s["github"]["stars"], reverse=True):
            if (source["category"] == "项目发现合集") != collections:
                continue
            github = source["github"]
            project_lines.append(f"| [{source['name']}](https://github.com/{github['repository']}) | {github['stars']:,} | {github['checked_on']} | {source['focus']} | {github['pushed_at'][:10]} |")
        project_lines.append("")
    project_lines += ["这是观察池，不是能力排名。n8n 等采用 fair-code 或自定义许可的公开项目，应按原仓库许可说明区分；加入名单不代表所有项目使用相同开源许可。", ""]
    outputs["PROJECTS.md"] = "\n".join(project_lines)
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for tag, value in (("title", "Agent & LLM 前沿周报"), ("link", repo_url), ("description", "每周读懂值得跟踪的技术变化：论文、Agent 工程、开源与评测。"), ("language", "zh-CN")):
        ET.SubElement(channel, tag).text = value
    ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link", href=f"https://raw.githubusercontent.com/{config['repository']}/main/feed.xml", rel="self", type="application/rss+xml")
    for issue in reversed(issues):
        item = ET.SubElement(channel, "item")
        link = f"{repo_url}/releases/tag/weekly-{issue['id']}"
        for tag, value in (("title", f"第 {issue['id']} 期｜{issue['title']}"), ("link", link), ("guid", link), ("description", issue["summary"]), ("pubDate", format_datetime(datetime.combine(iso(issue["published_on"]), time(9), TZ)))):
            ET.SubElement(item, tag).text = value
    ET.indent(rss, space="  ")
    outputs["feed.xml"] = ET.tostring(rss, encoding="unicode", xml_declaration=True) + "\n"
    return outputs


def release_notes(issue, config):
    text = render_issue(issue, {s["id"]: s["name"] for s in config["sources"]})
    base = f"https://github.com/{config['repository']}/blob/main/"
    return re.sub(r"\]\(\.\./([^\s)]+)\)", lambda m: "](" + base + m[1] + ")", text)


def next_period(issues, today):
    this_monday = today - timedelta(days=today.weekday())
    start = iso(issues[-1]["end"]) + timedelta(days=1) if issues else this_monday - timedelta(days=7)
    if start >= this_monday:
        return None
    return {"id": f"{len(issues) + 1:03}", "start": start.isoformat(), "end": (start + timedelta(days=6)).isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--next-period", action="store_true")
    mode.add_argument("--release-notes", metavar="ISSUE_ID")
    args = parser.parse_args()
    issues, config = load()
    if args.release_notes:
        selected = [i for i in issues if i["id"] == args.release_notes]
        require(bool(selected), "期号不存在")
        print(release_notes(selected[0], config), end="")
        return
    if args.next_period:
        print(json.dumps(next_period(issues, datetime.now(TZ).date()) or {"status": "up-to-date"}, ensure_ascii=False))
        return
    outputs = build_outputs(issues, config, (ROOT / "README.md").read_text())
    mismatches = []
    for relative, text in outputs.items():
        path = ROOT / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != text:
            mismatches.append(relative)
    expected = {f"{i['id']}.md" for i in issues}
    orphaned = [p.name for p in (ROOT / "content").glob("*.md") if p.name not in expected]
    require(not orphaned, "发现没有数据来源的期刊：" + ", ".join(orphaned))
    require(not mismatches, "生成文件过期，请运行 --write：" + ", ".join(mismatches))
    print(f"{'已生成' if args.write else '检查通过'}：{len(issues)} 期，{len(outputs)} 个文件。外部来源真实性需单独核查。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"错误：{error}", file=sys.stderr)
        sys.exit(1)
