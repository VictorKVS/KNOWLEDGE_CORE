package idempotentmessage

import "testing"

func TestDuplicateDoesNotRepeatSideEffect(t *testing.T) {
	state := NewState()
	applied, err := Handle(state, "m1", 10)
	if err != nil || !applied {
		t.Fatalf("first delivery failed: applied=%v err=%v", applied, err)
	}
	applied, err = Handle(state, "m1", 10)
	if err != nil || applied {
		t.Fatalf("duplicate delivery was applied: applied=%v err=%v", applied, err)
	}
	if state.Total != 10 {
		t.Fatalf("total=%d", state.Total)
	}
}

func TestDistinctMessagesApply(t *testing.T) {
	state := NewState()
	_, _ = Handle(state, "m1", 10)
	_, _ = Handle(state, "m2", 5)
	if state.Total != 15 {
		t.Fatalf("total=%d", state.Total)
	}
}
