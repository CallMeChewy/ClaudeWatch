# File: reader.py
# Path: /home/herb/Desktop/ClaudeWatch/src/claude_monitor/data/reader.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-26
# Last Modified: 2025-07-26 04:24AM

"""Simplified data reader for Claude Monitor.

Combines functionality from file_reader, filter, mapper, and processor
into a single cohesive module.
"""

import json
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from claude_monitor.core.data_processors import (
    DataConverter,
    TimestampProcessor,
    TokenExtractor,
)
from claude_monitor.core.models import CostMode, UsageEntry
from claude_monitor.core.pricing import PricingCalculator
from claude_monitor.data.enhanced_database import EnhancedDatabaseManager as DatabaseManager
from claude_monitor.error_handling import report_file_error
from claude_monitor.utils.time_utils import TimezoneHandler

FIELD_COST_USD = "cost_usd"
FIELD_MODEL = "model"
TOKEN_INPUT = "input_tokens"
TOKEN_OUTPUT = "output_tokens"

logger = logging.getLogger(__name__)


def load_usage_entries(
    data_path: Optional[str] = None,
    hours_back: Optional[int] = None,
    mode: CostMode = CostMode.AUTO,
    include_raw: bool = False,
) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
    """Load and convert usage data to UsageEntry objects.

    This function now reads from the database and performs a one-time
    migration from JSONL files if the database is empty.

    Args:
        data_path: Path to Claude data directory (for migration)
        hours_back: Only include entries from last N hours
        mode: Cost calculation mode (used during migration)
        include_raw: Whether to return raw JSON data alongside entries

    Returns:
        Tuple of (usage_entries, raw_data)
    """
    db_manager = DatabaseManager()
    
    # One-time migration if database is empty
    if not db_manager.get_all_usage_entries():
        _migrate_jsonl_to_db(db_manager, data_path, mode)

    all_db_entries = db_manager.get_all_usage_entries()
    
    # Filtering by hours_back
    if hours_back:
        cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)
        all_db_entries = [
            e for e in all_db_entries 
            if datetime.fromisoformat(e['timestamp']).replace(tzinfo=tz.utc) >= cutoff_time
        ]

    # Convert to UsageEntry objects
    usage_entries = [_dict_to_usage_entry(e) for e in all_db_entries]
    
    raw_data = all_db_entries if include_raw else None

    logger.info(f"Loaded {len(usage_entries)} entries from the database.")
    
    return usage_entries, raw_data


