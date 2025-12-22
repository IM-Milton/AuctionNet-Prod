<template>
  <!-- Loading -->
  <div v-if="loading" class="loading-container">
    <div class="spinner">⏳</div>
    <p>Chargement de l'enchère...</p>
  </div>

  <div class="auction-detail" v-else-if="auction">
    <div class="header-controls">
      <router-link to="/" class="btn-back"> ← Retour </router-link>

      <!-- Bouton supprimer (visible uniquement pour le créateur) -->
      <button
        v-if="
          isCreator &&
          auction.status === 'scheduled' &&
          auction.bids_count === 0
        "
        @click="confirmDelete"
        class="btn-delete"
        :disabled="deleteLoading"
      >
        {{ deleteLoading ? "Suppression..." : "Supprimer" }}
      </button>

      <!-- Indicateur WebSocket -->
      <div
        class="ws-indicator"
        :class="{
          'ws-connected': wsConnected,
          'ws-disconnected': !wsConnected,
        }"
      >
        <span class="ws-dot"></span>
        <span class="ws-text">{{ wsStatus }}</span>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="errorMessage" class="alert alert-error">
      ❌ {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <div class="detail-content">
      <div class="image-section">
        <img
          :src="getImageUrl(auction.product?.images)"
          :alt="auction.product?.title || auction.title"
          class="main-image"
        />
      </div>

      <div class="info-section">
        <div class="header">
          <h1>{{ auction.product?.title || auction.title }}</h1>
          <span
            class="badge"
            :class="{
              'badge-success': auction.status === 'running',
              'badge-warning': auction.status === 'scheduled',
              'badge-secondary': auction.status === 'closed',
            }"
          >
            {{ getStatusLabel(auction.status) }}
          </span>
        </div>

        <div class="price-section">
          <div class="current-price">
            <span class="label">Prix actuel</span>
            <span class="amount"
              >{{ auction.current_price || auction.start_price }} €</span
            >
          </div>
          <div class="stats">
            <div class="stat-item">
              <span>👥 {{ auction.bids_count || 0 }} enchères</span>
            </div>
            <div class="stat-item">
              <span>Prix de départ: {{ auction.start_price }} €</span>
            </div>
          </div>
        </div>

        <div
          class="timer-section"
          v-if="auction.status === 'running' && auction.end_at"
        >
          <div class="timer-label">⏰ Temps restant</div>
          <div class="countdown">
            <div class="time-unit">
              <span class="time-value">{{ timeRemaining.days }}</span>
              <span class="time-label">jours</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeRemaining.hours }}</span>
              <span class="time-label">heures</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeRemaining.minutes }}</span>
              <span class="time-label">minutes</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeRemaining.seconds }}</span>
              <span class="time-label">secondes</span>
            </div>
          </div>
        </div>

        <div
          class="timer-section"
          v-else-if="auction.status === 'scheduled' && auction.start_at"
        >
          <div class="timer-label">🕐 Débute dans</div>
          <div class="countdown">
            <div class="time-unit">
              <span class="time-value">{{ timeUntilStart.days }}</span>
              <span class="time-label">jours</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeUntilStart.hours }}</span>
              <span class="time-label">heures</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeUntilStart.minutes }}</span>
              <span class="time-label">minutes</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ timeUntilStart.seconds }}</span>
              <span class="time-label">secondes</span>
            </div>
          </div>
        </div>

        <div
          class="timer-section closed"
          v-else-if="auction.status === 'closed'"
        >
          <div class="timer-label">Enchère terminée</div>
          <div v-if="auction.winner_username" class="winner-info">
            <p>
              Gagnant: <strong>{{ auction.winner_username }}</strong>
            </p>
            <p>Prix final: {{ auction.current_price }} €</p>
          </div>
          <div v-else-if="auction.winner_id" class="winner-info">
            <p>Gagnant: {{ auction.winner_id }}</p>
            <p>Prix final: {{ auction.current_price }} €</p>
          </div>
        </div>

        <div class="bid-section" v-if="auction.status === 'running'">
          <label for="bid-amount">
            Votre enchère (minimum:
            {{
              (auction.current_price || auction.start_price) +
              auction.min_increment
            }}
            €)
          </label>
          <div class="bid-input-group">
            <input
              type="number"
              id="bid-amount"
              v-model="bidAmount"
              :min="
                (auction.current_price || auction.start_price) +
                auction.min_increment
              "
              :step="auction.min_increment"
              placeholder="Entrez votre enchère"
              :disabled="bidLoading || !currentUser"
            />
            <button
              class="btn btn-bid"
              @click="placeBid"
              :disabled="bidLoading || !currentUser"
            >
              <span v-if="bidLoading">⏳</span>
              <span v-else>💰</span>
              {{ bidLoading ? "Enchère en cours..." : "Enchérir" }}
            </button>
          </div>

          <div class="quick-bids">
            <button @click="quickBid(auction.min_increment)" class="btn-quick">
              +{{ auction.min_increment }} €
            </button>
            <button
              @click="quickBid(auction.min_increment * 2)"
              class="btn-quick"
            >
              +{{ auction.min_increment * 2 }} €
            </button>
            <button
              @click="quickBid(auction.min_increment * 5)"
              class="btn-quick"
            >
              +{{ auction.min_increment * 5 }} €
            </button>
          </div>

          <p v-if="!currentUser" class="warning-message">
            ⚠️ Vous devez être
            <router-link to="/login">connecté</router-link> pour enchérir
          </p>
        </div>

        <div class="bid-section disabled" v-else>
          <p class="info-message">
            {{
              auction.status === "scheduled"
                ? "L'enchère n'a pas encore commencé"
                : "L'enchère est terminée"
            }}
          </p>
        </div>

        <div class="description-section">
          <h3>Description</h3>
          <p>
            {{
              auction.product?.description || "Aucune description disponible."
            }}
          </p>

          <div class="product-details" v-if="auction.product">
            <h4>Détails du produit</h4>
            <ul>
              <li>
                <strong>Catégorie:</strong> {{ auction.product.category }}
              </li>
              <li>
                <strong>État:</strong>
                {{ auction.product.condition === "new" ? "Neuf" : "Occasion" }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Section Analytics et Leaderboard -->
    <div class="analytics-section">
      <div class="analytics-grid">
        <!-- Graphique d'évolution du prix -->
        <div class="analytics-card chart-card">
          <h2>
            📈 Évolution du prix
            <span class="live-indicator">🔴 EN DIRECT</span>
          </h2>
          <div class="chart-container">
            <div class="price-chart" ref="priceChartRef">
              <div class="chart-area">
                <!-- Ligne du graphique -->
                <svg viewBox="0 0 400 200" class="chart-svg">
                  <!-- Grille -->
                  <line
                    v-for="i in 5"
                    :key="`grid-${i}`"
                    :x1="0"
                    :y1="i * 40"
                    :x2="400"
                    :y2="i * 40"
                    class="grid-line"
                  />

                  <!-- Ligne de prix -->
                  <polyline
                    :points="priceChartPoints"
                    class="price-line"
                    fill="none"
                    stroke="#667eea"
                    stroke-width="3"
                  />

                  <!-- Points sur la ligne -->
                  <circle
                    v-for="(point, idx) in parsedPricePoints"
                    :key="`point-${idx}`"
                    :cx="point.x"
                    :cy="point.y"
                    r="4"
                    class="price-point"
                  />
                </svg>

                <!-- Labels des prix -->
                <div class="chart-labels">
                  <span class="label-y">{{ maxPrice }} €</span>
                  <span class="label-y"
                    >{{ Math.round((maxPrice + minPrice) / 2) }} €</span
                  >
                  <span class="label-y">{{ minPrice }} €</span>
                </div>
              </div>

              <!-- Statistiques sous le graphique -->
              <div class="chart-stats">
                <div class="stat">
                  <span class="stat-label">Prix actuel</span>
                  <span class="stat-value"
                    >{{
                      auction?.current_price || auction?.start_price
                    }}
                    €</span
                  >
                </div>
                <div class="stat">
                  <span class="stat-label">Hausse</span>
                  <span class="stat-value success">+{{ priceIncrease }} €</span>
                </div>
                <div class="stat">
                  <span class="stat-label">% Augmentation</span>
                  <span class="stat-value">{{ priceIncreasePercent }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Leaderboard des enchérisseurs -->
        <div class="analytics-card leaderboard-card">
          <h2>
            🏆 Classement des enchérisseurs
            <span class="live-indicator">🔴 EN DIRECT</span>
          </h2>

          <div class="leaderboard" v-if="leaderboard.length > 0">
            <div
              class="leaderboard-item"
              v-for="(leader, index) in leaderboard"
              :key="leader.userId"
              :class="{
                'top-1': index === 0,
                'top-2': index === 1,
                'top-3': index === 2,
                'current-user': isCurrentUser(leader.userId),
              }"
            >
              <div class="rank">
                <span v-if="index === 0" class="medal">🥇</span>
                <span v-else-if="index === 1" class="medal">🥈</span>
                <span v-else-if="index === 2" class="medal">🥉</span>
                <span v-else class="rank-number">#{{ index + 1 }}</span>
              </div>

              <div
                class="leader-avatar"
                :class="{ 'avatar-glow': index === 0 }"
              >
                {{ leader.username[0].toUpperCase() }}
              </div>

              <div class="leader-info">
                <div class="leader-name">
                  {{ leader.username }}
                  <span v-if="isCurrentUser(leader.userId)" class="you-badge"
                    >Vous</span
                  >
                  <span
                    v-if="index === 0 && auction?.status === 'running'"
                    class="winning-badge"
                    >En tête</span
                  >
                </div>
                <div class="leader-stats">
                  <span
                    class="bid-count"
                    :title="`${leader.bidCount} enchère(s) placée(s)`"
                  >
                    {{ leader.bidCount }} enchère{{
                      leader.bidCount > 1 ? "s" : ""
                    }}
                  </span>
                  <span class="separator">•</span>
                  <span
                    class="last-bid-time"
                    :title="formatFullDate(leader.lastBidTime)"
                  >
                    ⏰ {{ formatTimestamp(leader.lastBidTime) }}
                  </span>
                </div>
                <!-- Progression par rapport au prix de départ -->
                <div class="leader-progress">
                  <div class="progress-bar">
                    <div
                      class="progress-fill"
                      :style="{
                        width: calculateProgress(leader.currentBid) + '%',
                      }"
                    ></div>
                  </div>
                  <span class="progress-text"
                    >+{{ calculateIncrease(leader.currentBid) }}% depuis le
                    début</span
                  >
                </div>
              </div>

              <div class="leader-badge">
                <div class="highest-bid">{{ leader.currentBid }} €</div>
                <div class="badge-label">
                  {{ index === 0 ? "En tête" : "Enchère actuelle" }}
                </div>
                <!-- Afficher l'écart avec le leader -->
                <div v-if="index > 0" class="bid-difference">
                  -{{ leaderboard[0].currentBid - leader.currentBid }} €
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <div class="empty-leaderboard">
              <div class="empty-icon">🏆</div>
              <p>Aucun enchérisseur pour le moment</p>
              <span class="empty-hint"
                >Soyez le premier à placer une enchère !</span
              >
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Historique détaillé des enchères -->
    <div class="bid-history-detailed">
      <h2>Historique des enchères ({{ bidHistory.length }})</h2>

      <!-- Timeline -->
      <div class="bid-timeline" v-if="bidHistory.length > 0">
        <div
          class="timeline-item"
          v-for="(bid, index) in bidHistory"
          :key="bid.id"
        >
          <div class="timeline-marker">
            <div class="marker-dot"></div>
            <div class="marker-line" v-if="index < bidHistory.length - 1"></div>
          </div>

          <div class="timeline-content">
            <div class="timeline-header">
              <div class="user-info">
                <span class="user-avatar">{{
                  bid.user.username[0].toUpperCase()
                }}</span>
                <span class="user-name">{{ bid.user.username }}</span>
                <span class="bid-badge" v-if="index === 0">En tête</span>
              </div>
              <div class="time-info">
                {{ formatTimestamp(bid.timestamp) }}
              </div>
            </div>

            <div class="timeline-body">
              <div class="bid-amount-large">{{ bid.amount }} €</div>
              <div class="bid-meta">
                <span v-if="index < bidHistory.length - 1">
                  +{{ bid.amount - bidHistory[index + 1].amount }} € par rapport
                  à l'enchère précédente
                </span>
                <span v-else> Enchère de départ </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-bids-timeline">
        <div class="empty-state">
          <div class="empty-icon">🎯</div>
          <h3>Aucune enchère pour le moment</h3>
          <p>Soyez le premier à lancer les enchères !</p>
        </div>
      </div>
    </div>

    <!-- Section statistiques -->
    <div class="stats-section">
      <h2>Statistiques de l'enchère</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-number">{{ uniqueBidders }}</div>
            <div class="stat-label">Enchérisseurs uniques</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ bidHistory.length }}</div>
            <div class="stat-label">Total d'enchères</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ averageBid }} €</div>
            <div class="stat-label">Enchère moyenne</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ bidsPerHour }}</div>
            <div class="stat-label">Enchères/heure</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/services/api";
