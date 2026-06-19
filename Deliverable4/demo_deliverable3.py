#!/usr/bin/env python3
"""
Deliverable 3 demonstration runner.
Produces concise output that can be used for screenshots in the report.
"""

from memory_management import PagingMemoryManager
from process_synchronization import MutexCounterDemo, ProducerConsumerDemo


def memory_demo() -> None:
    print("=" * 70)
    print("DELIVERABLE 3 DEMO: MEMORY MANAGEMENT (PAGING + REPLACEMENT)")
    print("=" * 70)

    refs = [0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]

    for algorithm in ("fifo", "lru"):
        manager = PagingMemoryManager(total_frames=3, algorithm=algorithm)
        manager.register_process(10, 8)

        print(f"\nAlgorithm: {algorithm.upper()} | Frames: 3")
        print(f"Reference string: {refs}")
        for page in refs:
            result = manager.access_page(10, page)
            replaced = result["replaced"]
            if replaced:
                detail = f"replaced pid={replaced['pid']} page={replaced['page_number']}"
            else:
                detail = "no replacement"
            print(f"  access {page:>2} -> {result['result'].upper():<5} | frame {result['frame_id']} | {detail}")

        stats = manager.stats()
        print(
            f"Summary: faults={stats['page_faults']}, hits={stats['page_hits']}, "
            f"replacements={stats['replacements']}, fault_rate={stats['fault_rate']:.2f}%"
        )


def synchronization_demo() -> None:
    print("\n" + "=" * 70)
    print("DELIVERABLE 3 DEMO: PROCESS SYNCHRONIZATION")
    print("=" * 70)

    mutex_result = MutexCounterDemo(thread_count=4, increments_per_thread=1500).run()
    print("\nMutex Demo:")
    print(f"  Expected counter: {mutex_result['expected']}")
    print(f"  Actual counter:   {mutex_result['actual']}")
    print(f"  Race prevented:   {'YES' if mutex_result['consistent'] else 'NO'}")

    pc_result = ProducerConsumerDemo(
        producer_count=2,
        consumer_count=2,
        items_per_producer=5,
        buffer_size=3,
    ).run()

    print("\nProducer-Consumer Demo:")
    print(f"  Produced:         {pc_result['produced']}")
    print(f"  Consumed:         {pc_result['consumed']}")
    print(f"  Final buffer:     {pc_result['buffer_final_size']}")
    print(f"  Max occupancy:    {pc_result['max_buffer_observed']}")
    print(f"  Integrity check:  {'PASS' if pc_result['no_loss'] else 'FAIL'}")

    print("\nSample synchronization events:")
    for event in pc_result["events"][:12]:
        print(f"  [{event.actor:<12}] {event.action:<8} {event.detail}")


def main() -> None:
    memory_demo()
    synchronization_demo()


if __name__ == "__main__":
    main()
