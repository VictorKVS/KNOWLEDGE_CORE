package transaction

import (
	"errors"
	"testing"
)

func TestTransferUpdatesBothSides(t *testing.T) {
	accounts := map[string]*Account{"a": {Balance: 100}, "b": {Balance: 10}}
	if err := Transfer(accounts, "a", "b", 30); err != nil { t.Fatal(err) }
	if accounts["a"].Balance != 70 || accounts["b"].Balance != 40 {
		t.Fatalf("a=%d b=%d", accounts["a"].Balance, accounts["b"].Balance)
	}
}

func TestFailedTransferPreservesBothSides(t *testing.T) {
	accounts := map[string]*Account{"a": {Balance: 20}, "b": {Balance: 10}}
	err := Transfer(accounts, "a", "b", 30)
	if !errors.Is(err, ErrInsufficientFunds) { t.Fatalf("err=%v", err) }
	if accounts["a"].Balance != 20 || accounts["b"].Balance != 10 {
		t.Fatal("failed transfer changed state")
	}
}