import websocketService from "@/services/websocket";
import { useAuctionEvents } from "@/composables/useAuctionEvents";

// Helper pour obtenir l'URL d'une image
function getImageUrl(images) {
  if (!images || images.length === 0) {
    return "https://via.placeholder.com/400x300?text=Pas+d%27image";
  }

  const img = images[0];
  if (!img) return "https://via.placeholder.com/400x300?text=Pas+d%27image";

  // Si c'est une Data URL (base64) ou une URL complète, l'utiliser directement
  if (
    img.startsWith("data:") ||
    img.startsWith("http://") ||
    img.startsWith("https://")
  ) {
    return img;
  }

  // Si c'est un chemin media, le transformer
  if (img.match(/^\/?media\//)) {
    const base = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
    return `${base.replace(/\/+$/, "")}/${img.replace(/^\//, "")}`;
  }

  return "https://via.placeholder.com/400x300?text=Pas+d%27image";
}

const route = useRoute();
const router = useRouter();
const auctionId = route.params.id;
const { notifyBidPlaced } = useAuctionEvents();

const auction = ref(null);
const bidAmount = ref(0);
const now = ref(new Date());
const loading = ref(true);
const bidLoading = ref(false);
const deleteLoading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const currentUser = ref(null);
const bidHistory = ref([]);
const similarAuctions = ref([]);
const autoRefreshInterval = ref(null);
const countdownInterval = ref(null);
const isMounted = ref(false);
const priceChartRef = ref(null);
const wsConnected = ref(false);
const wsStatus = ref("Déconnecté");

// Computed: Leaderboard des enchérisseurs (EN TEMPS RÉEL)
const leaderboard = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return [];

  const userStats = {};

  // Calculer les stats pour chaque utilisateur
  bidHistory.value.forEach((bid) => {
    const userId = bid.user.id;
    const username = bid.user.username;
    const bidTime = bid.timestamp;

    if (!userStats[userId]) {
      userStats[userId] = {
        userId,
        username,
        bidCount: 0,
        currentBid: 0, // Dernière enchère (la plus haute dans l'historique trié)
        lastBidTime: bidTime,
        allBids: [],
      };
    }

    userStats[userId].bidCount++;
    userStats[userId].allBids.push({ amount: bid.amount, time: bidTime });

    // La première enchère dans bidHistory est la plus récente (déjà trié par timestamp desc)
    // Donc on prend seulement la première occurrence de cet utilisateur
    if (userStats[userId].bidCount === 1) {
      userStats[userId].currentBid = bid.amount;
      userStats[userId].lastBidTime = bidTime;
    }
  });

  // Convertir en tableau et trier par enchère actuelle (la plus haute)
  const sorted = Object.values(userStats)
    .sort((a, b) => b.currentBid - a.currentBid)
    .slice(0, 10); // Top 10

  console.log("Leaderboard mis à jour:", sorted);
  return sorted;
});

