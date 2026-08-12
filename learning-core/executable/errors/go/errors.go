package errorsample

import "errors"

var (
	ErrAccountNotFound   = errors.New("account not found")
	ErrInsufficientFunds = errors.New("insufficient funds")
	ErrInvalidAmount     = errors.New("amount must be positive")
)

type Account struct {
	Balance int
}

func Withdraw(accounts map[string]*Account, accountID string, amount int) (int, error) {
	if amount <= 0 {
		return 0, ErrInvalidAmount
	}
	account, ok := accounts[accountID]
	if !ok {
		return 0, ErrAccountNotFound
	}
	if account.Balance < amount {
		return account.Balance, ErrInsufficientFunds
	}
	account.Balance -= amount
	return account.Balance, nil
}
