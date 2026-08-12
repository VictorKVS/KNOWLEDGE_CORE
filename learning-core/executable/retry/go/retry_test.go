package retry

import (
	"errors"
	"testing"
)

func TestTransientFailureRecoversWithinBound(t *testing.T) {
	attempts := 0
	value, err := Call(func() (string, error) {
		attempts++
		if attempts < 3 {
			return "", ErrTransient
		}
		return "ok", nil
	}, 3)
	if err != nil || value != "ok" || attempts != 3 {
		t.Fatalf("value=%q err=%v attempts=%d", value, err, attempts)
	}
}

func TestPermanentFailureIsNotRetried(t *testing.T) {
	attempts := 0
	_, err := Call(func() (string, error) {
		attempts++
		return "", ErrPermanent
	}, 5)
	if !errors.Is(err, ErrPermanent) || attempts != 1 {
		t.Fatalf("err=%v attempts=%d", err, attempts)
	}
}

func TestRetryIsBounded(t *testing.T) {
	attempts := 0
	_, err := Call(func() (string, error) {
		attempts++
		return "", ErrTransient
	}, 3)
	if !errors.Is(err, ErrTransient) || attempts != 3 {
		t.Fatalf("err=%v attempts=%d", err, attempts)
	}
}

func TestIdempotencyPreventsDuplicateSideEffect(t *testing.T) {
	store := NewIdempotentStore()
	if got := store.CreateOnce("request-1", "created"); got != "created" {
		t.Fatal(got)
	}
	if got := store.CreateOnce("request-1", "created"); got != "created" {
		t.Fatal(got)
	}
	if store.SideEffects != 1 {
		t.Fatalf("side effects=%d", store.SideEffects)
	}
}
