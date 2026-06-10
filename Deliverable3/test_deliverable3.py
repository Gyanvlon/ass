#!/usr/bin/env python3
"""
Deliverable 3 test script.
Validates paging (FIFO/LRU) and synchronization demos.
"""

import sys
from memory_management import PagingMemoryManager
from process_synchronization import MutexCounterDemo, ProducerConsumerDemo


def test_fifo_page_faults() -> bool:
    manager = PagingMemoryManager(total_frames=3, algorithm="fifo")
    manager.register_process(1, 8)

    refs = [0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
    for page in refs:
        manager.access_page(1, page)

    stats = manager.stats()
    # Expected faults for this reference string with FIFO and 3 frames is 9.
    ok = stats["page_faults"] == 9
    print(f"{'PASS' if ok else 'FAIL'}: FIFO page faults expected=9 actual={stats['page_faults']}")
    return ok


def test_lru_page_faults() -> bool:
    manager = PagingMemoryManager(total_frames=3, algorithm="lru")
    manager.register_process(1, 8)

    refs = [0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
    for page in refs:
        manager.access_page(1, page)

    stats = manager.stats()
    # Expected faults for this reference string with LRU and 3 frames is 8.
    ok = stats["page_faults"] == 8
    print(f"{'PASS' if ok else 'FAIL'}: LRU page faults expected=8 actual={stats['page_faults']}")
    return ok


def test_memory_deallocation() -> bool:
    manager = PagingMemoryManager(total_frames=4, algorithm="fifo")
    manager.register_process(1, 4)
    manager.register_process(2, 4)

    manager.access_page(1, 0)
    manager.access_page(1, 1)
    manager.access_page(2, 0)

    freed = manager.deregister_process(1)
    snapshot = manager.frames_snapshot()
    p1_frames = [r for r in snapshot if r.get("pid") == 1]

    ok = freed == 2 and len(p1_frames) == 0
    print(f"{'PASS' if ok else 'FAIL'}: process deallocation freed={freed}, remaining_p1_frames={len(p1_frames)}")
    return ok


def test_mutex_consistency() -> bool:
    result = MutexCounterDemo(thread_count=4, increments_per_thread=2000).run()
    ok = result["consistent"]
    print(
        f"{'PASS' if ok else 'FAIL'}: mutex counter expected={result['expected']} actual={result['actual']}"
    )
    return ok


def test_producer_consumer_integrity() -> bool:
    result = ProducerConsumerDemo(
        producer_count=2,
        consumer_count=3,
        items_per_producer=6,
        buffer_size=4,
    ).run()

    ok = (
        result["produced"] == result["total_items"]
        and result["consumed"] == result["total_items"]
        and result["buffer_final_size"] == 0
        and result["no_loss"]
    )
    print(
        f"{'PASS' if ok else 'FAIL'}: producer-consumer produced={result['produced']} "
        f"consumed={result['consumed']} final_buffer={result['buffer_final_size']}"
    )
    return ok


def main() -> int:
    tests = [
        test_fifo_page_faults,
        test_lru_page_faults,
        test_memory_deallocation,
        test_mutex_consistency,
        test_producer_consumer_integrity,
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as exc:  # Keep output clear for submission evidence.
            print(f"FAIL: {test.__name__} raised exception: {exc}")

    total = len(tests)
    print("-" * 60)
    print(f"Deliverable 3 tests passed: {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