// Computed: Total des enchères dans le leaderboard
const totalBidsInLeaderboard = computed(() => {
  return leaderboard.value.reduce((sum, leader) => sum + leader.bidCount, 0);
});

// Computed: Différence entre le 1er et le 2ème
const highestBidDifference = computed(() => {
  if (leaderboard.value.length < 2) return 0;
  return leaderboard.value[0].currentBid - leaderboard.value[1].currentBid;
});

// Fonctions helper pour le leaderboard
function isCurrentUser(userId) {
  return currentUser.value && currentUser.value.id === userId;
}

function calculateProgress(currentBid) {
  if (!auction.value) return 0;
  const startPrice = auction.value.start_price;
  const maxBid =
    leaderboard.value.length > 0 ? leaderboard.value[0].currentBid : currentBid;
  if (maxBid === startPrice) return 100;
  return Math.min(
    ((currentBid - startPrice) / (maxBid - startPrice)) * 100,
    100
  );
}

function calculateIncrease(currentBid) {
  if (!auction.value || !auction.value.start_price) return 0;
  return Math.round(
    ((currentBid - auction.value.start_price) / auction.value.start_price) * 100
  );
}

function formatFullDate(timestamp) {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return date.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Computed: Points du graphique de prix (EN TEMPS RÉEL)
const priceChartPoints = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    // Si pas d'enchère, afficher une ligne au prix de départ
    const startPrice = auction.value?.start_price || 100;
    return `0,100 400,100`;
  }

  // bidHistory est trié du plus récent au plus ancien
  // On inverse pour avoir du plus ancien au plus récent
  const sortedBids = [...bidHistory.value].reverse();
  const prices = sortedBids.map((b) => b.amount);

  // Ajouter le prix de départ au début
  if (auction.value?.start_price) {
    prices.unshift(auction.value.start_price);
  }

  const minPriceVal = Math.min(...prices);
  const maxPriceVal = Math.max(...prices);
  const priceRange = maxPriceVal - minPriceVal || 1;

  const points = prices
    .map((price, index) => {
      const x = (index / Math.max(prices.length - 1, 1)) * 400;
      const y = 180 - ((price - minPriceVal) / priceRange) * 160;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  console.log("📈 Graphique mis à jour:", {
    bidCount: bidHistory.value.length,
    prices: prices,
    points: points.substring(0, 50) + "...",
  });

  return points;
});

