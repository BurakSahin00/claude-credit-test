# claude-credit-test
## toc.py — Markdown içindekiler tablosu

Bir Markdown dosyasındaki `#`, `##` ve `###` başlıklarından iç içe bir içindekiler tablosu üretir.
Kod blokları (``` veya ~~~) içindeki `#` satırları başlık sayılmaz.

```
python toc.py dosya.md
```

Örnek — `dosya.md`:

```markdown
# Proje
## Kurulum
### Gereksinimler
## Kullanım
```

Çıktı:

```
- [Proje](#proje)
  - [Kurulum](#kurulum)
    - [Gereksinimler](#gereksinimler)
  - [Kullanım](#kullanım)
```

Testler: `pytest`
