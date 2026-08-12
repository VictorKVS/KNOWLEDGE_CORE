package state

import "fmt"

type Status int

const (
	Draft Status = iota
	Approved
	Published
	Archived
)

type Document struct {
	Status Status
}

func Transition(doc Document, target Status) (Document, error) {
	allowed := map[Status]map[Status]bool{
		Draft:     {Approved: true},
		Approved:  {Draft: true, Published: true},
		Published: {Archived: true},
		Archived:  {},
	}
	if !allowed[doc.Status][target] {
		return doc, fmt.Errorf("invalid transition %d -> %d", doc.Status, target)
	}
	doc.Status = target
	return doc, nil
}
