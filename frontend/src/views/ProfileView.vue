<template>
  <div class="profile-page">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Chargement de votre profil...</p>
    </div>

    <div v-else-if="!currentUser" class="loading">
      <p>Redirection...</p>
    </div>

    <div v-else>
      <div class="page-header">
        <div class="user-info">
          <div class="avatar">👤</div>
          <div>
            <h1>Mon Profil</h1>
            <p class="username">{{ currentUser.name }}</p>
          </div>
        </div>

        <div class="balance-card">
          <span class="balance-label">💰 Solde du compte</span>
          <span class="balance-amount"
            >{{ currentUser.balance.toFixed(2) }} €</span
          >
          <button @click="showCreditModal = true" class="btn-credit">
            + Créditer mon compte
          </button>
        </div>
      </div>

      <!-- Statistiques -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">🎯</span>
          <span class="stat-value">{{ myParticipations.length }}</span>
          <span class="stat-label">Enchères participées</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">💰</span>
          <span class="stat-value">{{ myAuctions.length }}</span>
          <span class="stat-label">Enchères créées</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🏆</span>
          <span class="stat-value">{{ wonAuctions.length }}</span>
          <span class="stat-label">Enchères gagnées</span>
        </div>
      </div>

      <!-- Onglets -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span>{{ tab.icon }}</span>
          {{ tab.label }}
          <span class="tab-count">{{ getTabCount(tab.id) }}</span>
        </button>
      </div>

      <!-- Contenu des onglets -->
      <div class="tab-content">
        <!-- Enchères participées -->
        <div v-if="activeTab === 'participations'" class="auctions-list">
          <div v-if="myParticipations.length === 0" class="empty-state">
            <span class="empty-icon">🎯</span>
            <h3>Aucune participation</h3>
            <p>Vous n'avez participé à aucune enchère pour le moment</p>
            <router-link to="/" class="btn btn-primary"
              >Découvrir les enchères</router-link
            >
          </div>

          <div
            v-else
            class="auction-card"
            v-for="auction in myParticipations"
            :key="auction.id"
          >
            <div class="auction-image">
              <img :src="auction.imageUrl" :alt="auction.title" />
              <div
                class="auction-status"
                :class="getAuctionStatus(auction).class"
              >
                {{ getAuctionStatus(auction).text }}
              </div>
            </div>

            <div class="auction-details">
              <h3>{{ auction.title }}</h3>
              <p class="auction-category">
                {{ getCategoryLabel(auction.category) }}
              </p>

              <div class="auction-info">
                <div class="info-item">
                  <span class="label">Votre enchère :</span>
                  <span class="value">{{ auction.myBid }} €</span>
                </div>
                <div class="info-item">
                  <span class="label">Enchère actuelle :</span>
                  <span class="value highlight"
                    >{{ auction.currentBid }} €</span
                  >
                </div>
                <div class="info-item">
                  <span class="label">Fin :</span>
                  <span class="value">{{ formatDate(auction.endDate) }}</span>
                </div>
              </div>
            </div>

            <div class="auction-actions">
              <router-link
                :to="`/auction/${auction.id}`"
                class="btn btn-outline"
              >
                Voir détails
              </router-link>
            </div>
          </div>
        </div>

        <!-- Mes enchères créées -->
        <div v-if="activeTab === 'myAuctions'" class="auctions-list">
          <div v-if="myAuctions.length === 0" class="empty-state">
            <span class="empty-icon">💰</span>
            <h3>Aucune enchère créée</h3>
            <p>Vous n'avez pas encore créé d'enchère</p>
            <router-link to="/sell" class="btn btn-primary"
              >Créer une enchère</router-link
            >
          </div>

          <div
            v-else
            class="auction-card"
            v-for="auction in myAuctions"
            :key="auction.id"
          >
            <div class="auction-image">
              <img :src="auction.imageUrl" :alt="auction.title" />
              <div
                class="auction-status"
                :class="getAuctionStatus(auction).class"
              >
                {{ getAuctionStatus(auction).text }}
              </div>
            </div>

            <div class="auction-details">
              <h3>{{ auction.title }}</h3>
              <p class="auction-category">
                {{ getCategoryLabel(auction.category) }}
              </p>

              <div class="auction-info">
                <div class="info-item">
                  <span class="label">Prix de départ :</span>
                  <span class="value">{{ auction.startPrice }} €</span>
                </div>
                <div class="info-item">
                  <span class="label">Enchère actuelle :</span>
                  <span class="value highlight"
                    >{{ auction.currentBid }} €</span
                  >
                </div>
                <div class="info-item">
                  <span class="label">Nombre d'enchères :</span>
                  <span class="value">{{ auction.bidsCount }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Fin :</span>
                  <span class="value">{{ formatDate(auction.endDate) }}</span>
                </div>

                <div v-if="auction.winner" class="winner-info">
                  <span class="label">🏆 Gagnant :</span>
                  <span class="value winner">{{ auction.winner }}</span>
                </div>
              </div>
            </div>

            <div class="auction-actions">
              <router-link
                :to="`/auction/${auction.id}`"
                class="btn btn-outline"
              >
                Voir détails
              </router-link>
            </div>
          </div>
        </div>

        <!-- Enchères gagnées -->
        <div v-if="activeTab === 'won'" class="auctions-list">
          <div v-if="wonAuctions.length === 0" class="empty-state">
            <span class="empty-icon">🏆</span>
            <h3>Aucune enchère gagnée</h3>
            <p>Vous n'avez pas encore remporté d'enchère</p>
            <router-link to="/" class="btn btn-primary"
              >Participer aux enchères</router-link
            >
          </div>

          <div
            v-else
            class="auction-card"
            v-for="auction in wonAuctions"
            :key="auction.id"
          >
            <div class="auction-image">
              <img :src="auction.imageUrl" :alt="auction.title" />
              <div class="auction-status won">🏆 Remportée</div>
            </div>

            <div class="auction-details">
              <h3>{{ auction.title }}</h3>
              <p class="auction-category">
                {{ getCategoryLabel(auction.category) }}
              </p>

              <div class="auction-info">
                <div class="info-item">
                  <span class="label">Prix remporté :</span>
                  <span class="value highlight"
                    >{{ auction.winningBid }} €</span
                  >
                </div>
                <div class="info-item">
                  <span class="label">Date de fin :</span>
                  <span class="value">{{ formatDate(auction.endDate) }}</span>
                </div>
              </div>
            </div>

            <div class="auction-actions">
              <button class="btn btn-primary">Contacter le vendeur</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de crédit -->
    <div v-if="showCreditModal" class="modal-overlay" @click="closeCreditModal">
      <div class="modal-content" @click.stop>
        <h2>Créditer mon compte</h2>
        <p class="modal-description">
          Ajoutez des fonds à votre compte pour participer aux enchères
        </p>

        <div class="form-group">
          <label for="creditAmount">Montant à créditer (€)</label>
          <input
            id="creditAmount"
            type="number"
            v-model="creditAmount"
            min="1"
            max="10000"
            step="0.01"
            placeholder="Entrez le montant"
            class="input-field"
          />
          <p class="input-hint">Maximum : 10 000 € par transaction</p>
        </div>

        <div v-if="creditError" class="error-message">
          {{ creditError }}
        </div>

        <div v-if="creditSuccess" class="success-message">
          {{ creditSuccess }}
        </div>

        <div class="modal-actions">
          <button
            @click="closeCreditModal"
            class="btn btn-secondary"
            :disabled="creditLoading"
          >
            Annuler
          </button>
          <button
            @click="handleCredit"
            class="btn btn-primary"
            :disabled="creditLoading"
          >
            <span v-if="creditLoading">Traitement...</span>
            <span v-else>Créditer {{ creditAmount || 0 }} €</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  getMyProfile,
  getMyParticipations,
  getMyAuctions,
  getMyWonAuctions,
  creditAccount,
} from "@/services/profileService";
import { toMediaUrl } from "@/services/media";
import { useAuctionEvents } from "@/composables/useAuctionEvents";

