package dbtx

import "testing"

func TestCommitAndRollbackByOmission(t *testing.T) {
	store := &Store{Balances: map[string]int{"a": 100, "b": 50}}
	tx := store.Begin()
	if err := tx.Transfer("a", "b", 30); err != nil {
		t.Fatal(err)
	}
	store.Commit(tx)
	if store.Balances["a"] != 70 || store.Balances["b"] != 80 {
		t.Fatal("commit failed")
	}

	beforeA, beforeB := store.Balances["a"], store.Balances["b"]
	tx = store.Begin()
	if err := tx.Transfer("a", "missing", 10); err == nil {
		t.Fatal("expected error")
	}
	// no Commit: original store remains unchanged
	if store.Balances["a"] != beforeA || store.Balances["b"] != beforeB {
		t.Fatal("failed transaction leaked partial state")
	}
}
