"""Verifier & Scorer (Role C): labels each claim using its evidence."""

from dehallucinator import config
from dehallucinator.models import Claim, Evidence, Verdict

_tokenizer = None
_model = None


def _load_model():
    """Lazily load the NLI model and tokenizer into module-level variables."""
    global _tokenizer, _model

    if _model is None or _tokenizer is None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(config.NLI_MODEL)
        _model = AutoModelForSequenceClassification.from_pretrained(config.NLI_MODEL)

    return _tokenizer, _model


def _predict(pairs: list[tuple[str, str]]) -> list[dict[str, float]]:
    """Return NLI label probabilities for each evidence-claim pair."""
    import torch

    tokenizer, model = _load_model()
    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)
    id2label = model.config.id2label

    results = []
    for row in probabilities:
        label_probs = {
            id2label[index].lower(): probability.item() for index, probability in enumerate(row)
        }
        results.append(label_probs)

    return results


def verify_claims(claims: list[Claim], evidence: list[Evidence]) -> list[Verdict]:
    """Return one verdict per claim based on its available evidence."""
    verdicts = []

    for claim in claims:
        claim_evidence = [item for item in evidence if item.claim_id == claim.id]

        if not claim_evidence:
            verdicts.append(
                Verdict(
                    claim_id=claim.id,
                    label="NOT_ENOUGH_INFO",
                    score=0.0,
                    best_evidence=None,
                )
            )
            continue

        pairs = [(item.snippet, claim.text) for item in claim_evidence]
        predictions = _predict(pairs)

        max_entailment = 0.0
        max_contradiction = 0.0
        best_entailment_index = 0
        best_contradiction_index = 0

        for index, prediction in enumerate(predictions):
            entailment = prediction.get("entailment", 0.0)
            contradiction = prediction.get("contradiction", 0.0)

            if entailment > max_entailment:
                max_entailment = entailment
                best_entailment_index = index

            if contradiction > max_contradiction:
                max_contradiction = contradiction
                best_contradiction_index = index

        if max_entailment >= config.SUPPORT_THRESHOLD and max_entailment >= max_contradiction:
            label = "SUPPORTED"
            score = max_entailment
            best_evidence = claim_evidence[best_entailment_index]
        elif max_contradiction >= config.CONTRADICT_THRESHOLD:
            label = "CONTRADICTED"
            score = max_contradiction
            best_evidence = claim_evidence[best_contradiction_index]
        else:
            label = "NOT_ENOUGH_INFO"
            score = 1.0 - max(max_entailment, max_contradiction)
            best_evidence = claim_evidence[best_entailment_index]

        verdicts.append(
            Verdict(
                claim_id=claim.id,
                label=label,
                score=score,
                best_evidence=best_evidence,
            )
        )

    return verdicts


def trust_score(verdicts: list[Verdict]) -> float:
    """Return the overall trust score (0-100) for an answer."""
    if not verdicts:
        return 100.0

    score_map = {
        "SUPPORTED": 1.0,
        "NOT_ENOUGH_INFO": 0.5,
        "CONTRADICTED": 0.0,
    }

    total = sum(score_map[v.label] for v in verdicts)
    avg = total / len(verdicts)
    return round(avg * 100, 1)
