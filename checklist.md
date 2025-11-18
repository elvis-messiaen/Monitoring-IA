# CHECKLIST - Monitoring d'une application ML

**Projet**: Monitoring ML avec Evidently AI, Prometheus & Grafana
**Dataset**: Titanic
**Date**: 2025-11-18

---

## 📊 Progression globale

- **Tâches complétées**: 31/40
- **Pourcentage accompli**: **77.5%** ✅
- **Pourcentage restant**: **22.5%** 🔄

---

## 1. Entraînement du modèle ML

### 1.1 Préparation des données
- [x] **FAIT** - Dataset Titanic disponible (`data/raw/Titanic-Dataset.csv`)
- [x] **FAIT** - Dataset nettoyé créé (`data/titanic_cleaned_dataset.csv`)
- [x] **FAIT** - Notebook d'exploration des données (`notebooks/01_data_exploration.ipynb`)
- [x] **FAIT** - Division en jeux d'entraînement, test et référence

### 1.2 Entraînement et sauvegarde
- [x] **FAIT** - Notebook d'entraînement du modèle (`notebooks/02_model_training.ipynb`)
- [ ] **À FAIRE** - Modèle entraîné et sauvegardé dans `models/` (fichier .pkl ou .joblib)
- [ ] **À FAIRE** - Validation des performances du modèle (accuracy, F1-score, etc.)

**Sous-total 1**: 5/7 tâches ✅ **(71.4%)**

---

## 2. Développement de l'API FastAPI

### 2.1 Structure de base
- [x] **FAIT** - API FastAPI créée (`api/main.py`)
- [x] **FAIT** - Dockerfile pour l'API (`api/Dockerfile`)
- [x] **FAIT** - Endpoint `/` (root)
- [x] **FAIT** - Endpoint `/health` (healthcheck Docker)
- [x] **FAIT** - Endpoint `/docs` (documentation Swagger auto-générée)
- [x] **FAIT** - Endpoint `/metrics` (métriques Prometheus)

### 2.2 Endpoints de prédiction
- [ ] **À FAIRE** - Endpoint `/predict` fonctionnel avec le modèle chargé
- [ ] **À FAIRE** - Validation des données d'entrée avec Pydantic
- [ ] **À FAIRE** - Enregistrement des données reçues pour monitoring

### 2.3 Endpoints de monitoring
- [x] **FAIT** - Endpoint `/monitoring/stats` (statistiques)
- [x] **FAIT** - Endpoint `/monitoring/test/prediction` (test prédiction)
- [x] **FAIT** - Endpoint `/monitoring/test/accuracy` (test accuracy)

**Sous-total 2**: 9/12 tâches ✅ **(75%)**

---

## 3. Mise en place de Prometheus et Grafana

### 3.1 Configuration Prometheus
- [x] **FAIT** - Installation de `prometheus-fastapi-instrumentator` dans l'API
- [x] **FAIT** - Fichier de configuration Prometheus (`prometheus/prometheus.yml`)
- [x] **FAIT** - Configuration du scraping des métriques API (port 8000)
- [x] **FAIT** - Configuration du scraping Prometheus self-monitoring (port 9090)
- [x] **FAIT** - Configuration du scraping cAdvisor (port 8080)
- [x] **FAIT** - Intervalle de scraping configuré (15 secondes)

### 3.2 Métriques Prometheus personnalisées
- [x] **FAIT** - Métriques ML créées dans `api/metrics/monitoring.py`:
  - [x] `ml_predictions_total` (Counter)
  - [x] `ml_prediction_latency_seconds` (Histogram)
  - [x] `ml_prediction_errors_total` (Counter)
  - [x] `ml_prediction_confidence` (Gauge)
  - [x] `ml_data_drift_score` (Gauge)
  - [x] `ml_model_accuracy` (Gauge)

### 3.3 Grafana
- [x] **FAIT** - Service Grafana dans docker-compose
- [x] **FAIT** - Configuration datasource Prometheus (`grafana/datasources/prometheus.yml`)
- [ ] **À FAIRE** - Dashboard Grafana pour les performances de l'API
  - [ ] Graphique: Temps de réponse / latence
  - [ ] Graphique: Nombre de requêtes par seconde
  - [ ] Graphique: Taux d'erreurs 4xx/5xx
  - [ ] Graphique: CPU et RAM (via cAdvisor)
- [ ] **À FAIRE** - Dashboard Grafana pour les métriques ML
  - [ ] Graphique: Nombre de prédictions par classe
  - [ ] Graphique: Latence des prédictions
  - [ ] Gauge: Accuracy du modèle
  - [ ] Gauge: Score de drift

**Sous-total 3**: 14/22 tâches ✅ **(63.6%)**

---

## 4. Monitoring avec Evidently AI

### 4.1 Installation et configuration
- [x] **FAIT** - Evidently AI installé dans requirements.txt
- [x] **FAIT** - Module de monitoring créé (`api/metrics/monitoring.py`)
- [x] **FAIT** - Imports Evidently correctement configurés (version 0.7+)

