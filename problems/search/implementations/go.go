// PROB-SEARCH-001: repeated membership lookup.
// Reference variants for evidence-driven comparison.
package searchproblem

import "sort"

func LinearContains(values []int, target int) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func BinaryContains(sortedValues []int, target int) bool {
	index := sort.SearchInts(sortedValues, target)
	return index < len(sortedValues) && sortedValues[index] == target
}

func BuildHashIndex(values []int) map[int]struct{} {
	index := make(map[int]struct{}, len(values))
	for _, value := range values {
		index[value] = struct{}{}
	}
	return index
}

func HashContains(index map[int]struct{}, target int) bool {
	_, ok := index[target]
	return ok
}

func ValidateUnique(values []int) bool {
	seen := make(map[int]struct{}, len(values))
	for _, value := range values {
		if _, exists := seen[value]; exists {
			return false
		}
		seen[value] = struct{}{}
	}
	return true
}
