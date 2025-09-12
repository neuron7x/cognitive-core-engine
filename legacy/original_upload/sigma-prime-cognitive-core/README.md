# Σ'-Prime Cognitive Core

**Коротко:** відкритий науково-інженерний фреймворк для **вимірюваного, етичного моделювання персональної когнітивної динаміки** (без спекулятивного терміна “свідомість”).

- 🔬 **Метрики:** Σ'(t) з компонентами Φ, Ψ, Ε, Τ — операціоналізовані, відтворювані.
- 🧱 **Архітектура:** модульний дизайн, дані/етика/аудит як first-class citizens.
- ✅ **Валідація:** ULTRASIM (in-silico → benchmark → inversion → analog → peer).
- 🧩 **Ціль:** збереження та аналіз **когнітивного стану** особи, дослідницька платформа та базис для персональних агентів.

> Репозиторій містить оригінальні джерела у `docs/raw/` (див. `manifests/` з SHA256), протоколи, етичні норми й CI для перевірки цілісності.


## Швидкий старт
1. Клонуйте репозиторій та ознайомтесь із протоколом у `PROJECT_PROTOCOL.md`.
2. Перегляньте `ULTRASIM.md` для запуску валідаційного циклу.
3. Перевірте цілісність файлів:  
   ```bash
   sha256sum -c manifests/CHECKSUMS_raw_docs.txt
   ```

## Структура
```
.
├─ docs/
│  ├─ raw/                # НЕОБРОБЛЕНІ оригінальні матеріали (як надані)
│  └─ README.md
├─ ethics/
│  ├─ ETHICS.md           # Етичні принципи, consent, прозорість
│  └─ PRIVACY.md          # Політика приватності та класифікація даних
├─ manifests/
│  ├─ MANIFEST_raw_docs.csv
│  └─ CHECKSUMS_raw_docs.txt
├─ .github/workflows/
│  └─ ci.yml              # CI: перевірка цілісності, лінти
├─ PROJECT_PROTOCOL.md    # Компас проєкту (етапи, чеклісти, KPI)
├─ ULTRASIM.md            # Протокол валідації (5 стадій)
├─ VISION_MISSION.md      # Візія/Місія
├─ EXECUTIVE_SUMMARY.md   # Коротко для спільноти/інвесторів
├─ CONTRIBUTING.md        # Як контриб’ютити
├─ CODE_OF_CONDUCT.md     # Правила спільноти
├─ SECURITY.md            # Виявлення вразливостей
├─ CHANGELOG.md
├─ CITATION.cff           # Як цитувати роботу
├─ LICENSE                # MIT
└─ .gitignore
```

## Ліцензія
MIT — див. `LICENSE`.


---

## ZIP-CI Orchestrator v2 (Minimal UI flow)
**Кроки користувача:**  
1) Зберіть ZIP (без `.git/`).  
2) Завантажте у гілку `dev` → шлях `incoming/`.  
3) Відкрийте **Actions** і дивіться ✅/**❌**.

**Політика гілок:** `main` (прод) + тимчасові `zipci/<run_id>` від CI.  
Автоматичний PR і **auto-merge на GREEN**; **Issue з логами на RED**.  
Гілка `main` захищена, обов’язковий статус-чек: `zipci/gate`.

> Для первинної конфігурації запустіть вручну workflow **ZIPCI Bootstrap** (потрібен `secrets.ADMIN_TOKEN` з правами repo admin).


## Тести та покриття
- Запуск локально:  
  ```bash
  python -m pip install -U pip -r requirements-dev.txt
  pytest
  ```
- CI: `zipci/validate` виконує тести з **порогом покриття 95%** для Python-коду бібліотеки та скриптів.


## Quality Gates (Production)
- **Ruff** (PEP8+/pyupgrade/bugbear), **Black** (format), **Mypy** (strict), **Pytest** (coverage ≥95%).
- **Makefile** tasks: `make all` runs lint+type+test.
- **CLI**: `zipci-scan <file.zip>` — JSON report of ZIP safety.


### API Demo
Run: `uvicorn api.app:app --port 8000` → visit `/docs` for OpenAPI UI.


See **Engineering Standards**: [docs/ENGINEERING_STANDARDS.md](./docs/ENGINEERING_STANDARDS.md)
