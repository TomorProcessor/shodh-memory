# Local trial: does a build shorten old memories?

Upstream builds of the Python library cut a memory older than 7 days to its first 50 words
the next time a new memory is written. The fork's builds must keep it whole. These tools
show the difference in minutes, on scratch stores, by writing test memories with a creation
date in the past.

Never point them at a live store. The clock shift works on macOS only.

## Steps

1. Build the clock shift (the result is gitignored):

   ```sh
   clang -dynamiclib -o clockshift.dylib clockshift.c
   ```

2. Make two Python environments: one with the upstream wheel as the control
   (`shodh-memory==<version>` from PyPI), one with the build under test. Do not use
   `/usr/bin/python3`: macOS ignores `DYLD_INSERT_LIBRARIES` for it and the clock stays real.

3. Seed a scratch store with the control build, with the clock moved back (here 10 days):

   ```sh
   DYLD_INSERT_LIBRARIES=$PWD/clockshift.dylib CLOCK_SHIFT_SECONDS=-864000 \
     <control python> seed.py <store> <originals.json> 10d 10
   ```

   Use one age per store (see `seed.py`).

4. Copy the store twice. Let each build write one new memory into its own copy:

   ```sh
   <control python>    observe.py <copy 1> <originals.json> --write-one
   <build under test>  observe.py <copy 2> <originals.json> --write-one
   ```

## Expected

For memories seeded more than 7 days back:

- control: `whole=0 changed=10`, each text cut to 50 words ending `...`
- a no-compression build: `whole=10 changed=0`

A control that does not shorten means the trial is not working; the result of the build under
test then proves nothing.

## The scripts

- `clockshift.c` shifts the clock of one process by `CLOCK_SHIFT_SECONDS`.
- `seed.py` writes long test memories and records their full text.
- `observe.py` reports which seeded texts are still whole, after optionally writing a memory.
- `../trial-check.py` compares a copied store with a `wt-memory` export of the same store. It
  needs no clock shift and runs on any platform.
