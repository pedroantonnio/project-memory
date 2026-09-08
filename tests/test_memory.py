import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "memory.py"
spec = importlib.util.spec_from_file_location("project_memory_helper", MODULE_PATH)
mem = importlib.util.module_from_spec(spec)
assert spec.loader is not None
import sys
sys.modules[spec.name] = mem
spec.loader.exec_module(mem)


class ProjectMemoryTests(unittest.TestCase):
    def test_init_and_validate_empty_store(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            mem.ensure_structure(repo)
            errors, warnings = mem.validate(repo)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertTrue((repo / ".agents" / "MEMORY" / "SUMMARY.md").exists())

    def test_create_record_validates(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            args = argparse.Namespace(
                repo=str(repo),
                type="feature",
                slug="finances",
                title="Finances",
                status="active",
                scope=["finances", "forecast"],
                filename=None,
            )
            mem.command_create(args)
            errors, _warnings = mem.validate(repo)
            self.assertEqual(errors, [])
            self.assertTrue((repo / ".agents" / "MEMORY" / "records" / "features" / "finances.md").exists())

    def test_duplicate_ids_fail_validation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            mem.ensure_structure(repo)
            body = """---\nid: duplicate\ntype: feature\nstatus: active\ncreated: 2026-09-08\nupdated: 2026-09-08\nscope:\n  - test\n---\n\n# Test\n"""
            a = repo / ".agents" / "MEMORY" / "records" / "features" / "a.md"
            b = repo / ".agents" / "MEMORY" / "records" / "features" / "b.md"
            a.write_text(body, encoding="utf-8")
            b.write_text(body, encoding="utf-8")
            errors, _ = mem.validate(repo)
            self.assertTrue(any("Duplicate record id" in x for x in errors))

    def test_broken_summary_link_fails_validation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            mem.ensure_structure(repo)
            summary = repo / ".agents" / "MEMORY" / "SUMMARY.md"
            summary.write_text("# Project Memory Summary\n\n[Missing](records/features/missing.md)\n", encoding="utf-8")
            errors, _ = mem.validate(repo)
            self.assertTrue(any("Broken SUMMARY.md link" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