// Computed: Points parsés pour les cercles
const parsedPricePoints = computed(() => {
  if (!priceChartPoints.value) return [];
  return priceChartPoints.value.split(" ").map((point) => {
    const [x, y] = point.split(",").map(Number);
    return { x, y };
  });
});

// Computed: Prix min et max pour les labels
const minPrice = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    return auction.value?.start_price || 0;
  }
  const prices = bidHistory.value.map((b) => b.amount);
  if (auction.value?.start_price) {
    prices.push(auction.value.start_price);
  }
  return Math.min(...prices);
});

const maxPrice = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    return auction.value?.start_price || 0;
  }
  const prices = bidHistory.value.map((b) => b.amount);
  return Math.max(...prices);
});

// Computed: Augmentation du prix
const priceIncrease = computed(() => {
  if (!auction.value) return 0;
  const currentPrice = auction.value.current_price || auction.value.start_price;
  return currentPrice - auction.value.start_price;
});

const priceIncreasePercent = computed(() => {
  if (!auction.value || !auction.value.start_price) return 0;
  const increase = priceIncrease.value;
  return Math.round((increase / auction.value.start_price) * 100);
});

// Computed: Statistiques
const uniqueBidders = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0;
  const uniqueUsers = new Set(bidHistory.value.map((b) => b.user.id));
  return uniqueUsers.size;
});

