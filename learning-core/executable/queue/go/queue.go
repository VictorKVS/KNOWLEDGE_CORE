package queue

import "errors"

var ErrFull = errors.New("queue capacity reached")

type BoundedQueue struct {
	items    []string
	capacity int
}

func New(capacity int) *BoundedQueue {
	return &BoundedQueue{capacity: capacity}
}

func (q *BoundedQueue) Put(item string) error {
	if len(q.items) >= q.capacity {
		return ErrFull
	}
	q.items = append(q.items, item)
	return nil
}

func (q *BoundedQueue) Get() (string, bool) {
	if len(q.items) == 0 {
		return "", false
	}
	item := q.items[0]
	q.items = q.items[1:]
	return item, true
}

func (q *BoundedQueue) Len() int { return len(q.items) }
