"""
Script to generate a test Evidently report.
Uses Titanic data to create a sample report.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.metrics.monitoring import generer_rapport_drift

print("=" * 70)
print("GENERATION D'UN RAPPORT EVIDENTLY DE TEST")
print("=" * 70)
print()

data_path = Path("data/titanic_cleaned_dataset.csv")

if not data_path.exists():
    print(f"❌ Erreur: Fichier {data_path} introuvable")
    print("Assurez-vous d'avoir les donnees Titanic dans data/")
    sys.exit(1)

print(f"📂 Chargement des donnees depuis: {data_path}")
df = pd.read_csv(data_path)
print(f"✅ Donnees chargees: {len(df)} lignes, {len(df.columns)} colonnes")
print()

split_idx = int(len(df) * 0.7)
reference_data = df.iloc[:split_idx]
current_data = df.iloc[split_idx:]

print(f"📊 Donnees de reference: {len(reference_data)} lignes")
print(f"📊 Donnees actuelles: {len(current_data)} lignes")
print()

reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)

print("🔄 Generation du rapport de drift...")
try:
    output_path = reports_dir / "drift_report_test.html"

    resultat = generer_rapport_drift(
        reference_data=reference_data,
        current_data=current_data,
        output_path=output_path
    )

    print(f"✅ Rapport genere avec succes!")
    print(f"📄 Fichier: {output_path}")
    print()
    print("Pour voir le rapport, executez:")
    print(f"  open {output_path}")
    print()
    print("Ou dans le navigateur:")
    print(f"  file://{output_path.absolute()}")

except Exception as e:
    print(f"❌ Erreur lors de la generation du rapport: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("RAPPORT GENERE AVEC SUCCES ✅")
print("=" * 70)