def load_all_raw_entries(data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load all raw JSONL entries without processing.

    Args:
        data_path: Path to Claude data directory

    Returns:
        List of raw JSON dictionaries
    """
    resolved_path = Path(data_path if data_path else "~/.claude/projects").expanduser()
    jsonl_files = _find_jsonl_files(resolved_path)

    all_raw_entries: List[Dict[str, Any]] = []
    for file_path in jsonl_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        all_raw_entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.exception(f"Error loading raw entries from {file_path}: {e}")

    return all_raw_entries


def _find_jsonl_files(data_path: Path) -> List[Path]:
    """Find all .jsonl files in the data directory."""
    if not data_path.exists():
        logger.warning("Data path does not exist: %s", data_path)
        return []
    return list(data_path.rglob("*.jsonl"))


def _process_single_file(
    file_path: Path,
    mode: CostMode,
    cutoff_time: Optional[datetime],
    processed_hashes: Set[str],
    include_raw: bool,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
    """Process a single JSONL file."""
    entries: List[UsageEntry] = []
    raw_data: Optional[List[Dict[str, Any]]] = [] if include_raw else None

    try:
        entries_read = 0
        entries_filtered = 0
        entries_mapped = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    entries_read += 1

                    if not _should_process_entry(
                        data, cutoff_time, processed_hashes, timezone_handler
                    ):
                        entries_filtered += 1
                        continue

                    entry = _map_to_usage_entry(
                        data, mode, timezone_handler, pricing_calculator
                    )
                    if entry:
                        entries_mapped += 1
                        entries.append(entry)
                        _update_processed_hashes(data, processed_hashes)

                    if include_raw and raw_data is not None:
                        raw_data.append(data)

                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON line in {file_path}: {e}")
                    continue

        logger.debug(
            f"File {file_path.name}: {entries_read} read, "
            f"{entries_filtered} filtered out, {entries_mapped} successfully mapped"
        )

    except Exception as e:
        logger.warning("Failed to read file %s: %s", file_path, e)
        report_file_error(
            exception=e,
            file_path=str(file_path),
            operation="read",
            additional_context={"file_exists": file_path.exists()},
        )
        return [], None

    return entries, raw_data


def _should_process_entry(
    data: Dict[str, Any],
    cutoff_time: Optional[datetime],
    processed_hashes: Set[str],
    timezone_handler: TimezoneHandler,
) -> bool:
    """Check if entry should be processed based on time and uniqueness."""
    if cutoff_time:
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            processor = TimestampProcessor(timezone_handler)
            timestamp = processor.parse_timestamp(timestamp_str)
            if timestamp and timestamp < cutoff_time:
                return False

    unique_hash = _create_unique_hash(data)
    return not (unique_hash and unique_hash in processed_hashes)


def _create_unique_hash(data: Dict[str, Any]) -> Optional[str]:
    """Create unique hash for deduplication."""
    message_id = data.get("message_id") or (
        data.get("message", {}).get("id")
        if isinstance(data.get("message"), dict)
        else None
    )
    request_id = data.get("requestId") or data.get("request_id")

    return f"{message_id}:{request_id}" if message_id and request_id else None


def _update_processed_hashes(data: Dict[str, Any], processed_hashes: Set[str]) -> None:
    """Update the processed hashes set with current entry's hash."""
    unique_hash = _create_unique_hash(data)
    if unique_hash:
        processed_hashes.add(unique_hash)


def _migrate_jsonl_to_db(
    db_manager: DatabaseManager, data_path: Optional[str], mode: CostMode
) -> None:
    """Migrate data from JSONL files to the database."""
    logger.info("Performing one-time migration from JSONL files to database.")
    resolved_path = Path(data_path if data_path else "~/.claude/projects").expanduser()
    jsonl_files = _find_jsonl_files(resolved_path)

    if not jsonl_files:
        logger.warning("No JSONL files found for migration.")
        return

    timezone_handler = TimezoneHandler()
    pricing_calculator = PricingCalculator()
    processed_hashes: Set[str] = set()

    for file_path in jsonl_files:
        entries, _ = _process_single_file(
            file_path,
            mode,
            None,  # No cutoff time for migration
            processed_hashes,
            False, # No raw data needed
            timezone_handler,
            pricing_calculator,
        )
        for entry in entries:
            db_manager.add_usage_entry(entry.__dict__)
    
    logger.info(f"Migration complete. Added entries to the database.")


def _dict_to_usage_entry(data: Dict[str, Any]) -> UsageEntry:
    """Convert a dictionary from the database to a UsageEntry object."""
    return UsageEntry(
        timestamp=datetime.fromisoformat(data['timestamp']),
        input_tokens=data['input_tokens'],
        output_tokens=data['output_tokens'],
        cache_creation_tokens=data.get('cache_creation_tokens', 0),
        cache_read_tokens=data.get('cache_read_tokens', 0),
        cost_usd=data['cost_usd'],
        model=data['model'],
        message_id=data['message_id'],
        request_id=data['request_id'],
    )


def _map_to_usage_entry(
    data: Dict[str, Any],
    mode: CostMode,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> Optional[UsageEntry]:
    """Map raw data to UsageEntry with proper cost calculation."""
    try:
        timestamp_processor = TimestampProcessor(timezone_handler)
        timestamp = timestamp_processor.parse_timestamp(data.get("timestamp", ""))
        if not timestamp:
            return None

        token_data = TokenExtractor.extract_tokens(data)
        if not any(v for k, v in token_data.items() if k != "total_tokens"):
            return None

        model = DataConverter.extract_model_name(data, default="unknown")

        entry_data: Dict[str, Any] = {
            FIELD_MODEL: model,
            TOKEN_INPUT: token_data["input_tokens"],
            TOKEN_OUTPUT: token_data["output_tokens"],
            "cache_creation_tokens": token_data.get("cache_creation_tokens", 0),
            "cache_read_tokens": token_data.get("cache_read_tokens", 0),
            FIELD_COST_USD: data.get("cost") or data.get(FIELD_COST_USD),
        }
        cost_usd = pricing_calculator.calculate_cost_for_entry(entry_data, mode)

        message = data.get("message", {})
        message_id = data.get("message_id") or message.get("id") or ""
        request_id = data.get("request_id") or data.get("requestId") or "unknown"

        return UsageEntry(
            timestamp=timestamp,
            input_tokens=token_data["input_tokens"],
            output_tokens=token_data["output_tokens"],
            cache_creation_tokens=token_data.get("cache_creation_tokens", 0),
            cache_read_tokens=token_data.get("cache_read_tokens", 0),
            cost_usd=cost_usd,
            model=model,
            message_id=message_id,
            request_id=request_id,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Failed to map entry: {type(e).__name__}: {e}")
        return None


class UsageEntryMapper:
    """Compatibility wrapper for legacy UsageEntryMapper interface.

    This class provides backward compatibility for tests that expect
    the old UsageEntryMapper interface, wrapping the new functional
    approach in _map_to_usage_entry.
    """

    def __init__(
        self, pricing_calculator: PricingCalculator, timezone_handler: TimezoneHandler
    ):
        """Initialize with required components."""
        self.pricing_calculator = pricing_calculator
        self.timezone_handler = timezone_handler

    def map(self, data: Dict[str, Any], mode: CostMode) -> Optional[UsageEntry]:
        """Map raw data to UsageEntry - compatibility interface."""
        return _map_to_usage_entry(
            data, mode, self.timezone_handler, self.pricing_calculator
        )

    def _has_valid_tokens(self, tokens: Dict[str, int]) -> bool:
        """Check if tokens are valid (for test compatibility)."""
        return any(v > 0 for v in tokens.values())

    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp (for test compatibility)."""
        if "timestamp" not in data:
            return None
        processor = TimestampProcessor(self.timezone_handler)
        return processor.parse_timestamp(data["timestamp"])

    def _extract_model(self, data: Dict[str, Any]) -> str:
        """Extract model name (for test compatibility)."""
        return DataConverter.extract_model_name(data, default="unknown")

    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract metadata (for test compatibility)."""
        message = data.get("message", {})
        return {
            "message_id": data.get("message_id") or message.get("id", ""),
            "request_id": data.get("request_id") or data.get("requestId", "unknown"),
        }
