import copy
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts/build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class EditorialSafeguards(unittest.TestCase):
    def setUp(self):
        self.issue = json.loads((ROOT / "data/issues/001.json").read_text())
        self.config = json.loads((ROOT / "data/sources.json").read_text())
        fixture_source_ids = {c["id"] for c in self.issue["source_checks"]}
        self.config["sources"] = [s for s in self.config["sources"] if s["id"] in fixture_source_ids]
        self.today = max(date.fromisoformat(self.issue["published_on"]),
                         *(date.fromisoformat(c["date"]) for c in self.issue["corrections"]))

    def check(self, issues=None):
        build.validate(issues or [self.issue], self.config, self.today)

    def test_old_news_cannot_be_reported_as_this_week(self):
        self.issue["sections"][1]["entries"][0]["date"] = "2026-10-01"
        with self.assertRaisesRegex(ValueError, "新闻日期"):
            self.check()

    def test_recent_research_need_not_be_from_news_week(self):
        self.issue["sections"][0]["entries"][0]["date"] = "2026-10-21"
        self.check()

    def test_research_cannot_leak_past_coverage_cutoff(self):
        self.issue["sections"][0]["entries"][0]["date"] = "2026-11-09"
        with self.assertRaisesRegex(ValueError, "研究日期"):
            self.check()

    def test_old_research_is_rejected(self):
        self.issue["sections"][0]["entries"][0]["date"] = "2026-07-01"
        with self.assertRaisesRegex(ValueError, "研究日期"):
            self.check()

    def test_venue_claim_requires_evidence(self):
        self.issue["sections"][0]["entries"][1]["publication"].pop("evidence_url")
        with self.assertRaisesRegex(ValueError, "发表状态证据"):
            self.check()

    def test_discovery_snapshot_is_not_a_news_event(self):
        project = self.issue["sections"][2]["entries"][0]
        self.assertEqual(project["date"], "2026-11-12")
        self.check()
        project["selection"] = "update"
        with self.assertRaisesRegex(ValueError, "项目更新日期"):
            self.check()

    def test_small_projects_are_eligible(self):
        self.issue["sections"][2]["entries"][0]["github"]["stars"] = 20
        self.check()

    def test_empty_section_requires_explanation(self):
        section = self.issue["sections"][1]
        section["entries"] = []
        with self.assertRaisesRegex(ValueError, "空栏目"):
            self.check()

    def test_broken_highlight_is_rejected(self):
        self.issue["highlights"][0]["entry_id"] = "does-not-exist"
        with self.assertRaisesRegex(ValueError, "导读指向"):
            self.check()

    def test_future_publication_is_rejected(self):
        self.issue["published_on"] = (self.today + timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "发布日期"):
            self.check()

    def test_unfinished_week_is_rejected(self):
        self.issue["start"], self.issue["end"] = "2026-11-09", "2026-11-15"
        with self.assertRaisesRegex(ValueError, "覆盖周尚未结束"):
            self.check()

    def test_missing_primary_source_is_rejected(self):
        self.issue["sections"][0]["entries"][0]["links"] = []
        with self.assertRaisesRegex(ValueError, "缺少原始来源"):
            self.check()

    def test_missing_coverage_is_rejected(self):
        self.issue["source_checks"].pop()
        with self.assertRaisesRegex(ValueError, "每个配置来源"):
            self.check()

    def test_reproduction_claim_requires_evidence(self):
        self.issue["sections"][0]["entries"][0]["verification"]["level"] = "reproduced"
        with self.assertRaisesRegex(ValueError, "复现条件"):
            self.check()

    def test_overlapping_weeks_are_rejected(self):
        second = copy.deepcopy(self.issue)
        second["id"] = "002"
        with self.assertRaisesRegex(ValueError, "重复或缺失"):
            self.check([self.issue, second])

    def test_missed_runs_resume_from_first_missing_week(self):
        pending = build.next_period([self.issue], date(2026, 12, 7))
        self.assertEqual(pending, {"id": "002", "start": "2026-11-09", "end": "2026-11-15"})

    def test_current_week_is_not_published_early(self):
        self.assertIsNone(build.next_period([self.issue], date(2026, 11, 15)))
        self.assertEqual(build.next_period([self.issue], date(2026, 11, 16))["end"], "2026-11-15")

    def test_outputs_are_idempotent_and_rss_is_valid(self):
        self.check()
        readme = (ROOT / "README.md").read_text()
        first = build.build_outputs([self.issue], self.config, readme)
        second = build.build_outputs([self.issue], self.config, first["README.md"])
        self.assertEqual(first, second)
        rss = ET.fromstring(first["feed.xml"])
        self.assertEqual(rss.find("./channel/item/guid").text,
                         "https://github.com/735034777/agent-llm-weekly/releases/tag/weekly-001")

    def test_release_notes_use_absolute_repository_links(self):
        notes = build.release_notes(self.issue, self.config)
        self.assertNotIn("](../", notes)
        self.assertIn("https://github.com/735034777/agent-llm-weekly/blob/main/README.md", notes)
        self.assertIn("](#section-research)", notes)
        self.assertIn("/blob/main/evidence/001.md", notes)


if __name__ == "__main__":
    unittest.main()
