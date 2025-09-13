# UMAA+EPAUP Metrics

The engine evaluates responses using a set of UMAA+EPAUP metrics:

- **Role Adherence** – alignment with the assigned role.
- **Reasoning Soundness** – logical consistency of the answer.
- **Ethical Compliance** – conformity to content policies.
- **Hallucination Risk** – likelihood of unsupported claims.
- **Stability** – output variance under fixed settings.

Rubrics are defined in `config/rubrics/` and loaded at runtime.
