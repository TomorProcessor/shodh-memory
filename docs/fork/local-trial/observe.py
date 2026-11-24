"""Open a scratch store, optionally write one new memory, and report which seeded texts are still whole.

Usage: python observe.py <store> <originals.json> [--write-one]
Writing a memory is what makes the library look for old memories to shorten.
"""
import collections
import json
import sys
import uuid
from importlib.metadata import version

sys._shodh_star_shown = True  # suppresses the library's start-up banner
from shodh_memory import Memory

store_path, originals_path = sys.argv[1], sys.argv[2]
write_one = "--write-one" in sys.argv[3:]

with open(originals_path, encoding="utf-8") as originals_file:
    originals = json.load(originals_file)

memory = Memory(storage_path=store_path)
if write_one:
    # Unique text: the library returns early on identical content, before it looks for old memories.
    memory.remember(f"A short new note written today, number {uuid.uuid4()}.", memory_type="Context", tags=["local-trial", "trigger"])
    memory.flush()

stored = {record["id"]: record for record in memory.list_memories()}

whole = collections.Counter()
changed = collections.Counter()
missing = collections.Counter()
example_of_change = {}
created_days = collections.defaultdict(set)
for memory_id, original in originals.items():
    group = original["group"]
    record = stored.get(memory_id)
    if record is None:
        missing[group] += 1
        continue
    created_days[group].add(str(record["created_at"])[:10])
    if record["content"] == original["content"]:
        whole[group] += 1
    else:
        changed[group] += 1
        example_of_change.setdefault(group, record)

print("build:", version("shodh-memory"), "| wrote a new memory first:", write_one, "| memories in store:", len(stored))
for group in sorted({original["group"] for original in originals.values()}):
    print(
        f"  group {group:10} created {sorted(created_days[group])} "
        f"whole={whole[group]} changed={changed[group]} missing={missing[group]}"
    )
for group, record in sorted(example_of_change.items()):
    content = record["content"]
    print(f"  example of a changed text in {group}: {len(content.split())} words, compressed={record.get('compressed')}, ends {content[-40:]!r}")
