# 32: run the task-22 population models on the GPU when it is free

From: cloud session, 16 November 2026, about 10:40. In the queue Justin approved at 10:09 ("Go ahead with the queue").
Low priority.

Task 22's per-cell-store runs used torch on the CPU (about an hour each). When task 26's GPU work is finished, try the
same runs on the GPU and report the speedup and whether results match the CPU runs (same seeds). Keep the CPU path.
Queue position: after tasks 26–29 and 31's designs.
