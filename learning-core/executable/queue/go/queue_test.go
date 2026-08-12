package queue

import (
	"errors"
	"testing"
)

func TestFIFOAndCapacity(t *testing.T) {
	q := New(2)
	if err := q.Put("a"); err != nil { t.Fatal(err) }
	if err := q.Put("b"); err != nil { t.Fatal(err) }
	if got, ok := q.Get(); !ok || got != "a" { t.Fatalf("got=%q ok=%v", got, ok) }
	if got, ok := q.Get(); !ok || got != "b" { t.Fatalf("got=%q ok=%v", got, ok) }
}

func TestBackpressureRejectsGrowth(t *testing.T) {
	q := New(1)
	_ = q.Put("a")
	if err := q.Put("b"); !errors.Is(err, ErrFull) { t.Fatalf("err=%v", err) }
	if q.Len() != 1 { t.Fatalf("len=%d", q.Len()) }
}
