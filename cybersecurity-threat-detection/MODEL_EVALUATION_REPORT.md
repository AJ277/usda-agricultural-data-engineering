# Cybersecurity Threat Detection — Model Evaluation

## Project Overview
An educational machine-learning demonstration using
5,000 synthetically generated network security events.

## Dataset
- Total events: 5,000
- Normal events: 4,223
- Suspicious events: 777
- Training events: 4042
- Testing events: 958
- Numeric model features: 8
- Test strategy: seeded random 80/20 split

## Logistic Regression
- Accuracy: 0.9990
- Suspicious precision: 1.0000
- Suspicious recall: 0.9928
- Suspicious F1: 0.9964
- True positives: 137
- True negatives: 820
- False positives: 0
- False negatives: 1

## Random Forest
- Accuracy: 1.0000
- Suspicious precision: 1.0000
- Suspicious recall: 1.0000
- Suspicious F1: 1.0000
- True positives: 138
- True negatives: 820
- False positives: 0
- False negatives: 0

## Random Forest Feature Importance
- failed_login_attempts: 0.4430
- failed_login_rate: 0.3439
- bytes_received: 0.1124
- duration_seconds: 0.0705
- send_receive_ratio: 0.0172
- destination_port: 0.0113
- total_bytes: 0.0016
- bytes_sent: 0.0000

## Experiment Tracking
- Tracking platform: Databricks MLflow
- Logistic Regression run: 54fe20188c4143149acbd2920c011bbe
- Random Forest run: 77103630eabb4c0689b099ed7efeb8f5

## Limitations
1. All security events are synthetic.
2. Labels were assigned before feature generation.
3. Normal and suspicious events have deliberately
   separable feature patterns, inflating performance.
4. The random split does not establish performance
   against future or independently collected attacks.
5. Feature importance is not a causal explanation.
6. The models have not been validated for production
   intrusion detection or automated enforcement.

## Conclusion
Both Spark MLlib classifiers completed training and
held-out evaluation. Random Forest achieved perfect
classification on this synthetic test split, but
real-world effectiveness remains unverified.