const averageBid = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0;
  const total = bidHistory.value.reduce((sum, bid) => sum + bid.amount, 0);
  return Math.round(total / bidHistory.value.length);
});

const bidsPerHour = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0;

  // Calculer la durée depuis la première enchère
  const sortedBids = [...bidHistory.value].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  const firstBid = new Date(sortedBids[0].timestamp);
  const lastBid = new Date(sortedBids[sortedBids.length - 1].timestamp);
  const hoursDiff = (lastBid - firstBid) / (1000 * 60 * 60);

  if (hoursDiff < 0.01) return bidHistory.value.length; // Moins d'une minute

  return Math.round(bidHistory.value.length / hoursDiff);
});

// Charger les données de l'enchère
async function loadAuction() {
  // Ne rien faire si le composant n'est plus monté
  if (!isMounted.value) return;

  try {
    loading.value = true;
    const data = await api.getAuction(auctionId);

    // Vérifier à nouveau si le composant est toujours monté
    if (!isMounted.value) return;

    auction.value = data;

    // Initialiser le montant de l'enchère avec le minimum requis
    if (data.current_price) {
      bidAmount.value = data.current_price + (data.min_increment || 50);
    } else {
      bidAmount.value = data.start_price + (data.min_increment || 50);
    }

    // Charger l'historique des enchères (simulation pour le frontend)
    loadBidHistory();
  } catch (error) {
    console.error("Erreur lors du chargement de l'enchère:", error);
    errorMessage.value = "Impossible de charger l'enchère";
  } finally {
    loading.value = false;
  }
}

