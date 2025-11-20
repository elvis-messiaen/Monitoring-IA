"""
Monitoring module for Titanic ML API.
Contains custom Prometheus metrics and Evidently reports.
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


predictions_total = Counter(
    'ml_predictions_total',
    'Nombre total de prédictions effectuées',
    ['model_version', 'prediction_class']
)

prediction_latency = Histogram(
    'ml_prediction_latency_seconds',
    'Latence des prédictions en secondes',
    ['model_version'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

prediction_errors = Counter(
    'ml_prediction_errors_total',
    'Nombre total d\'erreurs lors des prédictions',
    ['error_type']
)

prediction_confidence = Gauge(
    'ml_prediction_confidence',
    'Confiance moyenne des prédictions (probabilité)',
    ['prediction_class']
)

prediction_confidence_summary = Summary(
    'ml_prediction_confidence_summary',
    'Statistiques de confiance des prédictions',
    ['model_version']
)

data_drift_detected = Counter(
    'ml_data_drift_detected_total',
    'Nombre de fois où un drift de données a été détecté',
    ['feature_name']
)

data_drift_score = Gauge(
    'ml_data_drift_score',
    'Score de drift global du dataset (0-1)',
)

model_accuracy = Gauge(
    'ml_model_accuracy',
    'Précision actuelle du modèle',
    ['model_version']
)

monitoring_requests = Counter(
    'ml_monitoring_requests_total',
    'Nombre total de requêtes de monitoring',
    ['endpoint']
)


def enregistrer_prediction(
    model_version: str,
    prediction_class: str,
    confidence: float,
    latency: float
) -> None:
    """
    Register a prediction in Prometheus metrics.

    Args:
        model_version: Model version used (e.g., "v1.0")
        prediction_class: Predicted class (e.g., "survived", "not_survived")
        confidence: Prediction confidence level (0-1)
        latency: Processing time in seconds
    """
    try:
        predictions_total.labels(
            model_version=model_version,
            prediction_class=prediction_class
        ).inc()

        prediction_latency.labels(model_version=model_version).observe(latency)
        prediction_confidence.labels(prediction_class=prediction_class).set(confidence)
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
    Register an error in Prometheus metrics.

    Args:
        error_type: Type of error encountered (e.g., "validation_error", "model_error")
    """
    try:
        prediction_errors.labels(error_type=error_type).inc()
        logger.warning(f"Erreur enregistrée: type={error_type}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'erreur: {e}")


def mettre_a_jour_accuracy(model_version: str, accuracy: float) -> None:
    """
    Update the model accuracy metric.

    Args:
        model_version: Model version
        accuracy: Model accuracy (0-1)
    """
    try:
        model_accuracy.labels(model_version=model_version).set(accuracy)
        logger.info(f"Accuracy mise à jour: version={model_version}, accuracy={accuracy:.3f}")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'accuracy: {e}")


def enregistrer_requete_monitoring(endpoint: str) -> None:
    """
    Register a request to a monitoring endpoint.

    Args:
        endpoint: Name of the called endpoint
    """
    try:
        monitoring_requests.labels(endpoint=endpoint).inc()
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la requête monitoring: {e}")


def generer_rapport_classification(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    target_column: str,
    prediction_column: str,
    output_path: Optional[Path] = None
) -> Dict:
    """
    Generate a classification performance report with Evidently.

    Args:
        reference_data: Reference data (training data)
        current_data: Current data (production data)
        target_column: Target column name
        prediction_column: Predictions column name
        output_path: Path to save HTML report (optional)

    Returns:
        Dictionary containing report results
    """
    try:
        logger.info("Génération du rapport de classification...")

        reference_df = reference_data.copy()
        current_df = current_data.copy()

        reference_df = reference_df.rename(columns={target_column: 'target', prediction_column: 'prediction'})
        current_df = current_df.rename(columns={target_column: 'target', prediction_column: 'prediction'})

        report = Report(metrics=[
            ClassificationPreset(),
        ])

        report_result = report.run(
            reference_data=reference_df,
            current_data=current_df
        )

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report_result.save_html(str(output_path))
            logger.info(f"Rapport de classification sauvegardé: {output_path}")

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
    Generate a drift detection report with Evidently.

    Args:
        reference_data: Reference data (training data)
        current_data: Current data (production data)
        output_path: Path to save HTML report (optional)

    Returns:
        Dictionary containing report results
    """
    try:
        logger.info("Génération du rapport de drift...")

        report = Report(metrics=[
            DataDriftPreset(),
        ])

        report_result = report.run(
            reference_data=reference_data,
            current_data=current_data
        )

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report_result.save_html(str(output_path))
            logger.info(f"Rapport de drift sauvegardé: {output_path}")

        resultats = report_result.as_dict() if hasattr(report_result, 'as_dict') else {}

        _mettre_a_jour_metriques_drift(resultats)

        logger.info("Rapport de drift généré avec succès")
        return resultats

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de drift: {e}")
        enregistrer_erreur("rapport_drift")
        raise


def _mettre_a_jour_metriques_drift(resultats_drift: Dict) -> None:
    """
    Update Prometheus metrics with drift results.

    Args:
        resultats_drift: Dictionary containing drift report results
    """
    try:
        metrics = resultats_drift.get('metrics', [])

        for metric in metrics:
            if metric.get('metric') == 'DatasetDriftMetric':
                result = metric.get('result', {})
                drift_score = result.get('dataset_drift_score', 0)
                drift_detected = result.get('drift_detected', False)

                data_drift_score.set(drift_score)

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
    Generate a complete report including classification and drift.

    Args:
        reference_data: Reference data
        current_data: Current data
        target_column: Target column name
        prediction_column: Predictions column name
        report_dir: Directory to save reports

    Returns:
        Dictionary containing all results
    """
    try:
        logger.info("Génération du rapport complet...")

        report_dir = Path(report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        classification_path = report_dir / f"classification_report_{timestamp}.html"
        resultats_classification = generer_rapport_classification(
            reference_data=reference_data,
            current_data=current_data,
            target_column=target_column,
            prediction_column=prediction_column,
            output_path=classification_path
        )

        drift_path = report_dir / f"drift_report_{timestamp}.html"
        resultats_drift = generer_rapport_drift(
            reference_data=reference_data,
            current_data=current_data,
            output_path=drift_path
        )

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


def obtenir_statistiques_metriques() -> Dict:
    """
    Get current Prometheus metrics statistics.

    Returns:
        Dictionary containing current metric values
    """
    try:
        enregistrer_requete_monitoring("statistiques_metriques")

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
    Reset certain Prometheus metrics.
    Used primarily for testing or debugging.
    """
    try:
        logger.warning("Réinitialisation des métriques demandée")
        logger.info("Les métriques Prometheus ne peuvent pas être réinitialisées")
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation des métriques: {e}")