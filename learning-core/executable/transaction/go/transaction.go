package transaction

import "errors"

var ErrInsufficientFunds = errors.New("insufficient funds")

type Account struct {
	Balance int
}

func Transfer(accounts map[string]*Account, source, target string, amount int) error {
	if amount <= 0 {
		return errors.New("amount must be positive")
	}
	src := accounts[source]
	dst := accounts[target]
	if src.Balance < amount {
		return ErrInsufficientFunds
	}
	// Commit boundary: validate first, then apply both mutations.
	src.Balance -= amount
	dst.Balance += amount
	return nil
}
