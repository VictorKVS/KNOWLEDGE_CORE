package idempotentmessage

import "errors"

type State struct {
	Processed map[string]bool
	Total     int
}

func NewState() *State {
	return &State{Processed: map[string]bool{}}
}

func Handle(state *State, messageID string, amount int) (bool, error) {
	if messageID == "" {
		return false, errors.New("message id is required")
	}
	if state.Processed[messageID] {
		return false, nil
	}
	state.Total += amount
	state.Processed[messageID] = true
	return true, nil
}
