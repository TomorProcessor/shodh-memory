//! The config the Python library opens its store with: old memories keep
//! their full text.

use std::path::PathBuf;

use chrono::{Duration, Utc};

use shodh_memory::memory::{MemoryConfig, NO_COMPRESSION_AGE_DAYS};

#[test]
fn without_compression_switches_auto_compress_off() {
    let config = MemoryConfig::without_compression(PathBuf::from("./store"));

    assert!(!config.auto_compress);
}

#[test]
fn without_compression_puts_the_age_threshold_out_of_reach() {
    // Promotion to long-term compresses a memory older than this many days
    // even when auto_compress is off.
    let config = MemoryConfig::without_compression(PathBuf::from("./store"));
    let oldest_plausible_memory_days = 50 * 365;

    assert!(config.compression_age_days > oldest_plausible_memory_days);
}

#[test]
fn without_compression_keeps_the_given_storage_path_and_other_defaults() {
    let defaults = MemoryConfig::default();

    let config = MemoryConfig::without_compression(PathBuf::from("./store"));

    assert_eq!(config.storage_path, PathBuf::from("./store"));
    assert_eq!(config.working_memory_size, defaults.working_memory_size);
    assert_eq!(config.importance_threshold, defaults.importance_threshold);
}

#[test]
fn the_age_threshold_is_a_date_the_engine_can_compute() {
    // compress_old_memories() subtracts the threshold from the current time.
    let cutoff = Utc::now().checked_sub_signed(Duration::days(NO_COMPRESSION_AGE_DAYS as i64));

    assert!(cutoff.is_some());
}
