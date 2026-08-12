package cache

type Repository struct {
	Data  map[string]string
	Reads int
}

func (r *Repository) Get(key string) string {
	r.Reads++
	return r.Data[key]
}

type CacheAside struct {
	Repo  *Repository
	Cache map[string]string
}

func NewCacheAside(repo *Repository) *CacheAside {
	return &CacheAside{Repo: repo, Cache: map[string]string{}}
}

func (c *CacheAside) Get(key string) string {
	if value, ok := c.Cache[key]; ok {
		return value
	}
	value := c.Repo.Get(key)
	c.Cache[key] = value
	return value
}

func (c *CacheAside) Invalidate(key string) {
	delete(c.Cache, key)
}
