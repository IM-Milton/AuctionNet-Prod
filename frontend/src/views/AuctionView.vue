<template>
  <!-- Loading -->
  <div v-if="loading" class="loading-container">
    <div class="spinner">⏳</div>
    <p>Chargement de l'enchère...</p>
  </div>

  <div class="auction-detail" v-else-if="auction">
    <router-link to="/" class="btn-back">
      ← Retour
    </router-link>

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
          :src="auction.product?.images?.[0] || auction.image || 'https://via.placeholder.com/400x300?text=Pas+d%27image'" 
          :alt="auction.product?.title || auction.title" 
          class="main-image" 
        />
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
                  <line v-for="i in 5" :key="`grid-${i}`" 
                    :x1="0" :y1="i * 40" 
                    :x2="400" :y2="i * 40" 
                    class="grid-line" />
                  
                  <!-- Ligne de prix -->
                  <polyline 
                    :points="priceChartPoints" 
                    class="price-line"
                    fill="none"
                    stroke="#667eea"
                    stroke-width="3" />
                  
                  <!-- Points sur la ligne -->
                  <circle v-for="(point, idx) in parsedPricePoints" :key="`point-${idx}`"
                    :cx="point.x" :cy="point.y" r="4"
                    class="price-point" />
                </svg>
                
                <!-- Labels des prix -->
                <div class="chart-labels">
                  <span class="label-y">{{ maxPrice }} €</span>
                  <span class="label-y">{{ Math.round((maxPrice + minPrice) / 2) }} €</span>
                  <span class="label-y">{{ minPrice }} €</span>
                </div>
              </div>
              
              <!-- Statistiques sous le graphique -->
              <div class="chart-stats">
                <div class="stat">
                  <span class="stat-label">Prix actuel</span>
                  <span class="stat-value">{{ auction?.current_price || auction?.start_price }} €</span>
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
            <div class="leaderboard-item" 
              v-for="(leader, index) in leaderboard" 
              :key="leader.userId"
              :class="{ 'top-1': index === 0, 'top-2': index === 1, 'top-3': index === 2 }">
              
              <div class="rank">
                <span v-if="index === 0" class="medal">🥇</span>
                <span v-else-if="index === 1" class="medal">🥈</span>
                <span v-else-if="index === 2" class="medal">🥉</span>
                <span v-else class="rank-number">#{{ index + 1 }}</span>
              </div>
              
              <div class="leader-avatar">
                {{ leader.username[0].toUpperCase() }}
              </div>
              
              <div class="leader-info">
                <div class="leader-name">
                  {{ leader.username }}
                  <span v-if="index === 0 && auction?.status === 'running'" class="winning-badge">🎯 En tête</span>
                </div>
                <div class="leader-stats">
                  <span class="bid-count">{{ leader.bidCount }} enchère{{ leader.bidCount > 1 ? 's' : '' }}</span>
                  <span class="separator">•</span>
                  <span class="last-bid-time">{{ formatTimestamp(leader.lastBidTime) }}</span>
                </div>
              </div>
              
              <div class="leader-badge">
                <div class="highest-bid">{{ leader.currentBid }} €</div>
                <div class="badge-label">{{ index === 0 ? 'En tête' : 'Enchère' }}</div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>Aucun enchérisseur pour le moment</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Historique détaillé des enchères -->
    <div class="bid-history-detailed">
      <h2>📊 Historique des enchères ({{ bidHistory.length }})</h2>
      
      <!-- Timeline -->
      <div class="bid-timeline" v-if="bidHistory.length > 0">
        <div class="timeline-item" v-for="(bid, index) in bidHistory" :key="bid.id">
          <div class="timeline-marker">
            <div class="marker-dot"></div>
            <div class="marker-line" v-if="index < bidHistory.length - 1"></div>
          </div>
          
          <div class="timeline-content">
            <div class="timeline-header">
              <div class="user-info">
                <span class="user-avatar">{{ bid.user.username[0].toUpperCase() }}</span>
                <span class="user-name">{{ bid.user.username }}</span>
                <span class="bid-badge" v-if="index === 0">🔥 En tête</span>
              </div>
              <div class="time-info">
                {{ formatTimestamp(bid.timestamp) }}
              </div>
            </div>
            
            <div class="timeline-body">
              <div class="bid-amount-large">{{ bid.amount }} €</div>
              <div class="bid-meta">
                <span v-if="index < bidHistory.length - 1">
                  +{{ bid.amount - bidHistory[index + 1].amount }} € par rapport à l'enchère précédente
                </span>
                <span v-else>
                  Enchère de départ
                </span>
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
      <h2>📊 Statistiques de l'enchère</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-number">{{ uniqueBidders }}</div>
            <div class="stat-label">Enchérisseurs uniques</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <div class="stat-number">{{ bidHistory.length }}</div>
            <div class="stat-label">Total d'enchères</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <div class="stat-number">{{ averageBid }} €</div>
            <div class="stat-label">Enchère moyenne</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
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
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import websocketService from '@/services/websocket'

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
const countdownInterval = ref(null)
const isMounted = ref(false)
const priceChartRef = ref(null)

