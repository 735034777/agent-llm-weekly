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
KINDS = {"research": "论文与研究", "news": "新闻动态", "projects": "开源项目"}
PUBLICATIONS = {"journal": "期刊论文", "conference": "会议论文", "preprint": "预印本", "blog": "研究博客", "report": "技术报告"}


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
        require(issue.get("schema_version") == 2, f"{issue_id}: 需要 schema_version 2")
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
        require([s.get("kind") for s in issue["sections"]] == list(KINDS), "栏目必须依次为研究、新闻、项目")
        for section in issue["sections"]:
            kind = section["kind"]
            require(section["title"] == KINDS[kind], "栏目名称不匹配")
            require(section["entries"] or section.get("empty_note", "").strip(), "空栏目须注明证据缺口")
            for entry in section["entries"]:
                key = entry["id"]
                require(key not in entry_ids, f"{issue_id}: 条目 ID 重复：{key}")
                entry_ids.add(key)
                for field in ("title", "summary", "date_label"):
                    require(bool(entry.get(field, "").strip()), f"{key}: 缺少 {field}")
                event_date = iso(entry["date"])
                require(event_date <= today, f"{key}: 事件日期不能在未来")
                if kind == "news":
                    require(start <= event_date <= end, f"{key}: 新闻日期不在覆盖周内")
                    require(key not in news_ids, f"重复报道同一新闻事件：{key}")
                    news_ids.add(key)
                    require(entry.get("date_basis", "").strip(), f"{key}: 缺少新闻日期依据")
                elif kind == "research":
                    require(end - timedelta(days=60) <= event_date <= end, f"{key}: 研究日期超出近 60 天或晚于覆盖周")
                    pub = entry["publication"]
                    require(pub["type"] in PUBLICATIONS and pub["venue"].strip(), f"{key}: 研究发表状态错误")
                    if pub["type"] in {"journal", "conference"}:
                        require(pub.get("status") in {"published", "accepted"}, f"{key}: 缺少正式发表或录用状态")
                        require(public_url(pub.get("evidence_url", "")), f"{key}: 缺少发表状态证据")
                    require(entry.get("insight", "").strip() and entry.get("limits", "").strip(), f"{key}: 研究须包含阅读判断与证据边界")
                else:
                    require(entry.get("selection") in {"discovery", "update"}, f"{key}: 项目选题类型错误")
                    if entry["selection"] == "update":
                        require(start <= event_date <= end, f"{key}: 项目更新日期不在覆盖周内")
                    else:
                        require(event_date <= published, f"{key}: 项目发现日期晚于本期发布")
                    require(entry.get("getting_started", "").strip() and entry.get("license", "").strip(), f"{key}: 项目缺少上手入口或许可")
                    require("github" in entry, f"{key}: 项目缺少 GitHub 快照")
                require(bool(entry["links"]), f"{key}: 缺少原始来源")
                for link in entry["links"]:
                    require(link["label"].strip() and public_url(link["url"]), f"{key}: 来源链接错误")
                verification = entry["verification"]
                if "github" in entry:
                    validate_github(entry["github"], today)
                require(verification["level"] in {"source-reviewed", "source-partial", "reproduced"}, f"{key}: 核查等级错误")
                require(verification.get("scope", "").strip(), f"{key}: 缺少实际核查范围")
                checked = iso(verification["checked_on"])
                require(checked <= today and (event_date is None or checked >= event_date), f"{key}: 核查日期错误")
                if verification["level"] == "reproduced":
                    require(bool(verification.get("reproduction")), f"{key}: 缺少复现条件和结果记录")
        highlights = issue["highlights"]
        require(len(highlights) == min(3, len(entry_ids)), f"{issue_id}: 导读应有三条")
        require(len({h["entry_id"] for h in highlights}) == len(highlights), "导读重复")
        require(all(h["entry_id"] in entry_ids and h["text"].strip() for h in highlights), f"{issue_id}: 导读指向不存在的条目")
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


def entry_label(entry, kind):
    if kind == "research":
        pub = entry["publication"]
        status = {"published": "已发表", "accepted": "已录用"}.get(pub.get("status"), "")
        return " · ".join(filter(None, [PUBLICATIONS[pub["type"]], pub["venue"], status, entry["date_label"] + " " + entry["date"]]))
    return entry["date_label"] + " " + entry["date"]