const router = useRouter();
const { onAuctionCreated, onBidPlaced } = useAuctionEvents();
const activeTab = ref("participations");
const loading = ref(true);

const tabs = [
  { id: "participations", icon: "🎯", label: "Participations" },
  { id: "myAuctions", icon: "💰", label: "Mes enchères" },
  { id: "won", icon: "🏆", label: "Gagnées" },
];

// Données utilisateur depuis le backend
const currentUser = ref(null);
const myParticipations = ref([]);
const myAuctions = ref([]);
const wonAuctions = ref([]);

// État du modal de crédit
const showCreditModal = ref(false);
const creditAmount = ref("");
const creditLoading = ref(false);
const creditError = ref("");
const creditSuccess = ref("");

// Variable pour stocker les fonctions de désabonnement
let unsubscribeAuctionCreated = null;
let unsubscribeBidPlaced = null;

// Charger les données du profil
async function loadProfileData() {
  try {
    loading.value = true;

    // Récupérer les données du profil
    const [profile, participations, auctions, won] = await Promise.all([
      getMyProfile(),
      getMyParticipations(),
      getMyAuctions(),
      getMyWonAuctions(),
    ]);

    currentUser.value = {
      name: profile.email?.split("@")[0] || "Utilisateur",
      email: profile.email,
      balance: profile.balance || 0,
      held: profile.held || 0,
    };

    myParticipations.value = participations.map(mapAuction);
    myAuctions.value = auctions.map(mapAuction);
    wonAuctions.value = won.map(mapAuction);

    loading.value = false;
  } catch (error) {
    console.error("Error loading profile:", error);
    // Si erreur d'authentification, rediriger vers login
    router.push("/login");
  }
}

