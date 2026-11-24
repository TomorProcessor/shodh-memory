/* Shifts the wall clock of one process by CLOCK_SHIFT_SECONDS, so test records can be
   written with a creation time in the past. macOS only.

   Build: clang -dynamiclib -o clockshift.dylib clockshift.c
   Use:   DYLD_INSERT_LIBRARIES=/path/to/clockshift.dylib CLOCK_SHIFT_SECONDS=-864000 <command> */
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>

#define INTERPOSE(replacement, original) \
    __attribute__((used)) static struct { const void *new_fn; const void *old_fn; } \
    interpose_##original __attribute__((section("__DATA,__interpose"))) = { \
        (const void *)(unsigned long)&replacement, (const void *)(unsigned long)&original };

static long shift_seconds(void) {
    const char *value = getenv("CLOCK_SHIFT_SECONDS");
    return value ? atol(value) : 0;
}

int shifted_clock_gettime(clockid_t clock_id, struct timespec *ts) {
    int rc = clock_gettime(clock_id, ts);
    if (rc == 0 && clock_id == CLOCK_REALTIME) ts->tv_sec += shift_seconds();
    return rc;
}
INTERPOSE(shifted_clock_gettime, clock_gettime)

int shifted_gettimeofday(struct timeval *tv, void *tz) {
    int rc = gettimeofday(tv, tz);
    if (rc == 0 && tv) tv->tv_sec += shift_seconds();
    return rc;
}
INTERPOSE(shifted_gettimeofday, gettimeofday)