def render_issue(issue, source_names=None):
    issue_id = issue["id"]
    lines = [f"# AI 周刊 · 第 {issue_id} 期", "", f"## {issue['title']}", "",
             f"> 新闻周：{issue['start']} — {issue['end']}｜发布：{issue['published_on']}｜排期：北京时间", "",
             "[首页](../README.md) · [往期](../ARCHIVE.md) · [信息源](../SOURCES.md)", "", issue["summary"], "",
             "**先看这三条**", ""]
    lines += [f"- [{h['text']}](#item-{h['entry_id']})" for h in issue["highlights"]]
    lines += ["", " · ".join(f"[{s['title']}](#section-{s['kind']})" for s in issue["sections"]), ""]
    count = 0
    for section in issue["sections"]:
        kind = section["kind"]
        lines += [f'<a id="section-{kind}"></a>', "", f"## {section['title']}", ""]
        if section.get("intro"):
            lines += [section["intro"], ""]
        if not section["entries"]:
            lines += [section["empty_note"], ""]
        for entry in section["entries"]:
            count += 1
            lines += [f'<a id="item-{entry["id"]}"></a>', "", f"### {count}. {entry['title']}", "",
                      f"`{entry_label(entry, kind)}` · " + " / ".join(entry["tags"]), ""]
            if kind == "projects":
                g = entry["github"]
                lines += [f"⭐ {g['stars']:,}（{g['checked_on']} 快照） · {entry['license']}", ""]
            lines += [entry["summary"], ""]
            if kind == "research":
                lines += [entry["insight"], "", entry["limits"], ""]
            elif kind == "projects":
                lines += ["**上手：** " + entry["getting_started"], ""]
                if entry.get("requirements"):
                    lines += [entry["requirements"], ""]
            elif entry.get("context"):
                lines += [entry["context"], ""]
            lines += [" · ".join(f"[{link['label']}]({link['url']})" for link in entry["links"]), ""]
    lines += ["---", "",
              f"本期核查与复现情况按条记录；未注明复现的条目均未独立复现实验或安装测试。详细核查范围与访问缺口见 [核查记录](../evidence/{issue_id}.md)；结构化内容见 [本期数据](../data/issues/{issue_id}.json)。", "",
              "<details>", "<summary>版本与更正</summary>", ""]
    lines += [f"- {c['date']}：{c['text']}" for c in issue["corrections"]] or ["暂无更正。"]
    lines += ["", "</details>", "", "本刊由 AI 辅助编写，观点与摘要请结合原始来源阅读。", ""]
    return "\n".join(lines)


def render_evidence(issue, source_names):
    counts = Counter(c["status"] for c in issue["source_checks"])
    lines = [f"# 第 {issue['id']} 期核查记录", "", f"[返回正文](../content/{issue['id']}.md)", "",
             f"来源目录 {len(issue['source_checks'])} 个：完成注明范围检查 {counts['reviewed']} 个，部分检查 {counts['partial']} 个，访问失败 {counts['unavailable']} 个，未检查 {counts['not_checked']} 个。目录是候选入口，不能据此声称穷尽全网。", "",
             "## 条目证据", ""]
    for section in issue["sections"]:
        for e in section["entries"]:
            v = e["verification"]
            lines += [f"### {e['title']}", "", f"{v['checked_on']} · `{v['level']}`", "", v["scope"], ""]
            if e.get("date_basis"):
                lines += ["日期依据：" + e["date_basis"], ""]
            if e.get("github"):
                g = e["github"]
                lines += [f"仓库：{g['repository']}；star {g['stars']:,}；查询日 {g['checked_on']}。", ""]
            if v.get("reproduction"):
                lines += ["复现记录：" + v["reproduction"], ""]
            lines += [" · ".join(f"[{l['label']}]({l['url']})" for l in e["links"]), ""]
    names = {"reviewed": "完成注明范围", "partial": "部分检查", "unavailable": "访问失败", "not_checked": "未检查"}
    lines += ["## 来源覆盖", "", "| 来源 | 状态 | 日期 | 实际范围 |", "| --- | --- | --- | --- |"]
    lines += [f"| {source_names.get(c['id'], c['id'])} | {names[c['status']]} | {c['checked_on']} | {c['note'].replace('|', '／')} |" for c in issue["source_checks"]]
    return "\n".join(lines) + "\n"


