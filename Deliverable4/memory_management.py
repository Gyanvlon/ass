#!/usr/bin/env python3
"""
Memory management module for Deliverable 3.
Implements paging with FIFO and LRU page replacement.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class PageReplacementAlgorithm(Enum):
    FIFO = "fifo"
    LRU = "lru"


@dataclass
class PageFrame:
    frame_id: int
    pid: int
    page_number: int
    loaded_at: int
    last_accessed: int


class PagingMemoryManager:
    """Simulates fixed-size frame memory with page replacement."""

    def __init__(self, total_frames: int = 8, algorithm: str = "fifo"):
        if total_frames <= 0:
            raise ValueError("total_frames must be > 0")

        algo = algorithm.lower()
        if algo not in (PageReplacementAlgorithm.FIFO.value, PageReplacementAlgorithm.LRU.value):
            raise ValueError("algorithm must be 'fifo' or 'lru'")

        self.total_frames = total_frames
        self.algorithm = algo

        self.frames: List[Optional[PageFrame]] = [None for _ in range(total_frames)]
        self.process_page_limits: Dict[int, int] = {}

        self.page_faults = 0
        self.page_hits = 0
        self.replacements = 0
        self._clock = 0

    def register_process(self, pid: int, total_pages: int) -> None:
        if total_pages <= 0:
            raise ValueError("total_pages must be > 0")
        self.process_page_limits[pid] = total_pages

    def deregister_process(self, pid: int) -> int:
        """Remove all pages for a process and return freed frame count."""
        freed = 0
        for i, frame in enumerate(self.frames):
            if frame is not None and frame.pid == pid:
                self.frames[i] = None
                freed += 1

        if pid in self.process_page_limits:
            del self.process_page_limits[pid]

        return freed

    def access_page(self, pid: int, page_number: int) -> Dict[str, object]:
        """Access a virtual page; may trigger page fault and replacement."""
        self._clock += 1

        if pid not in self.process_page_limits:
            raise ValueError(f"process {pid} is not registered")

        max_pages = self.process_page_limits[pid]
        if page_number < 0 or page_number >= max_pages:
            raise ValueError(f"invalid page {page_number} for process {pid}; valid range: 0..{max_pages - 1}")

        hit_idx = self._find_loaded_page(pid, page_number)
        if hit_idx is not None:
            frame = self.frames[hit_idx]
            if frame is not None:
                frame.last_accessed = self._clock
            self.page_hits += 1
            return {
                "result": "hit",
                "frame_id": hit_idx,
                "replaced": None,
                "page_faults": self.page_faults,
            }

        # Page fault
        self.page_faults += 1

        free_idx = self._find_free_frame()
        replaced = None

        if free_idx is None:
            victim_idx = self._select_victim_frame()
            victim = self.frames[victim_idx]
            replaced = {
                "pid": victim.pid,
                "page_number": victim.page_number,
                "frame_id": victim_idx,
            }
            free_idx = victim_idx
            self.replacements += 1

        self.frames[free_idx] = PageFrame(
            frame_id=free_idx,
            pid=pid,
            page_number=page_number,
            loaded_at=self._clock,
            last_accessed=self._clock,
        )

        return {
            "result": "fault",
            "frame_id": free_idx,
            "replaced": replaced,
            "page_faults": self.page_faults,
        }

    def memory_usage_by_process(self) -> Dict[int, int]:
        usage: Dict[int, int] = {}
        for frame in self.frames:
            if frame is None:
                continue
            usage[frame.pid] = usage.get(frame.pid, 0) + 1
        return usage

    def stats(self) -> Dict[str, object]:
        used_frames = sum(1 for frame in self.frames if frame is not None)
        total_accesses = self.page_faults + self.page_hits
        fault_rate = (self.page_faults / total_accesses * 100.0) if total_accesses > 0 else 0.0

        return {
            "total_frames": self.total_frames,
            "used_frames": used_frames,
            "free_frames": self.total_frames - used_frames,
            "algorithm": self.algorithm,
            "page_faults": self.page_faults,
            "page_hits": self.page_hits,
            "replacements": self.replacements,
            "fault_rate": fault_rate,
            "usage_by_process": self.memory_usage_by_process(),
        }

    def frames_snapshot(self) -> List[Dict[str, object]]:
        snap: List[Dict[str, object]] = []
        for i, frame in enumerate(self.frames):
            if frame is None:
                snap.append({"frame_id": i, "state": "free"})
            else:
                snap.append(
                    {
                        "frame_id": i,
                        "state": "used",
                        "pid": frame.pid,
                        "page_number": frame.page_number,
                        "loaded_at": frame.loaded_at,
                        "last_accessed": frame.last_accessed,
                    }
                )
        return snap

    def _find_loaded_page(self, pid: int, page_number: int) -> Optional[int]:
        for idx, frame in enumerate(self.frames):
            if frame is not None and frame.pid == pid and frame.page_number == page_number:
                return idx
        return None

    def _find_free_frame(self) -> Optional[int]:
        for idx, frame in enumerate(self.frames):
            if frame is None:
                return idx
        return None

    def _select_victim_frame(self) -> int:
        candidates: List[Tuple[int, int]] = []
        for idx, frame in enumerate(self.frames):
            if frame is None:
                continue

            if self.algorithm == PageReplacementAlgorithm.FIFO.value:
                score = frame.loaded_at
            else:
                score = frame.last_accessed

            candidates.append((score, idx))

        if not candidates:
            raise RuntimeError("no victim frame available")

        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]
