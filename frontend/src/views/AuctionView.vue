<template>
  <!-- Loading -->
  <div v-if="loading" class="loading-container">
    <div class="spinner">⏳</div>
    <p>Chargement de l'enchère...</p>
  </div>

  <div class="auction-detail" v-else-if="auction">
    <button class="btn-back" @click="router.push('/')">
      ← Retour
    </button>

    <!-- Messages -->
    <div v-if="errorMessage" class="alert alert-error">
      ❌ {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <div class="detail-content">
      <div class="image-section">
        <img :src="auction.image" :alt="auction.title" class="main-image" />
        <div class="image-gallery">
          <img :src="auction.image" alt="Vue 1" class="thumbnail active" />
          <img :src="auction.image" alt="Vue 2" class="thumbnail" />
          <img :src="auction.image" alt="Vue 3" class="thumbnail" />
        </div>
      </div>

      <div class="info-section">
        <div class="header">
          <h1>{{ auction.product?.title || auction.title }}</h1>
          <span class="badge" :class="{
            'badge-success': auction.status === 'running',
            'badge-warning': auction.status === 'scheduled',
            'badge-secondary': auction.status === 'closed'
          }">
            {{ getStatusLabel(auction.status) }}
          </span>
        </div>

        <div class="price-section">
          <div class="current-price">
            <span class="label">Prix actuel</span>
            <span class="amount">{{ auction.current_price || auction.start_price }} €</span>
          </div>
          <div class="stats">
            <div class="stat-item">
              <span>👥 {{ auction.bids_count || 0 }} enchères</span>
            </div>
            <div class="stat-item">
              <span>� Prix de départ: {{ auction.start_price }} €</span>
            </div>
          </div>
        </div>

        <div class="timer-section" v-if="auction.status === 'running' && auction.end_at">
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
        
        <div class="timer-section" v-else-if="auction.status === 'scheduled' && auction.start_at">
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
          </div>
        </div>
        
        <div class="timer-section closed" v-else-if="auction.status === 'closed'">
          <div class="timer-label">🏁 Enchère terminée</div>
          <div v-if="auction.winner_id" class="winner-info">
            <p>🎉 Gagnant: {{ auction.winner_id }}</p>
            <p>💰 Prix final: {{ auction.current_price }} €</p>
          </div>
        </div>

        <div class="bid-section" v-if="auction.status === 'running'">
          <label for="bid-amount">
            Votre enchère (minimum: {{ (auction.current_price || auction.start_price) + auction.min_increment }} €)
          </label>
          <div class="bid-input-group">
            <input
              type="number"
              id="bid-amount"
              v-model="bidAmount"
              :min="(auction.current_price || auction.start_price) + auction.min_increment"
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
              {{ bidLoading ? 'Enchère en cours...' : 'Enchérir' }}
            </button>
          </div>
          
          <div class="quick-bids">
            <button @click="quickBid(auction.min_increment)" class="btn-quick">
              +{{ auction.min_increment }} €
            </button>
            <button @click="quickBid(auction.min_increment * 2)" class="btn-quick">
              +{{ auction.min_increment * 2 }} €
            </button>
            <button @click="quickBid(auction.min_increment * 5)" class="btn-quick">
              +{{ auction.min_increment * 5 }} €
            </button>
          </div>
          
          <p v-if="!currentUser" class="warning-message">
            ⚠️ Vous devez être <router-link to="/login">connecté</router-link> pour enchérir
          </p>
        </div>
        
        <div class="bid-section disabled" v-else>
          <p class="info-message">
            {{ auction.status === 'scheduled' ? '⏰ L\'enchère n\'a pas encore commencé' : '🏁 L\'enchère est terminée' }}
          </p>
        </div>

        <div class="description-section">
          <h3>📝 Description</h3>
          <p>{{ auction.product?.description || 'Aucune description disponible.' }}</p>
          
          <div class="product-details" v-if="auction.product">
            <h4>Détails du produit</h4>
            <ul>
              <li><strong>Catégorie:</strong> {{ auction.product.category }}</li>
              <li><strong>État:</strong> {{ auction.product.condition === 'new' ? 'Neuf' : 'Occasion' }}</li>
            </ul>
          </div>
        </div>

        <div class="auction-info-section">
          <h3>ℹ️ Informations sur l'enchère</h3>
          <ul>
            <li><strong>ID:</strong> {{ auction.id }}</li>
            <li><strong>Début:</strong> {{ formatDate(auction.start_at) }}</li>
            <li><strong>Fin:</strong> {{ formatDate(auction.end_at) }}</li>
            <li><strong>Incrément minimum:</strong> {{ auction.min_increment }} €</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Historique des enchères -->
    <div class="bid-history">
      <h2>📊 Historique des enchères</h2>
      <div class="history-list">
        <div class="history-item" v-for="(bid, index) in bidHistory" :key="index">
          <div class="bidder">
            <span class="bidder-avatar">{{ bid.user[0] }}</span>
            <span class="bidder-name">{{ bid.user }}</span>
          </div>
          <div class="bid-details">
            <span class="bid-amount">{{ bid.amount }} €</span>
            <span class="bid-time">{{ bid.time }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Enchères similaires -->
    <div class="similar-section">
      <h2>🔍 Enchères similaires</h2>
      <div class="similar-grid">
        <div class="similar-item" v-for="similar in similarAuctions" :key="similar.id">
          <img :src="similar.image" :alt="similar.title" />
          <h4>{{ similar.title }}</h4>
          <p class="similar-price">{{ similar.price }} €</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const auctionId = route.params.id

const auction = ref(null)
const bidAmount = ref(0)
const now = ref(new Date())
const loading = ref(true)
const bidLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const currentUser = ref(null)
const bidHistory = ref([])
const similarAuctions = ref([])
const autoRefreshInterval = ref(null)

// Charger les données de l'enchère
async function loadAuction() {
  try {
    loading.value = true
    const data = await api.getAuction(auctionId)
    auction.value = data
    
    // Initialiser le montant de l'enchère avec le minimum requis
    if (data.current_price) {
      bidAmount.value = data.current_price + (data.min_increment || 50)
    } else {
      bidAmount.value = data.start_price + (data.min_increment || 50)
    }
    
    // Charger l'historique des enchères (simulation pour le frontend)
    loadBidHistory()
    
  } catch (error) {
    console.error('Erreur lors du chargement de l\'enchère:', error)
    errorMessage.value = 'Impossible de charger l\'enchère'
  } finally {
    loading.value = false
  }
}

// Charger l'historique des enchères (simulé)
function loadBidHistory() {
  if (!auction.value) return
  
  // Pour l'instant, on simule l'historique
  const bidsCount = auction.value.bids_count || 0
  bidHistory.value = []
  
  for (let i = 0; i < Math.min(bidsCount, 10); i++) {
    bidHistory.value.push({
      user: `Enchérisseur ${i + 1}`,
      amount: auction.value.current_price - (i * (auction.value.min_increment || 50)),
      time: `Il y a ${i * 5 + 2} minutes`
    })
  }
}

// Placer une enchère
async function placeBid() {
  if (!currentUser.value) {
    errorMessage.value = 'Vous devez être connecté pour enchérir'
    setTimeout(() => router.push('/login'), 2000)
    return
  }
  
  if (bidAmount.value <= auction.value.current_price) {
    errorMessage.value = `Votre enchère doit être supérieure à ${auction.value.current_price} €`
    return
  }
  
  const minRequired = auction.value.current_price + auction.value.min_increment
  if (bidAmount.value < minRequired) {
    errorMessage.value = `L'enchère minimum est de ${minRequired} €`
    return
  }
  
  try {
    bidLoading.value = true
    errorMessage.value = ''
    
    await api.placeBid(auctionId, bidAmount.value)
    
    successMessage.value = `✅ Enchère de ${bidAmount.value} € placée avec succès !`
    
    // Recharger les données de l'enchère
    await loadAuction()
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (error) {
    console.error('Erreur lors de l\'enchère:', error)
    errorMessage.value = error.message || 'Impossible de placer l\'enchère'
  } finally {
    bidLoading.value = false
  }
}

// Enchère rapide
function quickBid(increment) {
  const currentPrice = auction.value.current_price || auction.value.start_price
  bidAmount.value = currentPrice + increment
}

// Calculer le temps restant
const timeRemaining = computed(() => {
  if (!auction.value || !auction.value.end_at) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 }
  }
  
  const endDate = new Date(auction.value.end_at)
  const diff = endDate - now.value
  
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 }
  }
  
  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000)
  }
})

