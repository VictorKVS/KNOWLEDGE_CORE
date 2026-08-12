package errorsample

import (
	"errors"
	"testing"
)

func TestWithdraw(t *testing.T) {
	accounts := map[string]*Account{"a": {Balance: 100}}
	balance, err := Withdraw(accounts, "a", 30)
	if err != nil || balance != 70 {
		t.Fatalf("balance=%d err=%v", balance, err)
	}
}

func TestWithdrawErrorsPreserveState(t *testing.T) {
	accounts := map[string]*Account{"a": {Balance: 20}}
	_, err := Withdraw(accounts, "a", 30)
	if !errors.Is(err, ErrInsufficientFunds) {
		t.Fatalf("unexpected error: %v", err)
	}
	if accounts["a"].Balance != 20 {
		t.Fatal("failed operation changed state")
	}

	if _, err := Withdraw(accounts, "missing", 1); !errors.Is(err, ErrAccountNotFound) {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err := Withdraw(accounts, "a", 0); !errors.Is(err, ErrInvalidAmount) {
		t.Fatalf("unexpected error: %v", err)
	}
}
