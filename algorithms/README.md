# Algorithms

Algorithms are stored as engineering choices, not isolated textbook recipes.

Each algorithm record should answer:

- What problem does it solve?
- Under which constraints is it valid?
- What are the alternatives?
- What are the asymptotic and measured costs?
- What failure modes exist?
- What security implications matter?
- Which sources support the claims?
- Which implementation is preferred in Python, Go and C++ for the current context?

## Initial map

| ID | Topic | Typical alternatives |
|---|---|---|
| ALG-SEARCH-001 | Search | linear, binary, hash-based, tree-based |
| ALG-SORT-001 | Sorting | insertion, merge, quick, heap, language-native |
| DS-HASH-001 | Hash tables | tree, sorted vector, trie, direct addressing |
| DS-QUEUE-001 | Queue / stack | deque, ring buffer, linked structure |
| ALG-GRAPH-001 | Graph traversal | BFS, DFS |
| ALG-GRAPH-004 | Shortest path | BFS, Dijkstra, Bellman-Ford, A* |

## Selection rule

Do not select an algorithm because it is famous, fashionable or asymptotically attractive in isolation. Select it from the workload, constraints, data shape, failure model, security requirements and measured behaviour.

← [Engineering Knowledge](../README.md)