// Calculer le temps avant le début
const timeUntilStart = computed(() => {
  if (!auction.value || !auction.value.start_at) {
    return { days: 0, hours: 0, minutes: 0 }
  }
  
  const startDate = new Date(auction.value.start_at)
  const diff = startDate - now.value
  
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0 }
  }
  
  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  }
})

// Formater une date
function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Obtenir le label du statut
function getStatusLabel(status) {
  const labels = {
    'scheduled': 'Programmée',
    'running': 'En cours',
    'closed': 'Terminée'
  }
  return labels[status] || status
}

let interval

onMounted(async () => {
  // Charger l'utilisateur connecté
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }
  
  // Charger les données de l'enchère
  await loadAuction()
  
  // Mise à jour du compte à rebours chaque seconde
  interval = setInterval(() => {
    now.value = new Date()
  }, 1000)
  
  // Auto-refresh toutes les 10 secondes pour avoir les dernières enchères
  autoRefreshInterval.value = setInterval(async () => {
    if (!bidLoading.value) {
      await loadAuction()
    }
  }, 10000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
  if (autoRefreshInterval.value) clearInterval(autoRefreshInterval.value)
})
</script>

<style scoped>
/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 1rem;
}

.spinner {
  font-size: 3rem;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Alerts */
.alert {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 500;
  animation: slideDown 0.3s ease;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 2px solid #fcc;
}

.alert-success {
  background: #efe;
  color: #3a3;
  border: 2px solid #cfc;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auction-detail {
  animation: fadeIn 0.5s ease;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-back:hover {
  background: #f0f0f0;
  transform: translateX(-5px);
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.image-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.main-image {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-gallery {
  display: flex;
  gap: 0.75rem;
}

.thumbnail {
  width: calc(33.333% - 0.5rem);
  border-radius: 8px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.thumbnail:hover,
.thumbnail.active {
  opacity: 1;
  border-color: #667eea;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header h1 {
  font-size: 2rem;
  color: #333;
  line-height: 1.3;
}

.price-section {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 12px;
}

.current-price {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  color: #666;
  font-size: 0.95rem;
}

.timer-section {
  padding: 1.5rem;
  background: #fff3cd;
  border-radius: 12px;
  border: 2px solid #ffc107;
}

.timer-label {
  font-weight: 600;
  color: #856404;
  margin-bottom: 1rem;
}

.countdown {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.time-unit {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-value {
  font-size: 2rem;
  font-weight: 700;
  color: #856404;
}

.time-label {
  font-size: 0.75rem;
  color: #856404;
  text-transform: uppercase;
}

.separator {
  font-size: 2rem;
  font-weight: 700;
  color: #856404;
}

.bid-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bid-section label {
  font-weight: 600;
  color: #555;
}

.bid-input-group {
  display: flex;
  gap: 1rem;
}

.bid-input-group input {
  flex: 1;
}

.btn-bid {
  white-space: nowrap;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quick-bids {
  display: flex;
  gap: 0.75rem;
}

.btn-quick {
  flex: 1;
  padding: 0.5rem;
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-quick:hover {
  background: #667eea;
  color: white;
}

.description-section h3,
.seller-section h3 {
  color: #333;
  margin-bottom: 0.75rem;
}

.description-section p {
  color: #666;
  line-height: 1.8;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9ff;
  border-radius: 8px;
}

.seller-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.seller-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.seller-name {
  font-weight: 600;
  color: #333;
}

.seller-rating {
  color: #666;
  font-size: 0.9rem;
}

.bid-history {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.bid-history h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9ff;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: #e3f2fd;
}

.bidder {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bidder-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.bidder-name {
  font-weight: 600;
  color: #333;
}

.bid-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.bid-amount {
  font-size: 1.2rem;
  font-weight: 700;
  color: #667eea;
}

.bid-time {
  font-size: 0.85rem;
  color: #999;
}

.similar-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.similar-section h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.similar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.similar-item {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
}

.similar-item:hover {
  transform: translateY(-5px);
}

.similar-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

.similar-item h4 {
  margin: 0.75rem 0 0.25rem;
  color: #333;
  font-size: 0.95rem;
}

.similar-price {
  font-weight: 700;
  color: #667eea;
}

/* Nouveaux styles */
.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.badge-secondary {
  background: #e0e0e0;
  color: #666;
}

.timer-section.closed {
  background: #f0f0f0;
  border-color: #999;
}

.winner-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #efe;
  border-radius: 8px;
}

.winner-info p {
  margin: 0.5rem 0;
  color: #333;
  font-weight: 500;
}

.bid-section.disabled {
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 12px;
  text-align: center;
}

.warning-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fff3cd;
  border-radius: 8px;
  color: #856404;
  font-size: 0.9rem;
}

.warning-message a {
  color: #667eea;
  font-weight: 600;
  text-decoration: underline;
}

.info-message {
  font-size: 1.1rem;
  color: #666;
  font-weight: 500;
}

.btn-bid:disabled,
.bid-input-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.product-details,
.auction-info-section {
  margin-top: 1rem;
}

.product-details h4,
.auction-info-section h3 {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.75rem;
}

.product-details ul,
.auction-info-section ul {
  list-style: none;
  padding: 0;
}

.product-details li,
.auction-info-section li {
  padding: 0.5rem 0;
  color: #666;
  border-bottom: 1px solid #eee;
}

.product-details li:last-child,
.auction-info-section li:last-child {
  border-bottom: none;
}

@media (max-width: 968px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
  
  .countdown {
    gap: 0.5rem;
  }
  
  .time-value {
    font-size: 1.5rem;
  }
}
</style>
