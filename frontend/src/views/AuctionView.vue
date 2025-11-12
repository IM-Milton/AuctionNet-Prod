<template>
  <div class="auction-detail" v-if="auction">
    <button class="btn-back" @click="goBack">
      ← Retour
    </button>

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
          <h1>{{ auction.title }}</h1>
          <span class="badge badge-success">En cours</span>
        </div>

        <div class="price-section">
          <div class="current-price">
            <span class="label">Prix actuel</span>
            <span class="amount">{{ auction.price }} €</span>
          </div>
          <div class="stats">
            <div class="stat-item">
              <span>👥 {{ auction.bids || 0 }} enchères</span>
            </div>
            <div class="stat-item">
              <span>👁️ {{ auction.views || 156 }} vues</span>
            </div>
          </div>
        </div>

        <div class="timer-section" v-if="auction.endTime">
          <div class="timer-label">⏰ Temps restant</div>
          <div class="countdown">
            <div class="time-unit">
              <span class="time-value">{{ days }}</span>
              <span class="time-label">jours</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ hours }}</span>
              <span class="time-label">heures</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ minutes }}</span>
              <span class="time-label">minutes</span>
            </div>
            <div class="separator">:</div>
            <div class="time-unit">
              <span class="time-value">{{ seconds }}</span>
              <span class="time-label">secondes</span>
            </div>
          </div>
        </div>

        <div class="bid-section">
          <label for="bid-amount">Votre enchère (minimum: {{ auction.price + 1 }} €)</label>
          <div class="bid-input-group">
            <input
              type="number"
              id="bid-amount"
              v-model="bidAmount"
              :min="auction.price + 1"
              placeholder="Entrez votre enchère"
            />
            <button class="btn btn-bid" @click="placeBid">
              💰 Enchérir
            </button>
          </div>
          
          <div class="quick-bids">
            <button @click="quickBid(50)" class="btn-quick">+50 €</button>
            <button @click="quickBid(100)" class="btn-quick">+100 €</button>
            <button @click="quickBid(200)" class="btn-quick">+200 €</button>
          </div>
        </div>

        <div class="description-section">
          <h3>📝 Description</h3>
          <p>{{ auction.description || 'Article en excellent état. Livraison rapide et sécurisée. Garantie satisfait ou remboursé.' }}</p>
        </div>

        <div class="seller-section">
          <h3>👤 Vendeur</h3>
          <div class="seller-info">
            <div class="seller-avatar">JD</div>
            <div class="seller-details">
              <span class="seller-name">John Doe</span>
              <span class="seller-rating">⭐ 4.8 (127 avis)</span>
            </div>
          </div>
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

const route = useRoute()
const router = useRouter()
const id = route.params.id

const auctions = {
  1: { 
    title: 'Montre Rolex Submariner', 
    price: 3500, 
    image: '/assets/images/rolex.jpg',
    bids: 23,
    views: 245,
    endTime: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    description: 'Magnifique montre Rolex Submariner en excellent état. Boîtier en acier inoxydable, bracelet Oyster. Fonctionne parfaitement, révisée récemment.'
  },
  2: { 
    title: 'Vélo de course Canyon', 
    price: 1200, 
    image: '/assets/images/velo.jpg',
    bids: 15,
    views: 189,
    endTime: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    description: 'Vélo de course Canyon Aeroad, cadre carbone, groupe Shimano Ultegra. Très peu utilisé, comme neuf.'
  },
  3: { 
    title: 'MacBook Pro 16"', 
    price: 2100, 
    image: '/assets/images/macbook.jpg',
    bids: 42,
    views: 387,
    endTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    description: 'MacBook Pro 16" 2023, Apple M3 Pro, 18Go RAM, 512Go SSD. État impeccable, avec boîte et accessoires d\'origine.'
  }
}

const auction = auctions[id]
const bidAmount = ref(auction ? auction.price + 50 : 0)
const now = ref(new Date())

const bidHistory = ref([
  { user: 'Alice M.', amount: auction?.price || 0, time: 'Il y a 2 minutes' },
  { user: 'Bob D.', amount: (auction?.price || 0) - 50, time: 'Il y a 15 minutes' },
  { user: 'Charlie R.', amount: (auction?.price || 0) - 100, time: 'Il y a 1 heure' },
  { user: 'David L.', amount: (auction?.price || 0) - 200, time: 'Il y a 3 heures' }
])

const similarAuctions = ref([
  { id: 2, title: 'Vélo de course Canyon', price: 1200, image: '/assets/images/velo.jpg' },
  { id: 3, title: 'MacBook Pro 16"', price: 2100, image: '/assets/images/macbook.jpg' },
  { id: 4, title: 'iPhone 15 Pro', price: 950, image: '/assets/images/iphone.jpg' }
])

let interval

onMounted(() => {
  interval = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const timeLeft = computed(() => {
  if (!auction?.endTime) return 0
  return Math.max(0, auction.endTime - now.value)
})

const days = computed(() => Math.floor(timeLeft.value / (1000 * 60 * 60 * 24)))
const hours = computed(() => Math.floor((timeLeft.value % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)))
const minutes = computed(() => Math.floor((timeLeft.value % (1000 * 60 * 60)) / (1000 * 60)))
const seconds = computed(() => Math.floor((timeLeft.value % (1000 * 60)) / 1000))

function placeBid() {
  if (bidAmount.value <= auction.price) {
    alert('Votre enchère doit être supérieure au prix actuel !')
    return
  }
  alert(`✅ Enchère de ${bidAmount.value} € placée avec succès !`)
  auction.price = bidAmount.value
  bidAmount.value = auction.price + 50
}

function quickBid(amount) {
  bidAmount.value = auction.price + amount
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
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