// Charger l'historique des enchères depuis le backend
async function loadBidHistory() {
  if (!auction.value || !isMounted.value) return;

  try {
    console.log("Chargement de l'historique des enchères...");
    const response = await fetch(`${api.baseURL}/auctions/${auctionId}/bids`);
    if (!response.ok) {
      console.warn("Impossible de charger l'historique des enchères");
      bidHistory.value = [];
      return;
    }

    const data = await response.json();
    if (!isMounted.value) return;

    // Force la réactivité en créant un nouveau tableau
    bidHistory.value = [...(data.bids || [])];

    console.log("Historique chargé:", {
      count: bidHistory.value.length,
      bids: bidHistory.value.map((b) => ({
        user: b.user.username,
        amount: b.amount,
      })),
    });
  } catch (error) {
    console.error("Erreur lors du chargement de l'historique:", error);
    bidHistory.value = [];
  }
}

// Placer une enchère
async function placeBid() {
  // Vérifier le token JWT
  const token = api.getToken();
  if (!token) {
    errorMessage.value =
      "Vous devez être connecté pour enchérir (token manquant)";
    setTimeout(() => router.push("/login"), 2000);
    return;
  }

  if (!currentUser.value) {
    errorMessage.value = "Vous devez être connecté pour enchérir";
    setTimeout(() => router.push("/login"), 2000);
    return;
  }

  // PREMIÈRE VÉRIFICATION : L'utilisateur ne peut pas enchérir sur sa propre enchère
  if (auction.value.seller_id === currentUser.value.id) {
    errorMessage.value =
      "🚫 Vous ne pouvez pas enchérir sur votre propre enchère !";
    return;
  }

  if (bidAmount.value <= auction.value.current_price) {
    errorMessage.value = `Votre enchère doit être supérieure à ${auction.value.current_price} €`;
    return;
  }

  const minRequired = auction.value.current_price + auction.value.min_increment;
  if (bidAmount.value < minRequired) {
    errorMessage.value = `L'enchère minimum est de ${minRequired} €`;
    return;
  }

  // Vérifier le solde disponible (balance - held)
  const userBalance = currentUser.value.balance || 0;
  const userHeld = currentUser.value.held || 0;
  const availableBalance = userBalance - userHeld;

  if (bidAmount.value > availableBalance) {
    errorMessage.value = `💰 Solde insuffisant ! Vous avez ${availableBalance.toFixed(
      2
    )} € disponibles (Solde: ${userBalance.toFixed(
      2
    )} €, En attente: ${userHeld.toFixed(2)} €). Votre enchère de ${
      bidAmount.value
    } € dépasse votre solde disponible.`;
    return;
  }

  try {
    bidLoading.value = true;
    errorMessage.value = "";

    console.log(
      "Placement enchère avec token:",
      token.substring(0, 20) + "..."
    );

    await api.placeBid(auctionId, bidAmount.value);

    successMessage.value = `Enchère de ${bidAmount.value} € placée avec succès !`;

    // Recharger les infos utilisateur pour mettre à jour le solde
    try {
      const userData = await api.getCurrentUser();
      currentUser.value = userData;
      console.log("Solde mis à jour:", userData.balance, "€");
    } catch (error) {
      console.error("Erreur lors de la mise à jour du profil:", error);
    }

    // Notifier les autres composants qu'une enchère a été placée
    notifyBidPlaced({
      auctionId,
      amount: bidAmount.value,
      userId: currentUser.value.id,
    });

    // Le WebSocket mettra à jour automatiquement les données
    // Pas besoin de recharger manuellement

    setTimeout(() => {
      if (isMounted.value) {
        successMessage.value = "";
      }
    }, 3000);
  } catch (error) {
    console.error("Erreur lors de l'enchère:", error);

    // Si erreur 401, rediriger vers login
    if (error.message && error.message.includes("401")) {
      errorMessage.value = "Session expirée. Veuillez vous reconnecter.";
      setTimeout(() => router.push("/login"), 2000);
    } else if (
      error.message &&
      error.message.toLowerCase().includes("insufficient")
    ) {
      // Message d'erreur spécifique pour les fonds insuffisants
      errorMessage.value = `Solde insuffisant ! ${error.message}`;
    } else {
      errorMessage.value = error.message || "Impossible de placer l'enchère";
    }
  } finally {
    bidLoading.value = false;
  }
}

// Enchère rapide
function quickBid(increment) {
  const currentPrice = auction.value.current_price || auction.value.start_price;
  bidAmount.value = currentPrice + increment;
}

