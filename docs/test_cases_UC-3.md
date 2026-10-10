\# Test Cases: UC-3 Verify Claims and Score Answer (TC-3-01 to TC-3-10)



Module: Verifier \& Scorer (Role C). Requirements: FR-3.1 to FR-3.6, NFR-4.



\## Test cases



| ID      | Title                                        | Requirement    | Type   | Preconditions                                                      | Input                                                                                                                                                         | Steps                                                      | Expected result                                                                                      | Automated test                    |

| ------- | -------------------------------------------- | -------------- | ------ | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------- |

| TC-3-01 | Model loaded lazily once                     | FR-3.1         | Normal | Model not yet loaded; model loading mocked                         | Multiple calls to `verify\_claims`                                                                                                                             | Call `verify\_claims` more than once                        | Model is loaded only when needed and reused on subsequent calls                                      | To be added                       |

| TC-3-02 | Claim supported by evidence                  | FR-3.2, FR-3.3 | Normal | NLI model mocked                                                   | Entailment probability at or above `SUPPORT\_THRESHOLD` and at least the contradiction probability                                                             | Call `verify\_claims` with a claim and matching evidence    | Verdict is `SUPPORTED`; score reflects entailment probability                                        | To be added                       |

| TC-3-03 | Claim contradicted by evidence               | FR-3.2, FR-3.3 | Normal | NLI model mocked                                                   | Contradiction probability at or above `CONTRADICT\_THRESHOLD`                                                                                                  | Call `verify\_claims` with a claim and conflicting evidence | Verdict is `CONTRADICTED`                                                                            | To be added                       |

| TC-3-04 | Neither supported nor contradicted           | FR-3.2, FR-3.3 | Normal | NLI model mocked                                                   | Probabilities do not satisfy either threshold rule                                                                                                            | Call `verify\_claims` with a claim and evidence             | Verdict is `NOT\_ENOUGH\_INFO`                                                                         | To be added                       |

| TC-3-05 | No evidence available                        | FR-3.4         | Error  | Model call mocked                                                  | Claim with no matching evidence                                                                                                                               | Call `verify\_claims`                                       | Verdict is `NOT\_ENOUGH\_INFO`, score is `0.0`, `best\_evidence` is `None`, and the model is not called | To be added                       |

| TC-3-06 | Number mismatch forces contradiction         | FR-3.5         | Error  | NLI model mocked; claim and evidence mention the same named entity | Claim: "The Eiffel Tower was built in 1889." Evidence: "The Eiffel Tower was built in 1890." NLI probabilities would not independently produce `CONTRADICTED` | Call `verify\_claims`                                       | Number mismatch rule forces `CONTRADICTED`; score is at least `0.75`                                 | To be added                       |

| TC-3-07 | Matching number does not force contradiction | FR-3.5         | Normal | NLI model mocked; claim and evidence mention the same named entity | Claim: "The Eiffel Tower was built in 1889." Evidence: "The Eiffel Tower was built in 1889."                                                                  | Call `verify\_claims`                                       | Number mismatch rule does not force `CONTRADICTED`; verdict follows NLI thresholds                   | To be added                       |

| TC-3-08 | Trust score for mixed verdicts               | FR-3.6         | Normal | Verdicts available                                                 | One `SUPPORTED`, one `NOT\_ENOUGH\_INFO`, and one `CONTRADICTED` verdict                                                                                        | Call `trust\_score`                                         | Trust score is `50.0`                                                                                | `test\_trust\_score\_mixed\_verdicts` |

| TC-3-09 | Trust score with no verdicts                 | FR-3.6         | Normal | Empty verdict list                                                 | `\[]`                                                                                                                                                          | Call `trust\_score`                                         | Trust score is `100.0`                                                                               | `test\_trust\_score\_empty\_list`     |

| TC-3-10 | Trust score rounded to one decimal           | FR-3.6         | Normal | Verdicts available                                                 | Two `SUPPORTED` verdicts and one `NOT\_ENOUGH\_INFO` verdict                                                                                                    | Call `trust\_score`                                         | Trust score is `83.3`, rounded to one decimal place                                                  | To be added                       |



\## Traceability (requirement to test case)



| Requirement | Description                                                                           | Test cases                              |

| ----------- | ------------------------------------------------------------------------------------- | --------------------------------------- |

| FR-3.1      | Load NLI model lazily and reuse it                                                    | TC-3-01                                 |

| FR-3.2      | Batch-score claim-evidence pairs using softmax probabilities inside `torch.no\_grad()` | TC-3-02, TC-3-03, TC-3-04               |

| FR-3.3      | Assign verdicts using entailment and contradiction thresholds                         | TC-3-02, TC-3-03, TC-3-04               |

| FR-3.4      | Handle claims with no evidence without calling the model                              | TC-3-05                                 |

| FR-3.5      | Force contradiction for qualifying number mismatches                                  | TC-3-06, TC-3-07                        |

| FR-3.6      | Calculate and round the overall trust score; return 100 for an empty list             | TC-3-08, TC-3-09, TC-3-10               |

| NFR-4       | Maintain at least 80% unit test coverage                                              | Verify through the test coverage report |



Error cases: TC-3-05, TC-3-06.



\*\*Automation status:\*\* TC-3-08 and TC-3-09 map to existing automated tests. TC-3-01 to TC-3-07 and TC-3-10 are documented test cases for which corresponding automated tests still need to be added or verified. The automated test names listed above are not claims that all test cases have passed.