// Fonction pour fermer le modal
function closeCreditModal() {
  showCreditModal.value = false;
  creditAmount.value = "";
  creditError.value = "";
  creditSuccess.value = "";
}

// Fonction pour créditer le compte
async function handleCredit() {
  creditError.value = "";
  creditSuccess.value = "";

  // Validation
  const amount = parseFloat(creditAmount.value);
  if (!amount || amount <= 0) {
    creditError.value = "Veuillez entrer un montant valide";
    return;
  }
  if (amount > 10000) {
    creditError.value = "Le montant maximum est de 10 000 €";
    return;
  }

  try {
    creditLoading.value = true;
    const result = await creditAccount(amount);

    // Mettre à jour le solde localement
    currentUser.value.balance = result.new_balance;

    creditSuccess.value = `Votre compte a été crédité de ${amount.toFixed(
      2
    )} €. Nouveau solde : ${result.new_balance.toFixed(2)} €`;

    // Fermer le modal après 2 secondes
    setTimeout(() => {
      closeCreditModal();
    }, 2000);
  } catch (error) {
    console.error("Error crediting account:", error);
    creditError.value = error.message || "Erreur lors du crédit du compte";
  } finally {
    creditLoading.value = false;
  }
}

onMounted(async () => {
  await loadProfileData();

  // Écouter les événements de création d'enchère
  unsubscribeAuctionCreated = onAuctionCreated(async (auctionData) => {
    console.log(
      "🔄 ProfileView: Nouvelle enchère créée, rechargement...",
      auctionData
    );
    await loadProfileData();
  });

  // Écouter les événements de placement d'enchère
  unsubscribeBidPlaced = onBidPlaced(async (bidData) => {
    console.log(
      "🔄 ProfileView: Nouvelle enchère placée, rechargement...",
      bidData
    );
    await loadProfileData();
  });
});

// Nettoyer les écouteurs quand le composant est détruit
onUnmounted(() => {
  if (unsubscribeAuctionCreated) {
    unsubscribeAuctionCreated();
  }
  if (unsubscribeBidPlaced) {
    unsubscribeBidPlaced();
  }
});

// Mapper les données du backend vers le format attendu par la vue
function mapAuction(auction) {
  const product = auction.product || {};
  const images = product.images || [];
  const imageUrl =
    images.length > 0
      ? toMediaUrl(images[0])
      : "/assets/images/placeholder.jpg";

  return {
    id: auction.id,
    title: product.title || "Sans titre",
    category: product.category || "other",
    imageUrl,
    myBid: auction.myBid || 0,
    currentBid: auction.current_price || auction.start_price || 0,
    startPrice: auction.start_price || 0,
    endDate: auction.end_at || auction.endDate,
    bidsCount: auction.bids_count || 0,
    status: auction.status,
    winner: auction.winner_username,
    winningBid: auction.current_price || auction.start_price,
  };
}