def build_outputs(issues, config, readme):
    repo_url = "https://github.com/" + config["repository"]
    source_names = {s["id"]: s["name"] for s in config["sources"]}
    outputs = {f"content/{i['id']}.md": render_issue(i, source_names) for i in issues}
    outputs.update({f"evidence/{i['id']}.md": render_evidence(i, source_names) for i in issues})
    latest = issues[-1]
    units = {"research": ("研究", "篇"), "news": ("新闻", "条"), "projects": ("项目", "个")}
    counts = " · ".join(f"{units[s['kind']][0]} {len(s['entries'])} {units[s['kind']][1]}" for s in latest["sections"])
    latest_block = (f"<!-- LATEST:START -->\n"
                    f"### [第 {latest['id']} 期｜{latest['title']}](content/{latest['id']}.md)\n\n"
                    f"新闻周 {latest['start']} — {latest['end']} · 发布 {latest['published_on']}\n\n"
                    f"{counts}\n\n{latest['summary']}\n\n<!-- LATEST:END -->")
    pattern = r"<!-- LATEST:START -->.*?<!-- LATEST:END -->"
    require(len(re.findall(pattern, readme, re.S)) == 1, "README 最新一期标记缺失或重复")
    outputs["README.md"] = re.sub(pattern, lambda _: latest_block, readme, flags=re.S)
    archive = ["# 往期归档", "", "[返回首页](README.md)", "", "| 期号 | 新闻周 | 主题 | 发布日期 |", "| --- | --- | --- | --- |"]
    archive += [f"| [{i['id']}](content/{i['id']}.md) | {i['start']} — {i['end']} | {i['title']} | {i['published_on']} |" for i in reversed(issues)]
    outputs["ARCHIVE.md"] = "\n".join(archive) + "\n"
    source_lines = ["# 信息源目录", "", "[首页](README.md) · [项目索引](PROJECTS.md) · [编辑准则](docs/EDITORIAL.md)", "",
                    "优先级 1 为常规选题入口，2 为补充线索。每期按实际访问记录核查范围；列入目录不代表每周全部读完。聚合、社区和人物账号提供线索，入刊事实须追溯原始材料或可靠报道。", ""]
    for category in dict.fromkeys(s["category"] for s in config["sources"]):
        source_lines += [f"## {category}", "", "| 来源 | 优先级 | 检查方式 |", "| --- | --- | --- |"]
        source_lines += [f"| [{s['name']}]({s['url']}) | {s['priority']} | {s['method']} |" for s in config["sources"] if s["category"] == category]
        source_lines.append("")
    outputs["SOURCES.md"] = "\n".join(source_lines)
    project_lines = ["# 开源项目索引", "", "[首页](README.md) · [信息源](SOURCES.md)", "",
                     "按入刊顺序收录，方便回看。以用途、特色、文档、可用性和维护情况选稿；star 是查询日的关注度快照，不设硬门槛，也不是能力排名。发现条目不代表项目本周首次发布。", "",
                     "| 项目 | 方向 | Star 快照 | 查询日期 | 许可 | 入选期刊 |", "| --- | --- | ---: | --- | --- | --- |"]
    for issue in reversed(issues):
        for section in issue["sections"]:
            if section["kind"] != "projects":
                continue
            for e in section["entries"]:
                g = e["github"]
                project_lines.append(f"| [{g['repository']}](https://github.com/{g['repository']}) | {' / '.join(e['tags'])} | {g['stars']:,} | {g['checked_on']} | {e['license']} | [{issue['id']}](content/{issue['id']}.md#item-{e['id']}) |")
    project_lines += ["", "代码许可不自动覆盖模型权重、训练数据或素材；具体条件见项目条目和原仓库。", ""]
    outputs["PROJECTS.md"] = "\n".join(project_lines)
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for tag, value in (("title", "AI 周刊"), ("link", repo_url), ("description", "论文与研究、新闻动态、开源项目。每周精选值得读、值得聊、值得试的 AI 进展。"), ("language", "zh-CN")):
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
