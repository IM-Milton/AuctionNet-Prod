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
          <span class="balance-label">Solde du compte</span>
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
  { id: "participations", label: "Participations" },
  { id: "myAuctions", label: "Mes enchères" },
  { id: "won", label: "Gagnées" },
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

  // Gérer différents types d'images : URLs absolues, chemins media, Data URLs
  let imageUrl = "/assets/images/placeholder.jpg";

  if (images.length > 0 && images[0]) {
    const img = images[0];
    // Si c'est une Data URL (base64) ou une URL complète, l'utiliser directement
    if (
      img.startsWith("data:") ||
      img.startsWith("http://") ||
      img.startsWith("https://")
    ) {
      imageUrl = img;
    } else {
      // Sinon, c'est un chemin media à transformer
      imageUrl = toMediaUrl(img);
    }
  }

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
    return { text: "Remportée", class: "won" };
  }

  if (auction.status === "closed" || auction.status === "completed") {
    return { text: "Terminée", class: "ended" };
  }

  if (auction.status === "running" || auction.status === "active") {
    return { text: "En cours", class: "active" };
  }

  return { text: "Planifiée", class: "scheduled" };
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

<style scoped src="./css/ProfileView.css"></style>