// Computed: Leaderboard des enchérisseurs (EN TEMPS RÉEL)
const leaderboard = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return []
  
  const userStats = {}
  
  // Calculer les stats pour chaque utilisateur
  bidHistory.value.forEach(bid => {
    const userId = bid.user.id
    const username = bid.user.username
    const bidTime = bid.timestamp
    
    if (!userStats[userId]) {
      userStats[userId] = {
        userId,
        username,
        bidCount: 0,
        currentBid: 0, // Dernière enchère (la plus haute dans l'historique trié)
        lastBidTime: bidTime,
        allBids: []
      }
    }
    
    userStats[userId].bidCount++
    userStats[userId].allBids.push({ amount: bid.amount, time: bidTime })
    
    // La première enchère dans bidHistory est la plus récente (déjà trié par timestamp desc)
    // Donc on prend seulement la première occurrence de cet utilisateur
    if (userStats[userId].bidCount === 1) {
      userStats[userId].currentBid = bid.amount
      userStats[userId].lastBidTime = bidTime
    }
  })
  
  // Convertir en tableau et trier par enchère actuelle (la plus haute)
  const sorted = Object.values(userStats)
    .sort((a, b) => b.currentBid - a.currentBid)
    .slice(0, 10) // Top 10
  
  console.log('🏆 Leaderboard mis à jour:', sorted)
  return sorted
})

// Computed: Points du graphique de prix (EN TEMPS RÉEL)
const priceChartPoints = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    // Si pas d'enchère, afficher une ligne au prix de départ
    const startPrice = auction.value?.start_price || 100
    return `0,100 400,100`
  }
  
  // bidHistory est trié du plus récent au plus ancien
  // On inverse pour avoir du plus ancien au plus récent
  const sortedBids = [...bidHistory.value].reverse()
  const prices = sortedBids.map(b => b.amount)
  
  // Ajouter le prix de départ au début
  if (auction.value?.start_price) {
    prices.unshift(auction.value.start_price)
  }
  
  const minPriceVal = Math.min(...prices)
  const maxPriceVal = Math.max(...prices)
  const priceRange = maxPriceVal - minPriceVal || 1
  
  const points = prices.map((price, index) => {
    const x = (index / Math.max(prices.length - 1, 1)) * 400
    const y = 180 - ((price - minPriceVal) / priceRange) * 160
    return `${x.toFixed(2)},${y.toFixed(2)}`
  }).join(' ')
  
  console.log('📈 Graphique mis à jour:', {
    bidCount: bidHistory.value.length,
    prices: prices,
    points: points.substring(0, 50) + '...'
  })
  
  return points
})

// Computed: Points parsés pour les cercles
const parsedPricePoints = computed(() => {
  if (!priceChartPoints.value) return []
  return priceChartPoints.value.split(' ').map(point => {
    const [x, y] = point.split(',').map(Number)
    return { x, y }
  })
})

