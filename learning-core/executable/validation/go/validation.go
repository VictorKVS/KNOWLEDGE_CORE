package validation

import (
	"errors"
	"strings"
)

type Registration struct {
	Username string
	Age      int
}

func ParseRegistration(username string, age int) (Registration, error) {
	username = strings.TrimSpace(username)
	if len(username) < 1 || len(username) > 64 {
		return Registration{}, errors.New("username length must be 1..64")
	}
	if age < 0 || age > 130 {
		return Registration{}, errors.New("age must be in range 0..130")
	}
	return Registration{Username: username, Age: age}, nil
}
