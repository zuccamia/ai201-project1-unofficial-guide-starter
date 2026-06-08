# Generation & Interface

## Architecture (stage 5)

```
+----------------------------------------------------------------------------+
| 5 · GENERATION                                                             |
|----------------------------------------------------------------------------|
|                                                                            |
|   Tier-aware prompt                                                        |
|     authoritative > advisory > peer                                        |
|     + "as of {date}" framing                                               |
|     + "not legal advice -> confirm with your DSO"                          |
|                          |                                                 |
|                          v                                                 |
|   LLM:  Groq (Llama / Mixtral)                                             |
|                          |                                                 |
|                          v                                                 |
|   Answer + citations  (provenance pulled from breadcrumb metadata)         |
+----------------------------------------------------------------------------+
```

---

## Milestone 5 — Generation and interface
