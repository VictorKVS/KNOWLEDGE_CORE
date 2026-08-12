package dbtx

import "errors"

var (
	ErrNotFound          = errors.New("account not found")
	ErrInsufficientFunds = errors.New("insufficient funds")
)

type Store struct {
	Balances map[string]int
}

type Tx struct {
	working map[string]int
}

func (s *Store) Begin() *Tx {
	copyMap := make(map[string]int, len(s.Balances))
	for k, v := range s.Balances {
		copyMap[k] = v
	}
	return &Tx{working: copyMap}
}

func (tx *Tx) Transfer(source, target string, amount int) error {
	if amount <= 0 {
		return errors.New("amount must be positive")
	}
	src, ok := tx.working[source]
	if !ok {
		return ErrNotFound
	}
	if _, ok := tx.working[target]; !ok {
		return ErrNotFound
	}
	if src < amount {
		return ErrInsufficientFunds
	}
	tx.working[source] -= amount
	tx.working[target] += amount
	return nil
}

func (s *Store) Commit(tx *Tx) { s.Balances = tx.working }
