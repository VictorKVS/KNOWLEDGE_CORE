package cache

import "testing"

func TestMissThenHit(t *testing.T) {
	repo := &Repository{Data: map[string]string{"user:1": "Ada"}}
	cached := NewCacheAside(repo)
	if cached.Get("user:1") != "Ada" || cached.Get("user:1") != "Ada" {
		t.Fatal("unexpected value")
	}
	if repo.Reads != 1 {
		t.Fatalf("reads=%d", repo.Reads)
	}
}

func TestInvalidationRevealsSourceChange(t *testing.T) {
	repo := &Repository{Data: map[string]string{"user:1": "Ada"}}
	cached := NewCacheAside(repo)
	_ = cached.Get("user:1")
	repo.Data["user:1"] = "Grace"
	if cached.Get("user:1") != "Ada" {
		t.Fatal("expected stale cached value before invalidation")
	}
	cached.Invalidate("user:1")
	if cached.Get("user:1") != "Grace" {
		t.Fatal("expected refreshed source value")
	}
}
