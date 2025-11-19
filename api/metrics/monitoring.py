"""
Module de monitoring pour l'API ML Titanic.
Ce module contient les métriques Prometheus personnalisées et les rapports Evidently.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge, Summary
from evidently import Report
from evidently.presets import ClassificationPreset, DataDriftPreset
from evidently.legacy.pipeline.column_mapping import ColumnMapping
from loguru import logger


# ============================================================
# MÉTRIQUES PROMETHEUS PERSONNALISÉES
# ============================================================

# Compteur de prédictions totales
predictions_total = Counter(
    'ml_predictions_total',
    'Nombre total de prédictions effectuées',
    ['model_version', 'prediction_class']
)

# Histogramme de la latence des prédictions
prediction_latency = Histogram(
    'ml_prediction_latency_seconds',
    'Latence des prédictions en secondes',
    ['model_version'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

# Compteur d'erreurs de prédiction
prediction_errors = Counter(
    'ml_prediction_errors_total',
    'Nombre total d\'erreurs lors des prédictions',
    ['error_type']
)

# Gauge pour la confiance moyenne des prédictions
prediction_confidence = Gauge(
    'ml_prediction_confidence',
    'Confiance moyenne des prédictions (probabilité)',
    ['prediction_class']
)

# Summary pour les statistiques de confiance
prediction_confidence_summary = Summary(
    'ml_prediction_confidence_summary',
    'Statistiques de confiance des prédictions',
    ['model_version']
)

# Compteur de drift détecté
data_drift_detected = Counter(
    'ml_data_drift_detected_total',
    'Nombre de fois où un drift de données a été détecté',
    ['feature_name']
)

# Gauge pour le score de drift global
data_drift_score = Gauge(
    'ml_data_drift_score',
    'Score de drift global du dataset (0-1)',
)

# Compteur pour le monitoring de la qualité du modèle
model_accuracy = Gauge(
    'ml_model_accuracy',
    'Précision actuelle du modèle',
    ['model_version']
)

# Compteur de requêtes de monitoring
monitoring_requests = Counter(
    'ml_monitoring_requests_total',
    'Nombre total de requêtes de monitoring',
    ['endpoint']
)


# ============================================================
# FONCTIONS DE COLLECTE DE MÉTRIQUES
# ============================================================

def enregistrer_prediction(
    model_version: str,
    prediction_class: str,
    confidence: float,
    latency: float
) -> None:
    """
    Enregistre une prédiction dans les métriques Prometheus.

    Args:
        model_version: Version du modèle utilisé (ex: "v1.0")
        prediction_class: Classe prédite (ex: "survived", "not_survived")
        confidence: Niveau de confiance de la prédiction (0-1)
        latency: Temps de traitement en secondes
    """
    try:
        # Incrémenter le compteur de prédictions
        predictions_total.labels(
            model_version=model_version,
            prediction_class=prediction_class
        ).inc()

        # Enregistrer la latence
        prediction_latency.labels(model_version=model_version).observe(latency)

        # Mettre à jour la confiance
        prediction_confidence.labels(prediction_class=prediction_class).set(confidence)

        # Ajouter au summary de confiance
        prediction_confidence_summary.labels(model_version=model_version).observe(confidence)

        logger.info(
            f"Prédiction enregistrée: version={model_version}, "
            f"classe={prediction_class}, confiance={confidence:.3f}, "
            f"latence={latency:.3f}s"
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la prédiction: {e}")
        enregistrer_erreur("enregistrement_prediction")


def enregistrer_erreur(error_type: str) -> None:
    """
    Enregistre une erreur dans les métriques Prometheus.

    Args:
        error_type: Type d'erreur rencontrée (ex: "validation_error", "model_error")
    """
    try:
        prediction_errors.labels(error_type=error_type).inc()
        logger.warning(f"Erreur enregistrée: type={error_type}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'erreur: {e}")


def mettre_a_jour_accuracy(model_version: str, accuracy: float) -> None:
    """
    Met à jour la métrique d'accuracy du modèle.

    Args:
        model_version: Version du modèle
        accuracy: Précision du modèle (0-1)
    """
    try:
        model_accuracy.labels(model_version=model_version).set(accuracy)
        logger.info(f"Accuracy mise à jour: version={model_version}, accuracy={accuracy:.3f}")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'accuracy: {e}")


def enregistrer_requete_monitoring(endpoint: str) -> None:
    """
    Enregistre une requête vers un endpoint de monitoring.

    Args:
        endpoint: Nom de l'endpoint appelé
    """
    try:
        monitoring_requests.labels(endpoint=endpoint).inc()
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la requête monitoring: {e}")


# ============================================================
# RAPPORTS EVIDENTLY
# ============================================================

def generer_rapport_classification(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    target_column: str,
    prediction_column: str,
    output_path: Optional[Path] = None
) -> Dict:
    """
    Génère un rapport de performance de classification avec Evidently.

    Args:
        reference_data: Données de référence (données d'entraînement)
        current_data: Données actuelles (données de production)
        target_column: Nom de la colonne cible
        prediction_column: Nom de la colonne de prédictions
        output_path: Chemin où sauvegarder le rapport HTML (optionnel)

    Returns:
        Dictionnaire contenant les résultats du rapport
    """
    try:
        logger.info("Génération du rapport de classification...")

        # Preparer les donnees pour Evidently: renommer les colonnes target et prediction
        # Evidently 0.7 detecte automatiquement les colonnes 'target' et 'prediction'
        reference_df = reference_data.copy()
        current_df = current_data.copy()

        # Renommer les colonnes pour qu'Evidently les detecte automatiquement
        reference_df = reference_df.rename(columns={target_column: 'target', prediction_column: 'prediction'})
        current_df = current_df.rename(columns={target_column: 'target', prediction_column: 'prediction'})

        # Créer le rapport avec le preset de classification Evidently 0.7+
        report = Report(metrics=[
            ClassificationPreset(),
        ])

        # Exécuter le rapport (Evidently detecte automatiquement les colonnes 'target' et 'prediction')
        report_result = report.run(
            reference_data=reference_df,
            current_data=current_df
        )

        # Sauvegarder le rapport si un chemin est fourni
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report_result.save_html(str(output_path))
            logger.info(f"Rapport de classification sauvegardé: {output_path}")

        # Extraire les résultats
        resultats = report_result.as_dict() if hasattr(report_result, 'as_dict') else {}

        logger.info("Rapport de classification généré avec succès")
        return resultats

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de classification: {e}")
        enregistrer_erreur("rapport_classification")
        raise


def generer_rapport_drift(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    output_path: Optional[Path] = None
) -> Dict:
    """
    Génère un rapport de détection de drift avec Evidently.

    Args:
        reference_data: Données de référence (données d'entraînement)
        current_data: Données actuelles (données de production)
        output_path: Chemin où sauvegarder le rapport HTML (optionnel)

    Returns:
        Dictionnaire contenant les résultats du rapport
    """
    try:
        logger.info("Génération du rapport de drift...")

        # Créer le rapport avec le preset de drift Evidently 0.7+
        report = Report(metrics=[
            DataDriftPreset(),
        ])

        # Exécuter le rapport - run() retourne le resultat
        report_result = report.run(
            reference_data=reference_data,
            current_data=current_data
        )

        # Sauvegarder le rapport si un chemin est fourni
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report_result.save_html(str(output_path))
            logger.info(f"Rapport de drift sauvegardé: {output_path}")

        # Extraire les résultats
        resultats = report_result.as_dict() if hasattr(report_result, 'as_dict') else {}

        # Mettre à jour les métriques Prometheus
        _mettre_a_jour_metriques_drift(resultats)

        logger.info("Rapport de drift généré avec succès")
        return resultats

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de drift: {e}")
        enregistrer_erreur("rapport_drift")
        raise


def _mettre_a_jour_metriques_drift(resultats_drift: Dict) -> None:
    """
    Met à jour les métriques Prometheus avec les résultats du drift.

    Args:
        resultats_drift: Dictionnaire contenant les résultats du rapport de drift
    """
    try:
        # Extraire le score de drift global
        metrics = resultats_drift.get('metrics', [])

        for metric in metrics:
            if metric.get('metric') == 'DatasetDriftMetric':
                result = metric.get('result', {})
                drift_score = result.get('dataset_drift_score', 0)
                drift_detected = result.get('drift_detected', False)

                # Mettre à jour le score de drift global
                data_drift_score.set(drift_score)

                # Enregistrer les drifts détectés par feature
                drift_by_columns = result.get('drift_by_columns', {})
                for feature_name, feature_drift in drift_by_columns.items():
                    if feature_drift.get('drift_detected', False):
                        data_drift_detected.labels(feature_name=feature_name).inc()

                logger.info(
                    f"Métriques de drift mises à jour: "
                    f"score={drift_score:.3f}, détecté={drift_detected}"
                )
                break

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des métriques de drift: {e}")


def generer_rapport_complet(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    target_column: str,
    prediction_column: str,
    report_dir: Path = Path("/app/reports")
) -> Dict:
    """
    Génère un rapport complet incluant la classification et le drift.

    Args:
        reference_data: Données de référence
        current_data: Données actuelles
        target_column: Nom de la colonne cible
        prediction_column: Nom de la colonne de prédictions
        report_dir: Répertoire où sauvegarder les rapports

    Returns:
        Dictionnaire contenant tous les résultats
    """
    try:
        logger.info("Génération du rapport complet...")

        # Créer le répertoire de rapports s'il n'existe pas
        report_dir = Path(report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)

        # Générer un timestamp pour les noms de fichiers
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Générer le rapport de classification
        classification_path = report_dir / f"classification_report_{timestamp}.html"
        resultats_classification = generer_rapport_classification(
            reference_data=reference_data,
            current_data=current_data,
            target_column=target_column,
            prediction_column=prediction_column,
            output_path=classification_path
        )

        # Générer le rapport de drift
        drift_path = report_dir / f"drift_report_{timestamp}.html"
        resultats_drift = generer_rapport_drift(
            reference_data=reference_data,
            current_data=current_data,
            output_path=drift_path
        )

        # Combiner les résultats
        rapport_complet = {
            "timestamp": timestamp,
            "classification": resultats_classification,
            "drift": resultats_drift,
            "fichiers": {
                "classification": str(classification_path),
                "drift": str(drift_path)
            }
        }

        logger.info("Rapport complet généré avec succès")
        return rapport_complet

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport complet: {e}")
        enregistrer_erreur("rapport_complet")
        raise


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def obtenir_statistiques_metriques() -> Dict:
    """
    Récupère les statistiques actuelles des métriques Prometheus.

    Returns:
        Dictionnaire contenant les valeurs actuelles des métriques
    """
    try:
        enregistrer_requete_monitoring("statistiques_metriques")

        # Cette fonction pourrait être étendue pour extraire
        # les valeurs actuelles des métriques Prometheus
        # Pour l'instant, elle retourne un dictionnaire vide
        # qui sera rempli lors de l'intégration avec l'API

        statistiques = {
            "message": "Consultez /metrics pour les métriques Prometheus complètes"
        }

        return statistiques

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        enregistrer_erreur("statistiques_metriques")
        raise


def reinitialiser_metriques() -> None:
    """
    Réinitialise certaines métriques Prometheus.
    Utilisé principalement pour les tests ou le debugging.
    """
    try:
        logger.warning("Réinitialisation des métriques demandée")
        # Les métriques Prometheus ne peuvent pas être réinitialisées facilement
        # Cette fonction est un placeholder pour une future implémentation
        logger.info("Les métriques Prometheus ne peuvent pas être réinitialisées")
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation des métriques: {e}")
