package retry

import "errors"

var (
	ErrTransient = errors.New("transient failure")
	ErrPermanent = errors.New("permanent failure")
)

func Call(operation func() (string, error), maxAttempts int) (string, error) {
	if maxAttempts < 1 {
		return "", errors.New("maxAttempts must be >= 1")
	}
	var lastErr error
	for i := 0; i < maxAttempts; i++ {
		value, err := operation()
		if err == nil {
			return value, nil
		}
		if errors.Is(err, ErrPermanent) {
			return "", err
		}
		if !errors.Is(err, ErrTransient) {
			return "", err
		}
		lastErr = err
	}
	return "", lastErr
}

type IdempotentStore struct {
	results     map[string]string
	SideEffects int
}

func NewIdempotentStore() *IdempotentStore {
	return &IdempotentStore{results: map[string]string{}}
}

func (s *IdempotentStore) CreateOnce(key, value string) string {
	if existing, ok := s.results[key]; ok {
		return existing
	}
	s.SideEffects++
	s.results[key] = value
	return value
}
