"""
Package de monitoring pour l'API ML Titanic.
Expose les fonctions principales de monitoring et les metriques Prometheus.
"""

from .monitoring import (
    # Metriques Prometheus
    predictions_total,
    prediction_latency,
    prediction_errors,
    prediction_confidence,
    prediction_confidence_summary,
    data_drift_detected,
    data_drift_score,
    model_accuracy,
    monitoring_requests,

    # Fonctions de collecte de metriques
    enregistrer_prediction,
    enregistrer_erreur,
    mettre_a_jour_accuracy,
    enregistrer_requete_monitoring,

    # Fonctions de generation de rapports Evidently
    generer_rapport_classification,
    generer_rapport_drift,
    generer_rapport_complet,

    # Fonctions utilitaires
    obtenir_statistiques_metriques,
    reinitialiser_metriques,
)

__all__ = [
    # Metriques Prometheus
    "predictions_total",
    "prediction_latency",
    "prediction_errors",
    "prediction_confidence",
    "prediction_confidence_summary",
    "data_drift_detected",
    "data_drift_score",
    "model_accuracy",
    "monitoring_requests",

    # Fonctions de collecte de metriques
    "enregistrer_prediction",
    "enregistrer_erreur",
    "mettre_a_jour_accuracy",
    "enregistrer_requete_monitoring",

    # Fonctions de generation de rapports
    "generer_rapport_classification",
    "generer_rapport_drift",
    "generer_rapport_complet",

    # Fonctions utilitaires
    "obtenir_statistiques_metriques",
    "reinitialiser_metriques",
]