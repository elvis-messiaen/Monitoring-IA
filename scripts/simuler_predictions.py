"""
Script to simulate 10 random predictions to test the monitoring system.
Generates random combinations of sex (M/F) and fare (low/high).
"""

import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8000"

PRIX_BAS = (5.0, 30.0)
PRIX_HAUT = (50.0, 150.0)


def generer_passager_aleatoire():
    """
    Generate a random passenger with sex and fare.

    Returns:
        Dictionary with Sex, Fare, and category
    """
    sex = random.choice(['M', 'F'])

    if random.random() < 0.5:
        fare = round(random.uniform(*PRIX_BAS), 2)
        categorie = "Prix bas"
    else:
        fare = round(random.uniform(*PRIX_HAUT), 2)
        categorie = "Prix haut"

    return {
        "Sex": sex,
        "Fare": fare,
        "categorie": categorie
    }


def faire_prediction(passager):
    """
    Make a prediction for a passenger.

    Args:
        passager: Dictionary with Sex and Fare

    Returns:
        API response dictionary
    """
    try:
        data = {
            "Sex": passager["Sex"],
            "Fare": passager["Fare"]
        }

        response = requests.post(
            f"{API_URL}/predict",
            json=data,
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}


def main():
    """
    Run 10 prediction simulations.
    """
    print("=" * 70)
    print("SIMULATION DE 10 PREDICTIONS ALEATOIRES")
    print("=" * 70)
    print()

    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Erreur: L'API n'est pas accessible (status {response.status_code})")
            print("Assurez-vous que Docker est lance: docker-compose up -d")
            return
    except Exception as e:
        print(f"❌ Erreur: Impossible de se connecter a l'API")
        print(f"   {e}")
        print("Assurez-vous que Docker est lance: docker-compose up -d")
        return

    print("✅ API accessible")
    print()

    stats = {
        "total": 0,
        "survived": 0,
        "died": 0,
        "hommes": 0,
        "femmes": 0,
        "prix_bas": 0,
        "prix_haut": 0
    }

    for i in range(1, 11):
        passager = generer_passager_aleatoire()

        print(f"🎲 Prediction {i}/10")
        print(f"   Sexe: {passager['Sex']}")
        print(f"   Prix: {passager['Fare']}€ ({passager['categorie']})")

        resultat = faire_prediction(passager)

        if "error" in resultat:
            print(f"   ❌ Erreur: {resultat['error']}")
        else:
            print(f"   ✅ Prediction: {resultat['prediction']}")

            stats["total"] += 1
            if resultat["prediction"] == "Survived":
                stats["survived"] += 1
            else:
                stats["died"] += 1

            if passager["Sex"] == "M":
                stats["hommes"] += 1
            else:
                stats["femmes"] += 1

            if passager["categorie"] == "Prix bas":
                stats["prix_bas"] += 1
            else:
                stats["prix_haut"] += 1

        print()
        time.sleep(0.5)

    print("=" * 70)
    print("STATISTIQUES")
    print("=" * 70)
    print()
    print(f"Total de predictions: {stats['total']}")
    print()

    if stats['total'] > 0:
        print(f"Predictions:")
        print(f"  - Survived: {stats['survived']} ({stats['survived']/stats['total']*100:.1f}%)")
        print(f"  - Died:     {stats['died']} ({stats['died']/stats['total']*100:.1f}%)")
        print()
        print(f"Sexe:")
        print(f"  - Hommes: {stats['hommes']}")
        print(f"  - Femmes: {stats['femmes']}")
        print()
        print(f"Prix:")
        print(f"  - Prix bas:  {stats['prix_bas']}")
        print(f"  - Prix haut: {stats['prix_haut']}")
        print()
    else:
        print("❌ Aucune prediction reussie")
        print()
    print("=" * 70)
    print("Pour voir les metriques dans Grafana:")
    print("  http://localhost:3000")
    print()
    print("Pour voir les metriques Prometheus:")
    print("  http://localhost:8000/metrics")
    print("=" * 70)


if __name__ == "__main__":
    main()