package main

import "testing"

func TestMembershipStrategies(t *testing.T) {
    values := []int{1, 3, 5, 7, 9}
    set := map[int]struct{}{1: {}, 3: {}, 5: {}, 7: {}, 9: {}}

    cases := []struct {
        name     string
        target   int
        expected bool
    }{
        {"present", 7, true},
        {"absent", 4, false},
        {"negative absent", -1, false},
    }

    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            if got := linearContains(values, tc.target); got != tc.expected {
                t.Fatalf("linearContains() = %v, want %v", got, tc.expected)
            }
            if got := binaryContains(values, tc.target); got != tc.expected {
                t.Fatalf("binaryContains() = %v, want %v", got, tc.expected)
            }
            if got := hashContains(set, tc.target); got != tc.expected {
                t.Fatalf("hashContains() = %v, want %v", got, tc.expected)
            }
        })
    }
}

func TestEmpty(t *testing.T) {
    if linearContains(nil, 1) || binaryContains(nil, 1) || hashContains(map[int]struct{}{}, 1) {
        t.Fatal("empty collections must not contain target")
    }
}
