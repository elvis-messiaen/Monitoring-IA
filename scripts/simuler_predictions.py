"""
Script pour simuler 10 predictions aleatoires pour tester le systeme de monitoring.
Genere des combinaisons aleatoires de sexe (M/F) et prix (bas/haut).
"""

import requests
import random
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# Plages de prix
PRIX_BAS = (5.0, 30.0)    # Prix bas: entre 5 et 30
PRIX_HAUT = (50.0, 150.0)  # Prix haut: entre 50 et 150

def generer_passager_aleatoire():
    """
    Genere un passager aleatoire avec sexe et prix.

    Returns:
        dict: Passager avec Sex et Fare
    """
    # Choix aleatoire du sexe
    sex = random.choice(['M', 'F'])

    # Choix aleatoire entre prix bas et prix haut
    if random.random() < 0.5:
        # Prix bas
        fare = round(random.uniform(*PRIX_BAS), 2)
        categorie = "Prix bas"
    else:
        # Prix haut
        fare = round(random.uniform(*PRIX_HAUT), 2)
        categorie = "Prix haut"

    return {
        "Sex": sex,
        "Fare": fare,
        "categorie": categorie
    }

def faire_prediction(passager):
    """
    Fait une prediction pour un passager.

    Args:
        passager: dict avec Sex et Fare

    Returns:
        dict: Reponse de l'API
    """
    try:
        # Enlever la categorie avant d'envoyer a l'API
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
    Lance 10 simulations de predictions.
    """
    print("=" * 70)
    print("SIMULATION DE 10 PREDICTIONS ALEATOIRES")
    print("=" * 70)
    print()

    # Verifier que l'API est accessible
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

    # Statistiques
    stats = {
        "total": 0,
        "survived": 0,
        "died": 0,
        "hommes": 0,
        "femmes": 0,
        "prix_bas": 0,
        "prix_haut": 0
    }

    # Lancer 10 predictions
    for i in range(1, 11):
        # Generer un passager aleatoire
        passager = generer_passager_aleatoire()

        # Afficher les details
        print(f"🎲 Prediction {i}/10")
        print(f"   Sexe: {passager['Sex']}")
        print(f"   Prix: {passager['Fare']}€ ({passager['categorie']})")

        # Faire la prediction
        resultat = faire_prediction(passager)

        if "error" in resultat:
            print(f"   ❌ Erreur: {resultat['error']}")
        else:
            print(f"   ✅ Prediction: {resultat['prediction']}")

            # Mettre a jour les statistiques
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

        # Pause de 0.5 seconde entre chaque prediction
        time.sleep(0.5)

    # Afficher les statistiques
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