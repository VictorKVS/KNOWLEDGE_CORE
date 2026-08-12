package validation

import "testing"

func TestParseRegistrationValid(t *testing.T) {
	got, err := ParseRegistration("  Ada  ", 36)
	if err != nil {
		t.Fatal(err)
	}
	if got.Username != "Ada" || got.Age != 36 {
		t.Fatalf("unexpected result: %+v", got)
	}
}

func TestParseRegistrationRejectsInvalid(t *testing.T) {
	cases := []struct {
		name string
		age  int
	}{
		{"", 36},
		{"Ada", -1},
		{"Ada", 131},
	}
	for _, tc := range cases {
		if _, err := ParseRegistration(tc.name, tc.age); err == nil {
			t.Fatalf("expected error for name=%q age=%d", tc.name, tc.age)
		}
	}
}
