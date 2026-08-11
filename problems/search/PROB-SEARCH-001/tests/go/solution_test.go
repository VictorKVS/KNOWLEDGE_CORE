package searchproblem

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
            if got := LinearContains(values, tc.target); got != tc.expected {
                t.Fatalf("LinearContains() = %v, want %v", got, tc.expected)
            }
            if got := BinaryContains(values, tc.target); got != tc.expected {
                t.Fatalf("BinaryContains() = %v, want %v", got, tc.expected)
            }
            if got := HashContains(set, tc.target); got != tc.expected {
                t.Fatalf("HashContains() = %v, want %v", got, tc.expected)
            }
        })
    }
}

func TestEmpty(t *testing.T) {
    if LinearContains(nil, 1) || BinaryContains(nil, 1) || HashContains(map[int]struct{}{}, 1) {
        t.Fatal("empty collections must not contain target")
    }
}
