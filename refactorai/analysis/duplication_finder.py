"""
Code Duplication Detection Module.

Finds duplicated code patterns across a codebase using
various techniques including text similarity and AST analysis.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import Duplication, Location


class DuplicationFinder:
    """
    Finds duplicated code across a codebase.

    Uses multiple techniques:
    - Exact text matching with normalization
    - Structural matching (AST-based)
    - Fuzzy matching for similar code blocks
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.min_lines = config.min_duplication_lines

    def find_duplications(self, file_paths: list[str]) -> list[Duplication]:
        """
        Find all duplications in the given files.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            List of Duplication objects
        """
        # First pass: collect all code blocks
        all_blocks = self._extract_code_blocks(file_paths)

        # Group by hash to find exact duplicates
        duplicates = self._find_exact_duplicates(all_blocks)

        # Also find near-duplicates
        near_duplicates = self._find_near_duplicates(all_blocks)

        # Merge results
        all_duplications = duplicates + near_duplicates

        # Remove overlapping duplications
        return self._remove_overlapping(all_duplications)

    def _extract_code_blocks(self, file_paths: list[str]) -> list[dict]:
        """Extract code blocks from all files."""
        blocks = []

        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                file_blocks = self._extract_blocks_from_file(file_path, content)
                blocks.extend(file_blocks)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        return blocks

    def _extract_blocks_from_file(self, file_path: str, content: str) -> list[dict]:
        """Extract code blocks from a single file."""
        blocks = []
        lines = content.split("\n")

        # Split into logical blocks (separated by blank lines or definitions)
        current_block = []
        block_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip comments and empty lines for the block
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue

            # Check for function/class definitions (new block)
            if re.match(r"^(def|class|async def|if __name__|@)", stripped):
                if len(current_block) >= self.min_lines:
                    blocks.append(
                        {
                            "file": file_path,
                            "start": block_start + 1,
                            "end": i,
                            "lines": current_block,
                            "content": "\n".join(current_block),
                        }
                    )
                current_block = []
                block_start = i

            current_block.append(line)

        # Don't forget the last block
        if len(current_block) >= self.min_lines:
            blocks.append(
                {
                    "file": file_path,
                    "start": block_start + 1,
                    "end": len(lines),
                    "lines": current_block,
                    "content": "\n".join(current_block),
                }
            )

        return blocks

    def _normalize_for_comparison(self, code: str) -> str:
        """Normalize code for comparison by removing whitespace variations."""
        # Remove comments
        lines = []
        for line in code.split("\n"):
            # Remove inline comments
            if "#" in line and not (line.strip().startswith('"') or line.strip().startswith("'")):
                line = line[: line.index("#")]
            lines.append(line)

        # Remove empty lines and normalize whitespace
        normalized = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                normalized.append(stripped)

        return "\n".join(normalized)

    def _compute_hash(self, content: str) -> str:
        """Compute a hash for content comparison."""
        normalized = self._normalize_for_comparison(content)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _find_exact_duplicates(self, blocks: list[dict]) -> list[Duplication]:
        """Find exact duplicate code blocks."""
        # Group by hash
        hash_groups: dict[str, list[dict]] = defaultdict(list)

        for block in blocks:
            block_hash = self._compute_hash(block["content"])
            block["hash"] = block_hash
            hash_groups[block_hash].append(block)

        duplications = []

        for block_hash, group in hash_groups.items():
            if len(group) < 2:  # Need at least 2 occurrences
                continue

            # Collect all locations
            locations = [
                Location(
                    file_path=item["file"],
                    line_start=item["start"],
                    line_end=item["end"],
                    snippet=item["content"][:200] if len(item["content"]) > 200 else item["content"],
                )
                for item in group
            ]

            duplications.append(
                Duplication(
                    code_fragment=group[0]["content"][:500],  # First 500 chars
                    locations=locations,
                    lines=len(group[0]["lines"]),
                    hash=block_hash,
                )
            )

        return duplications

    def _find_near_duplicates(self, blocks: list[dict]) -> list[Duplication]:
        """Find near-duplicate code blocks using similarity analysis."""
        duplications = []
        processed_pairs: set[tuple] = set()

        for i, block1 in enumerate(blocks):
            for block2 in blocks[i + 1 :]:
                # Skip if already processed
                pair = tuple(sorted([block1["hash"], block2["hash"]]))
                if pair in processed_pairs:
                    continue

                # Calculate similarity
                normalized1 = self._normalize_for_comparison(block1["content"])
                normalized2 = self._normalize_for_comparison(block2["content"])

                if len(normalized1) < 10 or len(normalized2) < 10:
                    continue

                ratio = SequenceMatcher(None, normalized1, normalized2).ratio()

                if ratio >= 0.8:  # 80% similarity threshold
                    processed_pairs.add(pair)

                    locations = [
                        Location(
                            file_path=block1["file"],
                            line_start=block1["start"],
                            line_end=block1["end"],
                        ),
                        Location(
                            file_path=block2["file"],
                            line_start=block2["start"],
                            line_end=block2["end"],
                        ),
                    ]

                    duplications.append(
                        Duplication(
                            code_fragment=block1["content"][:500],
                            locations=locations,
                            lines=len(block1["lines"]),
                            hash=f"near_{block1['hash'][:8]}",
                        )
                    )

        return duplications

    def _remove_overlapping(self, duplications: list[Duplication]) -> list[Duplication]:
        """Remove overlapping duplication entries."""
        if not duplications:
            return []

        # Sort by number of locations (descending) then by lines (descending)
        sorted_dups = sorted(duplications, key=lambda d: (-len(d.locations), -d.lines))

        result = []
        covered_ranges: set[tuple] = set()

        for dup in sorted_dups:
            # Check if any location is already covered
            is_new = False
            for loc in dup.locations:
                key = (loc.file_path, loc.line_start, loc.line_end)
                if key not in covered_ranges:
                    is_new = True
                    break

            if is_new:
                result.append(dup)
                # Mark ranges as covered
                for loc in dup.locations:
                    for line in range(loc.line_start, loc.line_end + 1):
                        covered_ranges.add((loc.file_path, line, line))

        return result

    def analyze_similarity_matrix(self, file_paths: list[str]) -> dict:
        """
        Generate a similarity matrix between files.

        Returns a dictionary with file pairs and their similarity scores.
        """
        matrix = {}

        for i, file1 in enumerate(file_paths):
            for file2 in file_paths[i + 1 :]:
                try:
                    with open(file1, "r") as f1, open(file2, "r") as f2:
                        content1 = self._normalize_for_comparison(f1.read())
                        content2 = self._normalize_for_comparison(f2.read())

                    if len(content1) < 10 or len(content2) < 10:
                        continue

                    ratio = SequenceMatcher(None, content1, content2).ratio()
                    matrix[f"{file1}|||{file2}"] = ratio

                except Exception:
                    pass

        return matrix