// Computed: Prix min et max pour les labels
const minPrice = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    return auction.value?.start_price || 0
  }
  const prices = bidHistory.value.map(b => b.amount)
  if (auction.value?.start_price) {
    prices.push(auction.value.start_price)
  }
  return Math.min(...prices)
})

const maxPrice = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) {
    return auction.value?.start_price || 0
  }
  const prices = bidHistory.value.map(b => b.amount)
  return Math.max(...prices)
})

// Computed: Augmentation du prix
const priceIncrease = computed(() => {
  if (!auction.value) return 0
  const currentPrice = auction.value.current_price || auction.value.start_price
  return currentPrice - auction.value.start_price
})

const priceIncreasePercent = computed(() => {
  if (!auction.value || !auction.value.start_price) return 0
  const increase = priceIncrease.value
  return Math.round((increase / auction.value.start_price) * 100)
})

// Computed: Statistiques
const uniqueBidders = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0
  const uniqueUsers = new Set(bidHistory.value.map(b => b.user.id))
  return uniqueUsers.size
})

const averageBid = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0
  const total = bidHistory.value.reduce((sum, bid) => sum + bid.amount, 0)
  return Math.round(total / bidHistory.value.length)
})

const bidsPerHour = computed(() => {
  if (!bidHistory.value || bidHistory.value.length === 0) return 0
  
  // Calculer la durée depuis la première enchère
  const sortedBids = [...bidHistory.value].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp)
  )
  
  const firstBid = new Date(sortedBids[0].timestamp)
  const lastBid = new Date(sortedBids[sortedBids.length - 1].timestamp)
  const hoursDiff = (lastBid - firstBid) / (1000 * 60 * 60)
  
  if (hoursDiff < 0.01) return bidHistory.value.length // Moins d'une minute
  
  return Math.round(bidHistory.value.length / hoursDiff)
})