function getTabCount(tabId) {
  switch (tabId) {
    case "participations":
      return myParticipations.value.length;
    case "myAuctions":
      return myAuctions.value.length;
    case "won":
      return wonAuctions.value.length;
    default:
      return 0;
  }
}

function getAuctionStatus(auction) {
  if (auction.status === "won" || auction.winner) {
    return { text: "🏆 Remportée", class: "won" };
  }

  if (auction.status === "closed" || auction.status === "completed") {
    return { text: "⏱️ Terminée", class: "ended" };
  }

  if (auction.status === "running" || auction.status === "active") {
    return { text: "🔥 En cours", class: "active" };
  }

  return { text: "� Planifiée", class: "scheduled" };
}

function getCategoryLabel(category) {
  const labels = {
    electronics: "📱 Électronique",
    fashion: "👗 Mode",
    home: "🏠 Maison",
    sports: "⚽ Sport",
    art: "🎨 Art",
    vehicles: "🚗 Véhicules",
    vehicule: "🚗 Véhicules",
    other: "📦 Autre",
  };
  return labels[category] || category;
}

function formatDate(dateString) {
  if (!dateString) return "Date inconnue";
  const date = new Date(dateString);
  return date.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading {
  text-align: center;
  padding: 4rem;
  color: white;
  font-size: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
}

.page-header h1 {
  margin: 0 0 0.25rem 0;
  color: #333;
  font-size: 2rem;
}

.username {
  margin: 0;
  color: #666;
  font-size: 1.1rem;
}

.balance-card {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border-radius: 12px;
  color: white;
}

.balance-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.balance-amount {
  font-size: 2rem;
  font-weight: 700;
}

.btn-credit {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #43e97b;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-credit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  color: #666;
  font-size: 0.95rem;
  text-align: center;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab:hover {
  background: #f5f5f5;
}

.tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.tab-count {
  padding: 0.25rem 0.75rem;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 0.85rem;
}

.tab.active .tab-count {
  background: rgba(255, 255, 255, 0.2);
}

.tab-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.auctions-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 5rem;
  display: block;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 2rem;
}

.auction-card {
  display: grid;
  grid-template-columns: 200px 1fr auto;
  gap: 1.5rem;
  padding: 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.auction-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.auction-image {
  position: relative;
  width: 200px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
}

.auction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.auction-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  backdrop-filter: blur(10px);
}

.auction-status.active {
  background: rgba(67, 233, 123, 0.95);
  color: white;
}

.auction-status.ended {
  background: rgba(158, 158, 158, 0.95);
  color: white;
}

.auction-status.won {
  background: rgba(255, 193, 7, 0.95);
  color: #333;
}

.auction-details h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.3rem;
}

.auction-category {
  color: #667eea;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.auction-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.info-item .label {
  color: #666;
  font-size: 0.95rem;
}

.info-item .value {
  font-weight: 600;
  color: #333;
}

.info-item .value.highlight {
  color: #667eea;
  font-size: 1.1rem;
}

.info-item .value.winner {
  color: #f59e0b;
}

.winner-info {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #fff3cd;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
}

.auction-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.75rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-content h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.8rem;
}

.modal-description {
  color: #666;
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 600;
}

.input-field {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
}

.input-hint {
  margin: 0.5rem 0 0 0;
  color: #999;
  font-size: 0.85rem;
}

.error-message {
  padding: 1rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.success-message {
  padding: 1rem;
  background: #efe;
  border: 1px solid #cfc;
  border-radius: 8px;
  color: #3a3;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-secondary {
  background: #e0e0e0;
  color: #666;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1.5rem;
  }

  .balance-card {
    width: 100%;
    align-items: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .tabs {
    flex-direction: column;
  }

  .auction-card {
    grid-template-columns: 1fr;
  }

  .auction-image {
    width: 100%;
    height: 200px;
  }

  .auction-actions {
    flex-direction: row;
  }
}
</style>
