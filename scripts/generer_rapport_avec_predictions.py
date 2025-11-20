"""
Script to generate an Evidently report with real model predictions.
Loads the trained model, makes predictions on test data,
then generates a complete report (classification + drift).
"""

import sys
from pathlib import Path
import pandas as pd
import joblib

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.metrics.monitoring import generer_rapport_drift

print("=" * 70)
print("GENERATION DE RAPPORT EVIDENTLY AVEC VRAIES PREDICTIONS")
print("=" * 70)
print()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"

print(f"📦 Chargement du modele depuis: {MODEL_PATH}")

if not MODEL_PATH.exists():
    print(f"❌ Erreur: Le modele n'existe pas a {MODEL_PATH}")
    print("Veuillez d'abord entrainer le modele avec le notebook 02_model_training.ipynb")
    sys.exit(1)

try:
    pipeline = joblib.load(MODEL_PATH)
    print("✅ Modele charge avec succes")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modele: {e}")
    sys.exit(1)

print()

data_path = BASE_DIR / "data" / "titanic_cleaned_dataset.csv"

print(f"📂 Chargement des donnees depuis: {data_path}")

if not data_path.exists():
    print(f"❌ Erreur: Fichier {data_path} introuvable")
    sys.exit(1)

try:
    df = pd.read_csv(data_path)
    print(f"✅ Donnees chargees: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"   Colonnes: {list(df.columns)}")
except Exception as e:
    print(f"❌ Erreur lors du chargement des donnees: {e}")
    sys.exit(1)

print()

print("📊 Preparation des donnees...")

split_idx = int(len(df) * 0.7)
train_data = df.iloc[:split_idx].copy()
test_data = df.iloc[split_idx:].copy()

print(f"   Donnees d'entrainement (reference): {len(train_data)} lignes")
print(f"   Donnees de test (current): {len(test_data)} lignes")
print()

print("🔮 Generation des predictions sur les donnees de test...")

try:
    def encode_sex(sex_value):
        """
        Encode Sex: 0 for M, 1 for F.

        Args:
            sex_value: Sex value to encode

        Returns:
            Encoded sex value
        """
        return 0 if sex_value == 0 else 1

    if test_data['Sex'].dtype == 'object':
        test_data_encoded = test_data.copy()
        test_data_encoded['Sex'] = test_data_encoded['Sex'].apply(
            lambda x: 0 if x.upper() == 'M' else 1
        )
    else:
        test_data_encoded = test_data.copy()

    X_test = test_data_encoded[['Sex', 'Fare']]
    predictions = pipeline.predict(X_test)

    test_data['prediction'] = predictions

    print(f"✅ Predictions generees: {len(predictions)} predictions")
    print(f"   Distribution des predictions:")
    print(f"   - Classe 0 (Died): {(predictions == 0).sum()} ({(predictions == 0).sum() / len(predictions) * 100:.1f}%)")
    print(f"   - Classe 1 (Survived): {(predictions == 1).sum()} ({(predictions == 1).sum() / len(predictions) * 100:.1f}%)")

except Exception as e:
    print(f"❌ Erreur lors de la generation des predictions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

print("📝 Ajout des predictions aux donnees de reference...")

try:
    train_data['prediction'] = train_data['Survived']

    print(f"✅ Colonnes dans train_data: {list(train_data.columns)}")
    print(f"✅ Colonnes dans test_data: {list(test_data.columns)}")

except Exception as e:
    print(f"❌ Erreur lors de l'ajout des predictions: {e}")
    sys.exit(1)

print()

print("📊 Generation du rapport Evidently de drift avec predictions...")

reports_dir = BASE_DIR / "reports"
reports_dir.mkdir(exist_ok=True)

try:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    drift_report_path = reports_dir / f"drift_report_with_predictions_{timestamp}.html"

    rapport = generer_rapport_drift(
        reference_data=train_data,
        current_data=test_data,
        output_path=drift_report_path
    )

    print()
    print("=" * 70)
    print("RAPPORT GENERE AVEC SUCCES ✅")
    print("=" * 70)
    print()
    print("📄 Fichier genere:")
    print(f"   - Drift avec predictions: {drift_report_path}")
    print()
    print("Pour visualiser le rapport, ouvrez le fichier HTML dans votre navigateur:")
    print(f"   open {drift_report_path}")
    print()

    print("📈 Le rapport inclut:")
    print("   - Analyse du drift entre donnees d'entrainement et de test")
    print("   - Comparaison des distributions des features (Sex, Fare)")
    print("   - Comparaison des predictions vs valeurs reelles")
    print()

except Exception as e:
    print(f"❌ Erreur lors de la generation du rapport: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("FIN DU SCRIPT")
print("=" * 70)