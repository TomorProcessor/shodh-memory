"""Open a COPY of a store with the installed shodh-memory and compare it with a wt-memory export.

Usage: python trial-check.py <copied store folder> <export.json of the same store>
Never point this at a live store.
"""
import json
import sys
from importlib.metadata import version

sys._shodh_star_shown = True  # suppresses the library's start-up banner
from shodh_memory import Memory

store_copy_path, export_path = sys.argv[1], sys.argv[2]

with open(export_path, encoding="utf-8") as export_file:
    exported = {record["id"]: record["content"] for record in json.load(export_file)["records"]}
opened = {record["id"]: record["content"] for record in Memory(storage_path=store_copy_path).list_memories()}

missing = exported.keys() - opened.keys()
extra = opened.keys() - exported.keys()
differing = sorted(i for i in exported.keys() & opened.keys() if exported[i] != opened[i])

print("installed build:", version("shodh-memory"))
print("memories in export:", len(exported), "| in the copy opened by this build:", len(opened))
print("missing in copy:", len(missing), "| extra in copy:", len(extra), "| text differs:", len(differing))
for memory_id in differing[:5]:
    print("  differs:", memory_id, "| export ends:", repr(exported[memory_id][-30:]), "| copy ends:", repr(opened[memory_id][-30:]))

passed = len(opened) > 0 and not missing and not extra and not differing
print("RESULT:", "PASS" if passed else "FAIL")
sys.exit(0 if passed else 1)
