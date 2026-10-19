# Векторный индекс

- **Модель эмбеддингов:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Ссылка:** https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Размерность:** 384
- **База знаний:** `knowledge_base/` (Aether Nexus)
- **Файлы после `build_index.py`:**
  - `faiss.index` — индекс FAISS (Inner Product / cosine при L2-нормализации)
  - `docs.pkl` — чанки + метаданные (source, title, chunk_index)
  - `meta.json` — число чанков, время сборки и параметры

Сборка:

```bash
python scripts/build_index.py
```
