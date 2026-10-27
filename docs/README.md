# Project documents

All project documents live here, so every change is a reviewed commit. Edit your own
section on a branch (`docs/DH-<n>-<short-name>`) and open a pull request, same as code.

| Document | File | Owner |
|---|---|---|
| Software Requirements Specification | [`srs/SRS.md`](srs/SRS.md) (v1.0 PDF: [`srs/SRS_Dehallucinator.pdf`](srs/SRS_Dehallucinator.pdf)) | Compiled by Shreya (B); each member owns their section |
| Architecture | [`architecture/architecture.md`](architecture/architecture.md) | Compiled by Nikitha (A); each member owns their component |
| Architecture – Evidence Retriever | [`architecture_evidence_retriever.md`](architecture_evidence_retriever.md) | Shreya (B) |
| Architecture – Verifier & Scorer | [`architecture/architecture_verifier.md`](architecture/architecture_verifier.md) | Ralph (C) |
| Architecture – API, UI and deployment | [`architecture/architecture_api_ui_deployment.md`](architecture/architecture_api_ui_deployment.md) | Satwik (D) |
| Design – Corrector, pipeline and API (with [`openapi.json`](design/openapi.json)) | [`design/design_corrector_pipeline_api.md`](design/design_corrector_pipeline_api.md) | Satwik (D) |
| Test plan and test cases | [`test-plan/test_plan.md`](test-plan/test_plan.md) | Compiled by Ralph (C); each member owns their use case |
| UC-2 test cases | [`test_cases_UC-2.md`](test_cases_UC-2.md) | Shreya (B) |
| Sprint logs | [`sprints/`](sprints/) | Nikitha (A) |
| LLM prompt logs | [`llm-prompts/`](llm-prompts/) | Everyone (one file per role) |

Planned: the other roles' design docs (`design/`), validation report and maintenance plan.

Diagrams go next to the document that uses them (for example
`architecture/architecture_diagram.png`) and are linked with a relative path.
