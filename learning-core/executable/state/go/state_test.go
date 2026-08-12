package state

import "testing"

func TestLifecycle(t *testing.T) {
	doc := Document{Status: Draft}
	var err error
	for _, target := range []Status{Approved, Published, Archived} {
		doc, err = Transition(doc, target)
		if err != nil {
			t.Fatal(err)
		}
	}
	if doc.Status != Archived {
		t.Fatalf("status=%v", doc.Status)
	}
}

func TestInvalidTransitionPreservesState(t *testing.T) {
	original := Document{Status: Draft}
	got, err := Transition(original, Published)
	if err == nil {
		t.Fatal("expected error")
	}
	if got.Status != Draft || original.Status != Draft {
		t.Fatal("invalid transition changed state")
	}
}
