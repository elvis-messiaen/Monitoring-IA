"""
Monitoring package for Titanic ML API.
Exposes main monitoring functions and Prometheus metrics.
"""

from .monitoring import (
    predictions_total,
    prediction_latency,
    prediction_errors,
    prediction_confidence,
    prediction_confidence_summary,
    data_drift_detected,
    data_drift_score,
    model_accuracy,
    monitoring_requests,
    enregistrer_prediction,
    enregistrer_erreur,
    mettre_a_jour_accuracy,
    enregistrer_requete_monitoring,
    generer_rapport_classification,
    generer_rapport_drift,
    generer_rapport_complet,
    obtenir_statistiques_metriques,
    reinitialiser_metriques,
)

__all__ = [
    "predictions_total",
    "prediction_latency",
    "prediction_errors",
    "prediction_confidence",
    "prediction_confidence_summary",
    "data_drift_detected",
    "data_drift_score",
    "model_accuracy",
    "monitoring_requests",
    "enregistrer_prediction",
    "enregistrer_erreur",
    "mettre_a_jour_accuracy",
    "enregistrer_requete_monitoring",
    "generer_rapport_classification",
    "generer_rapport_drift",
    "generer_rapport_complet",
    "obtenir_statistiques_metriques",
    "reinitialiser_metriques",
]