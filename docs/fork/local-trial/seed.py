"""Write long test memories into a scratch store and record their full text.

Usage: python seed.py <store> <originals.json> <group label> <count>
The creation time of the memories is the process clock (shift it with clockshift.dylib).

One age per store: an upstream build shortens old memories whenever a new one is written,
so seeding a younger group into a store that holds an older one cuts the older one.
"""
import json
import os
import sys

sys._shodh_star_shown = True  # suppresses the library's start-up banner
from shodh_memory import Memory

store_path, originals_path, group, count = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

WORDS = (
    "pipeline deploy cache index branch review latency retry token schema migrate backup "
    "worker queue timeout cluster volume proxy socket header payload session tenant ledger "
    "invoice report filter export import widget layout render module adapter gateway broker"
).split()


def long_text(group_label, number):
    """About 130 distinct-looking words, so shortening to 50 words is unmistakable."""
    body = " ".join(f"{WORDS[(number * 7 + position * 3) % len(WORDS)]}{position}" for position in range(130))
    return f"Test note {group_label}-{number}: {body} END-OF-NOTE-{group_label}-{number}"


originals = {}
if os.path.exists(originals_path):
    with open(originals_path, encoding="utf-8") as originals_file:
        originals = json.load(originals_file)

memory = Memory(storage_path=store_path)
for number in range(count):
    content = long_text(group, number)
    memory_id = memory.remember(content, memory_type="Context", tags=["local-trial", group])
    originals[memory_id] = {"group": group, "content": content}
memory.flush()

with open(originals_path, "w", encoding="utf-8") as originals_file:
    json.dump(originals, originals_file)
print(f"seeded {count} memories in group {group!r}; originals recorded: {len(originals)}")
