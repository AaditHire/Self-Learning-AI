"""Frozen Phase 3C-CONF1 Coverage-v3 evidence machinery.

This package is non-model infrastructure.  Importing it performs no file I/O,
compiler execution, fixture evaluation, model loading, inference, or training.
"""

from .interfaces import (
    ClosureError,
    SchemaError,
    artifact_reference,
    ordered_row_id_digest,
    rid,
    validate_artifact_reference,
    validate_expected_row_index,
    validate_record_reference,
)
from .binder import GATES, bind_gate_trace, final_bind
from .contracts import CoverageContractV3, all_contracts
from .goco import parse, source_occurrence_inventory

__all__ = [
    "ClosureError",
    "SchemaError",
    "artifact_reference",
    "ordered_row_id_digest",
    "rid",
    "validate_artifact_reference",
    "validate_expected_row_index",
    "validate_record_reference",
    "GATES",
    "CoverageContractV3",
    "all_contracts",
    "bind_gate_trace",
    "final_bind",
    "parse",
    "source_occurrence_inventory",
]