// Charger les données de l'enchère
async function loadAuction() {
  // Ne rien faire si le composant n'est plus monté
  if (!isMounted.value) return
  
  try {
    loading.value = true
    const data = await api.getAuction(auctionId)
    
    // Vérifier à nouveau si le composant est toujours monté
    if (!isMounted.value) return
    
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

// Charger l'historique des enchères depuis le backend
async function loadBidHistory() {
  if (!auction.value || !isMounted.value) return
  
  try {
    console.log('🔄 Chargement de l\'historique des enchères...')
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auctions/${auctionId}/bids`)
    if (!response.ok) {
      console.warn('⚠️ Impossible de charger l\'historique des enchères')
      bidHistory.value = []
      return
    }
    
    const data = await response.json()
    if (!isMounted.value) return
    
    // Force la réactivité en créant un nouveau tableau
    bidHistory.value = [...(data.bids || [])]
    
    console.log('✅ Historique chargé:', {
      count: bidHistory.value.length,
      bids: bidHistory.value.map(b => ({ user: b.user.username, amount: b.amount }))
    })
  } catch (error) {
    console.error('❌ Erreur lors du chargement de l\'historique:', error)
    bidHistory.value = []
  }
}

// Placer une enchère
async function placeBid() {
  // Vérifier le token JWT
  const token = api.getToken()
  if (!token) {
    errorMessage.value = 'Vous devez être connecté pour enchérir (token manquant)'
    setTimeout(() => router.push('/login'), 2000)
    return
  }
  
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
    
    console.log('🔐 Placement enchère avec token:', token.substring(0, 20) + '...')
    
    await api.placeBid(auctionId, bidAmount.value)
    
    successMessage.value = `✅ Enchère de ${bidAmount.value} € placée avec succès !`
    
    // Le WebSocket mettra à jour automatiquement les données
    // Pas besoin de recharger manuellement
    
    setTimeout(() => {
      if (isMounted.value) {
        successMessage.value = ''
      }
    }, 3000)
    
  } catch (error) {
    console.error('Erreur lors de l\'enchère:', error)
    
    // Si erreur 401, rediriger vers login
    if (error.message && error.message.includes('401')) {
      errorMessage.value = 'Session expirée. Veuillez vous reconnecter.'
      setTimeout(() => router.push('/login'), 2000)
    } else {
      errorMessage.value = error.message || 'Impossible de placer l\'enchère'
    }
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

// Formater le timestamp pour l'affichage
function formatTimestamp(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'À l\'instant'
  if (diffMins < 60) return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`
  if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`
  if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`
  
  // Format date complète pour les enchères plus anciennes
  return date.toLocaleDateString('fr-FR', { 
    day: 'numeric', 
    month: 'short', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

onMounted(async () => {
  isMounted.value = true
  
  // Charger l'utilisateur connecté
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  }
  
  // Charger les données de l'enchère
  await loadAuction()
  
  // Mise à jour du compte à rebours chaque seconde
  countdownInterval.value = setInterval(() => {
    if (isMounted.value) {
      now.value = new Date()
    }
  }, 1000)
  
  // Connecter WebSocket et rejoindre la room de l'enchère
  try {
    websocketService.connect()
    await websocketService.joinAuction(auctionId)
    
    // Écouter les nouvelles enchères en temps réel
    websocketService.onBidPlaced((data) => {
      if (!isMounted.value) return
      
      console.log('🔥 Nouvelle enchère reçue en temps réel:', data)
      
      // Mettre à jour l'enchère avec les nouvelles données
      if (data.auction && data.auction_id === auctionId) {
        auction.value = data.auction
        
        // Mettre à jour le montant minimum pour la prochaine enchère
        bidAmount.value = data.auction.current_price + (data.auction.min_increment || 50)
        
        // Recharger l'historique des enchères pour afficher la nouvelle enchère
        loadBidHistory()
        
        // Afficher une notification
        successMessage.value = `💰 Nouvelle enchère: ${data.current_price} €`
        setTimeout(() => {
          if (isMounted.value) {
            successMessage.value = ''
          }
        }, 3000)
      }
    })
    
    console.log('✅ WebSocket connecté et room rejointe')
  } catch (error) {
    console.error('Erreur WebSocket:', error)
    // En cas d'erreur, fallback sur le polling
    autoRefreshInterval.value = setInterval(async () => {
      if (isMounted.value && !bidLoading.value) {
        await loadAuction()
      }
    }, 5000)
  }
})

onBeforeUnmount(() => {
  console.log('🧹 AuctionView: Cleanup before unmount')
  
  // Marquer le composant comme démonté AVANT de nettoyer
  isMounted.value = false
  
  // Quitter la room WebSocket et arrêter d'écouter les événements
  try {
    websocketService.leaveAuction(auctionId)
    websocketService.offBidPlaced()
    console.log('✅ WebSocket cleanup done')
  } catch (error) {
    console.error('⚠️ Error during WebSocket cleanup:', error)
  }
  
  // Nettoyer les intervals
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
    console.log('✅ Countdown interval cleared')
  }
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
    console.log('✅ Auto-refresh interval cleared')
  }
  
  console.log('✅ AuctionView cleanup complete')
})

onUnmounted(() => {
  // Double sécurité pour nettoyer les intervals
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
  }
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
  text-decoration: none;
  color: #333;
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

.no-bids {
  text-align: center;
  padding: 3rem 1rem;
  color: #999;
  font-size: 1.1rem;
}

.no-bids p {
  margin: 0;
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

/* Analytics Section */
.analytics-section {
  margin-bottom: 2rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.analytics-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.analytics-card h2 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.live-indicator {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.4rem 0.8rem;
  background: #ff4444;
  color: white;
  border-radius: 20px;
  animation: pulse-live 2s infinite;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

@keyframes pulse-live {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(0.98); }
}

/* Graphique de prix */
.chart-container {
  width: 100%;
}

.price-chart {
  position: relative;
}

.chart-area {
  position: relative;
  height: 200px;
  margin-bottom: 1.5rem;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.grid-line {
  stroke: #f0f0f0;
  stroke-width: 1;
}

.price-line {
  stroke: #667eea;
  stroke-width: 3;
  fill: none;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
  transition: all 0.5s ease;
}

.price-point {
  fill: #667eea;
  stroke: white;
  stroke-width: 2;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: pointPop 0.5s ease-out;
}

@keyframes pointPop {
  0% {
    r: 0;
    opacity: 0;
  }
  50% {
    r: 8;
  }
  100% {
    r: 4;
    opacity: 1;
  }
}

.price-point:hover {
  fill: #764ba2;
  filter: drop-shadow(0 2px 6px rgba(118, 75, 162, 0.5));
}

.price-point:last-child {
  fill: #ffd700;
  stroke: #ff8c00;
  stroke-width: 3;
  animation: pulse-point 2s infinite;
}

@keyframes pulse-point {
  0%, 100% { r: 4; }
  50% { r: 6; }
}

.chart-labels {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0 0.5rem;
}

.label-y {
  font-size: 0.75rem;
  color: #999;
  font-weight: 500;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  padding: 1rem;
  background: #f8f9ff;
  border-radius: 12px;
  gap: 1rem;
}

.stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
}

.stat-value.success {
  color: #28a745;
}

/* Leaderboard */
.leaderboard {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9ff;
  border-radius: 12px;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  animation: slideInLeft 0.5s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.leaderboard-item:hover {
  background: #e3f2fd;
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.leaderboard-item.top-1 {
  background: linear-gradient(135deg, #ffd70020 0%, #ffed4e20 100%);
  border-color: #ffd700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
}

.leaderboard-item.top-2 {
  background: linear-gradient(135deg, #c0c0c020 0%, #e0e0e020 100%);
  border-color: #c0c0c0;
}

.leaderboard-item.top-3 {
  background: linear-gradient(135deg, #cd7f3220 0%, #ffb85020 100%);
  border-color: #cd7f32;
}

.rank {
  min-width: 40px;
  text-align: center;
}

.medal {
  font-size: 1.5rem;
}

.rank-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: #999;
}

.leader-avatar {
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

.leader-info {
  flex: 1;
}

.leader-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.winning-badge {
  padding: 0.25rem 0.6rem;
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #856404;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  animation: pulse-winning 2s infinite;
}

@keyframes pulse-winning {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
  50% { transform: scale(1.05); box-shadow: 0 0 0 6px rgba(255, 215, 0, 0); }
}

.leader-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.separator {
  color: #ccc;
}

.leader-badge {
  text-align: right;
}

.highest-bid {
  font-size: 1.2rem;
  font-weight: 700;
  color: #667eea;
}

.badge-label {
  font-size: 0.75rem;
  color: #999;
}

.no-data {
  text-align: center;
  padding: 3rem 1rem;
  color: #999;
}

/* Timeline des enchères */
.bid-history-detailed {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.bid-history-detailed h2 {
  margin-bottom: 2rem;
  color: #333;
}

.bid-timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.timeline-marker {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #667eea;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #667eea;
  z-index: 2;
}

.timeline-item:first-child .marker-dot {
  background: #ffd700;
  box-shadow: 0 0 0 2px #ffd700, 0 0 12px rgba(255, 215, 0, 0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.marker-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(to bottom, #667eea, #e0e0e0);
  margin-top: 0.5rem;
}

.timeline-content {
  flex: 1;
  background: #f8f9ff;
  padding: 1.5rem;
  border-radius: 12px;
  border-left: 3px solid #667eea;
  transition: all 0.3s ease;
}

.timeline-item:first-child .timeline-content {
  border-left-color: #ffd700;
  background: linear-gradient(135deg, #ffd70010 0%, #ffed4e10 100%);
}

.timeline-content:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.bid-badge {
  padding: 0.25rem 0.75rem;
  background: #ffd700;
  color: #856404;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.time-info {
  font-size: 0.85rem;
  color: #999;
}

.timeline-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bid-amount-large {
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
}

.bid-meta {
  font-size: 0.9rem;
  color: #666;
}

.no-bids-timeline {
  padding: 3rem 0;
}

.empty-state {
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #999;
}

/* Section statistiques */
.stats-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.stats-section h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
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
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .timeline-item {
    gap: 1rem;
  }
  
  .bid-amount-large {
    font-size: 1.4rem;
  }
}
</style>