// Vérifier si l'utilisateur actuel est le créateur de l'enchère
const isCreator = computed(() => {
  if (!currentUser.value || !auction.value || !auction.value.product) {
    return false;
  }
  return auction.value.product.owner_id === currentUser.value.id;
});

// Confirmer et supprimer l'enchère
async function confirmDelete() {
  if (
    !confirm(
      "⚠️ Êtes-vous sûr de vouloir supprimer cette enchère ? Cette action est irréversible."
    )
  ) {
    return;
  }

  try {
    deleteLoading.value = true;
    errorMessage.value = "";

    await api.deleteAuction(auctionId);

    successMessage.value = "Enchère supprimée avec succès !";

    // Rediriger vers la page d'accueil après 1 seconde
    setTimeout(() => {
      router.push("/");
    }, 1000);
  } catch (error) {
    console.error("Erreur lors de la suppression:", error);

    if (error.status === 400) {
      errorMessage.value =
        "❌ Impossible de supprimer une enchère avec des enchères existantes.";
    } else if (error.status === 403) {
      errorMessage.value =
        "❌ Vous n'êtes pas autorisé à supprimer cette enchère.";
    } else {
      errorMessage.value = error.message || "Impossible de supprimer l'enchère";
    }
  } finally {
    deleteLoading.value = false;
  }
}

// Calculer le temps restant
const timeRemaining = computed(() => {
  if (!auction.value || !auction.value.end_at) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }

  const endDate = new Date(auction.value.end_at);
  const diff = endDate - now.value;

  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }

  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000),
  };
});

// Calculer le temps avant le début
const timeUntilStart = computed(() => {
  if (!auction.value || !auction.value.start_at) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }

  const startDate = new Date(auction.value.start_at);
  const diff = startDate - now.value;

  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  }

  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000),
  };
});

// Formater une date
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Obtenir le label du statut
function getStatusLabel(status) {
  const labels = {
    scheduled: "Programmée",
    running: "En cours",
    closed: "Terminée",
  };
  return labels[status] || status;
}

