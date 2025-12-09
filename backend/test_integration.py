"""
Tests de vérification de l'intégration backend-frontend
Execute ce script pour vérifier que tous les endpoints fonctionnent correctement
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:5000/api"

def print_test(name, success, details=""):
    """Affiche le résultat d'un test"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")
    print()

def test_get_auctions():
    """Test 1: Récupérer la liste des enchères"""
    try:
        response = requests.get(f"{BASE_URL}/auctions")
        success = response.status_code == 200 and "auctions" in response.json()
        auctions = response.json().get("auctions", [])
        print_test(
            "GET /api/auctions",
            success,
            f"Trouvé {len(auctions)} enchères"
        )
        return auctions[0]["id"] if auctions else None
    except Exception as e:
        print_test("GET /api/auctions", False, str(e))
        return None

def test_get_auction_detail(auction_id):
    """Test 2: Récupérer les détails d'une enchère"""
    try:
        response = requests.get(f"{BASE_URL}/auctions/{auction_id}")
        data = response.json()
        success = (
            response.status_code == 200 and
            "id" in data and
            "bids_count" in data and  # ✅ Nouveau champ
            "product" in data
        )
        print_test(
            f"GET /api/auctions/{auction_id}",
            success,
            f"Enchère: {data.get('product', {}).get('title', 'N/A')}, "
            f"Prix actuel: {data.get('current_price')}€, "
            f"Nombre d'enchères: {data.get('bids_count', 0)}"
        )
        return success
    except Exception as e:
        print_test(f"GET /api/auctions/{auction_id}", False, str(e))
        return False

def test_get_auction_bids(auction_id):
    """Test 3: Récupérer l'historique des enchères (NOUVEAU ENDPOINT)"""
    try:
        response = requests.get(f"{BASE_URL}/auctions/{auction_id}/bids")
        data = response.json()
        success = response.status_code == 200 and "bids" in data
        bids = data.get("bids", [])
        
        # Vérifier la structure des données
        if bids and len(bids) > 0:
            first_bid = bids[0]
            has_correct_structure = (
                "id" in first_bid and
                "amount" in first_bid and
                "timestamp" in first_bid and
                "user" in first_bid and
                "username" in first_bid["user"]
            )
            success = success and has_correct_structure
        
        print_test(
            f"GET /api/auctions/{auction_id}/bids",
            success,
            f"Trouvé {len(bids)} enchères dans l'historique"
        )
        return success
    except Exception as e:
        print_test(f"GET /api/auctions/{auction_id}/bids", False, str(e))
        return False

def test_register_and_login():
    """Test 4: Créer un compte et se connecter"""
    try:
        # Générer un nom d'utilisateur unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        username = f"testuser_{timestamp}"
        password = "Test123!"
        
        # Inscription
        register_data = {
            "username": username,
            "email": f"{username}@test.com",
            "password": password
        }
        register_response = requests.post(f"{BASE_URL}/register", json=register_data)
        
        # Connexion
        login_data = {
            "username": username,
            "password": password
        }
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        login_result = login_response.json()
        
        success = (
            register_response.status_code == 201 and
            login_response.status_code == 200 and
            "token" in login_result
        )
        
        print_test(
            "POST /api/register + POST /api/login",
            success,
            f"Utilisateur créé: {username}, Token reçu: {login_result.get('token', 'N/A')[:20]}..."
        )
        
        return login_result.get("token") if success else None
    except Exception as e:
        print_test("POST /api/register + POST /api/login", False, str(e))
        return None

def test_place_bid(auction_id, token):
    """Test 5: Placer une enchère (avec authentification)"""
    try:
        # Récupérer d'abord les infos de l'enchère
        auction_response = requests.get(f"{BASE_URL}/auctions/{auction_id}")
        auction = auction_response.json()
        
        # Calculer le montant minimum
        current_price = auction.get("current_price", auction.get("start_price", 0))
        min_increment = auction.get("min_increment", 50)
        bid_amount = current_price + min_increment
        
        # Placer l'enchère
        headers = {"Authorization": f"Bearer {token}"}
        bid_data = {"amount": bid_amount}
        response = requests.post(
            f"{BASE_URL}/auctions/{auction_id}/bids",
            json=bid_data,
            headers=headers
        )
        
        success = response.status_code == 201
        
        print_test(
            f"POST /api/auctions/{auction_id}/bids",
            success,
            f"Enchère placée: {bid_amount}€ (anciennement {current_price}€)"
        )
        
        return success
    except Exception as e:
        print_test(f"POST /api/auctions/{auction_id}/bids", False, str(e))
        return False

def test_verify_bids_count_updated(auction_id, initial_count):
    """Test 6: Vérifier que bids_count est bien mis à jour"""
    try:
        response = requests.get(f"{BASE_URL}/auctions/{auction_id}")
        data = response.json()
        new_count = data.get("bids_count", 0)
        
        success = new_count == initial_count + 1
        
        print_test(
            "Vérification bids_count après enchère",
            success,
            f"Nombre d'enchères: {initial_count} → {new_count}"
        )
        
        return success
    except Exception as e:
        print_test("Vérification bids_count après enchère", False, str(e))
        return False

def main():
    print("=" * 60)
    print("🧪 TESTS D'INTÉGRATION BACKEND-FRONTEND")
    print("=" * 60)
    print()
    
    # Test 1: Liste des enchères
    auction_id = test_get_auctions()
    if not auction_id:
        print("❌ Impossible de continuer sans enchère disponible")
        return
    
    # Test 2: Détails d'une enchère
    test_get_auction_detail(auction_id)
    
    # Test 3: Historique des enchères (NOUVEAU)
    test_get_auction_bids(auction_id)
    
    # Sauvegarder le compte initial d'enchères
    response = requests.get(f"{BASE_URL}/auctions/{auction_id}")
    initial_bids_count = response.json().get("bids_count", 0)
    
    # Test 4: Inscription et connexion
    token = test_register_and_login()
    if not token:
        print("⚠️ Tests d'authentification ignorés (déjà testé précédemment ?)")
    else:
        # Test 5: Placer une enchère
        if test_place_bid(auction_id, token):
            # Test 6: Vérifier la mise à jour
            test_verify_bids_count_updated(auction_id, initial_bids_count)
    
    print("=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)
    print()
    print("📝 Pour tester les WebSockets:")
    print("   1. Ouvrez http://localhost:5173 dans 2 onglets différents")
    print("   2. Naviguez vers la même enchère dans les 2 onglets")
    print("   3. Placez une enchère dans l'onglet 1")
    print("   4. Vérifiez que l'onglet 2 reçoit la mise à jour instantanément")
    print()

if __name__ == "__main__":
    main()
