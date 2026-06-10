#!/usr/bin/env python3
"""
Process synchronization module for Deliverable 3.
Includes mutex-based shared resource protection and Producer-Consumer simulation.
"""

import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Deque, List


@dataclass
class SyncEvent:
    timestamp: float
    actor: str
    action: str
    detail: str


class MutexCounterDemo:
    """Demonstrates race-free shared counter updates using a mutex."""

    def __init__(self, thread_count: int = 4, increments_per_thread: int = 1000):
        self.thread_count = thread_count
        self.increments_per_thread = increments_per_thread
        self.counter = 0
        self.lock = threading.Lock()
        self.events: List[SyncEvent] = []

    def run(self) -> dict:
        threads: List[threading.Thread] = []

        def worker(tid: int) -> None:
            actor = f"T{tid}"
            for step in range(self.increments_per_thread):
                with self.lock:
                    self.counter += 1
                    if step == 0:
                        self.events.append(
                            SyncEvent(time.time(), actor, "lock-acquire", "entered critical section")
                        )
            self.events.append(SyncEvent(time.time(), actor, "done", "finished increments"))

        for i in range(self.thread_count):
            t = threading.Thread(target=worker, args=(i + 1,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        expected = self.thread_count * self.increments_per_thread
        return {
            "expected": expected,
            "actual": self.counter,
            "consistent": expected == self.counter,
            "events": self.events,
        }


class ProducerConsumerDemo:
    """Classical bounded-buffer producer-consumer with semaphores."""

    def __init__(
        self,
        producer_count: int = 2,
        consumer_count: int = 2,
        items_per_producer: int = 5,
        buffer_size: int = 4,
        delay: float = 0.005,
    ):
        if producer_count <= 0 or consumer_count <= 0:
            raise ValueError("producer_count and consumer_count must be > 0")
        if items_per_producer <= 0 or buffer_size <= 0:
            raise ValueError("items_per_producer and buffer_size must be > 0")

        self.producer_count = producer_count
        self.consumer_count = consumer_count
        self.items_per_producer = items_per_producer
        self.buffer_size = buffer_size
        self.delay = delay

        self.buffer: Deque[str] = deque()
        self.empty = threading.Semaphore(buffer_size)
        self.full = threading.Semaphore(0)
        self.mutex = threading.Lock()

        self.events: List[SyncEvent] = []
        self.produced_items: List[str] = []
        self.consumed_items: List[str] = []
        self.max_buffer_observed = 0

    def run(self) -> dict:
        total_items = self.producer_count * self.items_per_producer
        consumers_goal = self._split_work(total_items, self.consumer_count)

        threads: List[threading.Thread] = []

        def producer(pid: int) -> None:
            for i in range(self.items_per_producer):
                item = f"P{pid}-item{i}"
                self.empty.acquire()
                with self.mutex:
                    self.buffer.append(item)
                    self.produced_items.append(item)
                    self.max_buffer_observed = max(self.max_buffer_observed, len(self.buffer))
                    self.events.append(
                        SyncEvent(time.time(), f"Producer-{pid}", "produce", f"{item} -> buffer={len(self.buffer)}")
                    )
                self.full.release()
                time.sleep(self.delay)

            self.events.append(SyncEvent(time.time(), f"Producer-{pid}", "done", "completed production"))

        def consumer(cid: int, consume_count: int) -> None:
            for _ in range(consume_count):
                self.full.acquire()
                with self.mutex:
                    item = self.buffer.popleft()
                    self.consumed_items.append(item)
                    self.events.append(
                        SyncEvent(time.time(), f"Consumer-{cid}", "consume", f"{item} <- buffer={len(self.buffer)}")
                    )
                self.empty.release()
                time.sleep(self.delay)

            self.events.append(SyncEvent(time.time(), f"Consumer-{cid}", "done", "completed consumption"))

        for i in range(self.producer_count):
            t = threading.Thread(target=producer, args=(i + 1,))
            threads.append(t)
            t.start()

        for i in range(self.consumer_count):
            t = threading.Thread(target=consumer, args=(i + 1, consumers_goal[i]))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return {
            "total_items": total_items,
            "produced": len(self.produced_items),
            "consumed": len(self.consumed_items),
            "buffer_final_size": len(self.buffer),
            "max_buffer_observed": self.max_buffer_observed,
            "no_loss": sorted(self.produced_items) == sorted(self.consumed_items),
            "events": self.events,
        }

    @staticmethod
    def _split_work(total: int, workers: int) -> List[int]:
        base = total // workers
        remainder = total % workers
        out = [base for _ in range(workers)]
        for i in range(remainder):
            out[i] += 1
        return out