### 4.2 Rapports de drift
- [x] **FAIT** - Fonction `generer_rapport_drift()` implémentée
- [x] **FAIT** - Utilisation de `DataDriftPreset()`
- [x] **FAIT** - Sauvegarde des rapports HTML dans `reports/`
- [x] **FAIT** - Script de test `scripts/generer_rapport_test.py`
- [x] **FAIT** - Rapport de drift généré avec succès (`reports/drift_report_test.html`)

### 4.3 Rapports de performance
- [x] **FAIT** - Fonction `generer_rapport_classification()` implémentée
- [x] **FAIT** - Utilisation de `ClassificationPreset()`
- [ ] **À FAIRE** - Génération de rapport avec vraies prédictions du modèle

### 4.4 Intégration complète
- [x] **FAIT** - Fonction `generer_rapport_complet()` pour classification + drift
- [ ] **À FAIRE** - Exposition des métriques Evidently vers Prometheus/Grafana
- [ ] **À FAIRE** - Automatisation de la génération de rapports (cron job ou endpoint)

**Sous-total 4**: 10/13 tâches ✅ **(76.9%)**

---

## 5. Orchestration avec Docker Compose

### 5.1 Services Docker
- [x] **FAIT** - Service API FastAPI configuré
- [x] **FAIT** - Service Prometheus configuré
- [x] **FAIT** - Service Grafana configuré
- [x] **FAIT** - Service cAdvisor configuré
- [x] **FAIT** - Réseau Docker (`ml-monitoring`)
- [x] **FAIT** - Volumes persistants (prometheus_data, grafana_data)

### 5.2 Configuration
- [x] **FAIT** - Healthcheck pour l'API
- [x] **FAIT** - Variables d'environnement configurées
- [x] **FAIT** - Restart policy (`unless-stopped`)
- [x] **FAIT** - Ports exposés correctement

**Sous-total 5**: 10/10 tâches ✅ **(100%)** 🎉

---

## 6. Documentation et livrables

### 6.1 Documentation
- [x] **FAIT** - README.md complet avec:
  - [x] Description du projet
  - [x] Architecture
  - [x] Instructions de démarrage
  - [x] Points d'accès (URLs)
  - [x] Métriques disponibles
  - [x] Exemples d'utilisation
  - [x] Troubleshooting
- [x] **FAIT** - CLAUDE.md (guide pour Claude Code)
- [x] **FAIT** - tempo.md (guide de démarrage rapide)
- [x] **FAIT** - Commentaires et docstrings en français dans le code

### 6.2 Code et bonnes pratiques
- [x] **FAIT** - Code modulaire (séparation api/metrics/)
- [x] **FAIT** - Fonctions avec docstrings explicatives
- [x] **FAIT** - Gestion des erreurs avec try/except
- [x] **FAIT** - Logging structuré (loguru)
- [ ] **À FAIRE** - Tests unitaires pour les fonctions de monitoring
- [ ] **À FAIRE** - Tests d'intégration pour les endpoints

### 6.3 Repository GitHub
- [x] **FAIT** - Repository Git initialisé
- [x] **FAIT** - Fichier .gitignore approprié
- [x] **FAIT** - Branches (main, dev, feature branches)
- [ ] **À FAIRE** - Code review et merge final

**Sous-total 6**: 16/20 tâches ✅ **(80%)**

---

## 📋 Résumé par catégorie

| Catégorie | Tâches complétées | Total | Pourcentage |
|-----------|-------------------|-------|-------------|
| 1. Entraînement du modèle | 5 | 7 | 71.4% |
| 2. API FastAPI | 9 | 12 | 75% |
| 3. Prometheus & Grafana | 14 | 22 | 63.6% |
| 4. Evidently AI | 10 | 13 | 76.9% |
| 5. Docker Compose | 10 | 10 | 100% ✅ |
| 6. Documentation | 16 | 20 | 80% |
| **TOTAL** | **31** | **40** | **77.5%** |

---

## 🎯 Priorités pour finaliser le projet

### Priorité HAUTE (bloquant) 🔴
1. **Entraîner et sauvegarder le modèle ML** dans `models/`
2. **Implémenter l'endpoint `/predict`** avec le modèle chargé
3. **Créer les dashboards Grafana** (API + ML metrics)

### Priorité MOYENNE (important) 🟡
4. Générer des rapports Evidently avec vraies prédictions
5. Exposer les métriques Evidently vers Grafana
6. Ajouter des tests unitaires et d'intégration

### Priorité BASSE (amélioration) 🟢
7. Automatiser la génération des rapports Evidently
8. Configurer des alertes Prometheus
9. Optimiser les performances

---

## 📝 Notes

- **Dataset**: Titanic (714 lignes, 4 colonnes nettoyées)
- **Version Evidently**: 0.7.16 (utilise Presets)
- **Version Python**: 3.13.5
- **Stack technique**: FastAPI + Prometheus + Grafana + Evidently + Docker
- **Tous les services démarrent correctement** avec `docker-compose up -d --build`

---

**Dernière mise à jour**: 2025-11-18
**Statut global**: 🟢 **EN BONNE VOIE** (77.5% complété)