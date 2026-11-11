Source: https://ieeexplore.ieee.org/abstract/document/11403491
Retrieved: 2026-10-22
Access: abstract + beginning of §I only (PDF purchase required; "References is not available for this document")

Title: Integrating Federated Learning and Deep Q-Networks for Resilient Healthcare Supply Chain
Optimization amidst Uncertain Demand
Authors: Gurwinder Singh; Nikhil Aggarwal
Published in: 2025 2nd International Conference on Artificial Intelligence for Innovations in Healthcare
Industries (ICAIIHI)
Date of Conference: 04-05 December 2025
Conference Location: Raipur, India
Date Added to IEEE Xplore: 25 February 2026
DOI: 10.1109/ICAIIHI67124.2025.11403491
Metrics shown on page: 1 citation, 43 full-text views

ABSTRACT (verbatim)

Healthcare supply chains face challenges from uncertain demand, strict privacy restrictions and
fragmented data across institutions. This paper proposes FedDQN-SC, a federated reinforcement
learning framework that integrates federated learning (FL) with Deep Q-networks (DQN) for
privacy-preserving and distributed inventory optimization. Local DQN agents learn about ordering
policies using institutional data, while model updates are collected securely without sharing raw
records. The framework includes FedProx regularization and differential privacy to address non-iid
demand and communication bottlenecks. Experimental evaluation of pharmaceutical supply chain
datasets shows that FedDQN-SC achieves up to 18% higher service level, 22% lower inventory and 15%
lower operating costs compared to centralized and local baselines. During demand shock scenarios,
the FedDQN-SC maintains the service level above 80%, while the baseline falls below 65%. These
results show that combining FL with deep reinforcement learning enables flexible, efficient and
privacy-conscious optimization of the healthcare supply chain under uncertainty.

I. INTRODUCTION (first paragraph only; remainder behind sign-in)

The healthcare supply chain is critical towards healthcare delivery, availability of medicines,
vaccines, and equipment, but in the recent past, the COVID-19 pandemic has exposed the supply chain
to demand shocks, transportation delays, and shortages. Traditional models such as the Economic
order quantity (EOQ) and base-stock models are best applied in homogeneous and certain environment
as they cannot be applied in heterogeneous and uncertain environment.

NOTE ON EVIDENCE QUALITY
Conference paper, two authors, short page budget, no dataset named, no per-client results in the
abstract, no code or data link. The 18/22/15% figures cannot be audited from what is publicly
available. Cite as an existence proof for FL-based ordering in healthcare supply chains, not as a
benchmark to reproduce or beat.