// Formater le timestamp pour l'affichage
function formatTimestamp(timestamp) {
  if (!timestamp) return "";

  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "À l'instant";
  if (diffMins < 60)
    return `Il y a ${diffMins} minute${diffMins > 1 ? "s" : ""}`;
  if (diffHours < 24)
    return `Il y a ${diffHours} heure${diffHours > 1 ? "s" : ""}`;
  if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? "s" : ""}`;

  // Format date complète pour les enchères plus anciennes
  return date.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(async () => {
  isMounted.value = true;

  // Charger l'utilisateur connecté depuis l'API (pour avoir le solde à jour)
  try {
    const token = api.getToken();
    if (token) {
      const userData = await api.getCurrentUser();
      currentUser.value = userData;
      console.log("👤 Profil utilisateur chargé:", userData);
    }
  } catch (error) {
    console.error("Erreur lors du chargement du profil:", error);
    // Fallback sur localStorage si l'API échoue
    const user = localStorage.getItem("currentUser");
    if (user) {
      currentUser.value = JSON.parse(user);
    }
  }

  // Charger les données de l'enchère
  await loadAuction();

  // Mise à jour du compte à rebours chaque seconde
  countdownInterval.value = setInterval(() => {
    if (isMounted.value) {
      now.value = new Date();

      if (auction.value) {
        const currentTime = new Date().getTime();

        // Vérifier si une enchère "à venir" doit démarrer
        if (auction.value.status === "scheduled" && auction.value.start_at) {
          const startTime = new Date(auction.value.start_at).getTime();

          if (currentTime >= startTime) {
            console.log(
              "🚀 Enchère démarrée! Mise à jour du statut: scheduled -> running"
            );
            auction.value.status = "running";
            // Recharger depuis le backend pour synchroniser
            loadAuction();
          }
        }

        // Vérifier si une enchère "en cours" est expirée
        if (auction.value.status === "running" && auction.value.end_at) {
          const endTime = new Date(auction.value.end_at).getTime();

          if (currentTime >= endTime) {
            console.log(
              "⏰ Enchère expirée! Mise à jour du statut: running -> closed"
            );
            auction.value.status = "closed";
            // Recharger depuis le backend pour synchroniser
            loadAuction();
          }
        }
      }
    }
  }, 1000);

  // Connecter WebSocket et rejoindre la room de l'enchère
  try {
    console.log("\n" + "=".repeat(60));
    console.log("🔌 DÉMARRAGE DE LA CONNEXION WEBSOCKET");
    console.log("=".repeat(60) + "\n");
    wsStatus.value = "Connexion...";

    const socket = websocketService.connect();

    // Écouter les événements de connexion
    socket.on("connect", () => {
      console.log("\n" + "=".repeat(60));
      console.log("✅ WEBSOCKET CONNECTÉ AVEC SUCCÈS!");
      console.log(`🆔 Socket ID: ${socket.id}`);
      console.log("=".repeat(60) + "\n");
      wsConnected.value = true;
      wsStatus.value = "Connecté ✓";
    });

    socket.on("disconnect", (reason) => {
      console.log("\n" + "=".repeat(60));
      console.log("❌ WEBSOCKET DÉCONNECTÉ");
      console.log(`Raison: ${reason}`);
      console.log("=".repeat(60) + "\n");
      wsConnected.value = false;
      wsStatus.value = "Déconnecté";
    });

    await websocketService.joinAuction(auctionId);
    console.log("\n" + "=".repeat(60));
    console.log(`🛋️ REJOINT LA ROOM: auction_${auctionId}`);
    console.log("=".repeat(60) + "\n");

    // Écouter les nouvelles enchères en temps réel
    websocketService.onBidPlaced((data) => {
      if (!isMounted.value) return;

      console.log("\n" + "=".repeat(60));
      console.log("NOUVELLE ENCHÈRE REÇUE EN TEMPS RÉEL!");
      console.log("=".repeat(60));
      console.log("Données:", {
        auction_id: data.auction_id,
        current_price: data.auction?.current_price + " €",
        bids_count: data.auction?.bids_count,
        timestamp: new Date().toLocaleTimeString("fr-FR"),
      });
      console.log("=".repeat(60) + "\n");

      // Mettre à jour l'enchère avec les nouvelles données
      if (data.auction && data.auction_id === auctionId) {
        auction.value = data.auction;

        // Mettre à jour le montant minimum pour la prochaine enchère
        bidAmount.value =
          data.auction.current_price + (data.auction.min_increment || 50);

        // Recharger l'historique des enchères pour afficher la nouvelle enchère
        console.log("Rechargement de l'historique des enchères...");
        loadBidHistory();

        // Afficher une notification
        successMessage.value = `Nouvelle enchère: ${data.auction.current_price} €`;
        setTimeout(() => {
          if (isMounted.value) {
            successMessage.value = "";
          }
        }, 3000);
      }
    });

    console.log("\n" + "=".repeat(60));
    console.log("✅ WEBSOCKET CONFIGURÉ ET PRÊT");
    console.log("📡 En attente des mises à jour en temps réel...");
    console.log("=".repeat(60) + "\n");
  } catch (error) {
    console.error("\n" + "=".repeat(60));
    console.error("❌ ERREUR WEBSOCKET");
    console.error("=".repeat(60));
    console.error(error);
    console.error("=".repeat(60) + "\n");
    wsConnected.value = false;
    wsStatus.value = "Erreur";
    // En cas d'erreur, fallback sur le polling
    console.log("⚠️ Mode polling activé (rechargement toutes les 5s)");
    autoRefreshInterval.value = setInterval(async () => {
      if (isMounted.value && !bidLoading.value) {
        await loadAuction();
      }
    }, 5000);
  }
});

onBeforeUnmount(() => {
  console.log("🧹 AuctionView: Cleanup before unmount");

  // Marquer le composant comme démonté AVANT de nettoyer
  isMounted.value = false;

  // Quitter la room WebSocket et arrêter d'écouter les événements
  try {
    websocketService.leaveAuction(auctionId);
    websocketService.offBidPlaced();
    console.log("✅ WebSocket cleanup done");
  } catch (error) {
    console.error("⚠️ Error during WebSocket cleanup:", error);
  }

  // Nettoyer les intervals
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
    countdownInterval.value = null;
    console.log("✅ Countdown interval cleared");
  }
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value);
    autoRefreshInterval.value = null;
    console.log("✅ Auto-refresh interval cleared");
  }

  console.log("✅ AuctionView cleanup complete");
});

onUnmounted(() => {
  // Double sécurité pour nettoyer les intervals
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
    countdownInterval.value = null;
  }
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value);
    autoRefreshInterval.value = null;
  }
});
</script>

<style scoped src="./css/AuctionView.css"></style>
