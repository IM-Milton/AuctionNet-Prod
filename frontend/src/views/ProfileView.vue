<template>
  <div class="profile-page">
    <div v-if="!currentUser" class="loading">
      Chargement...
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
          <span class="balance-amount">{{ currentUser.balance.toFixed(2) }} €</span>
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
          <router-link to="/" class="btn btn-primary">Découvrir les enchères</router-link>
        </div>

        <div v-else class="auction-card" v-for="auction in myParticipations" :key="auction.id">
          <div class="auction-image">
            <img :src="auction.imageUrl" :alt="auction.title" />
            <div class="auction-status" :class="getAuctionStatus(auction).class">
              {{ getAuctionStatus(auction).text }}
            </div>
          </div>
          
          <div class="auction-details">
            <h3>{{ auction.title }}</h3>
            <p class="auction-category">{{ getCategoryLabel(auction.category) }}</p>
            
            <div class="auction-info">
              <div class="info-item">
                <span class="label">Votre enchère :</span>
                <span class="value">{{ auction.myBid }} €</span>
              </div>
              <div class="info-item">
                <span class="label">Enchère actuelle :</span>
                <span class="value highlight">{{ auction.currentBid }} €</span>
              </div>
              <div class="info-item">
                <span class="label">Fin :</span>
                <span class="value">{{ formatDate(auction.endDate) }}</span>
              </div>
            </div>
          </div>

          <div class="auction-actions">
            <router-link :to="`/auction/${auction.id}`" class="btn btn-outline">
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
          <router-link to="/sell" class="btn btn-primary">Créer une enchère</router-link>
        </div>

        <div v-else class="auction-card" v-for="auction in myAuctions" :key="auction.id">
          <div class="auction-image">
            <img :src="auction.imageUrl" :alt="auction.title" />
            <div class="auction-status" :class="getAuctionStatus(auction).class">
              {{ getAuctionStatus(auction).text }}
            </div>
          </div>
          
          <div class="auction-details">
            <h3>{{ auction.title }}</h3>
            <p class="auction-category">{{ getCategoryLabel(auction.category) }}</p>
            
            <div class="auction-info">
              <div class="info-item">
                <span class="label">Prix de départ :</span>
                <span class="value">{{ auction.startPrice }} €</span>
              </div>
              <div class="info-item">
                <span class="label">Enchère actuelle :</span>
                <span class="value highlight">{{ auction.currentBid }} €</span>
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
            <router-link :to="`/auction/${auction.id}`" class="btn btn-outline">
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
          <router-link to="/" class="btn btn-primary">Participer aux enchères</router-link>
        </div>

        <div v-else class="auction-card" v-for="auction in wonAuctions" :key="auction.id">
          <div class="auction-image">
            <img :src="auction.imageUrl" :alt="auction.title" />
            <div class="auction-status won">
              🏆 Remportée
            </div>
          </div>
          
          <div class="auction-details">
            <h3>{{ auction.title }}</h3>
            <p class="auction-category">{{ getCategoryLabel(auction.category) }}</p>
            
            <div class="auction-info">
              <div class="info-item">
                <span class="label">Prix remporté :</span>
                <span class="value highlight">{{ auction.winningBid }} €</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('participations')

const tabs = [
  { id: 'participations', icon: '🎯', label: 'Participations' },
  { id: 'myAuctions', icon: '💰', label: 'Mes enchères' },
  { id: 'won', icon: '🏆', label: 'Gagnées' }
]

// Données utilisateur depuis localStorage
const currentUser = ref(null)

onMounted(() => {
  const user = localStorage.getItem('currentUser')
  if (user) {
    currentUser.value = JSON.parse(user)
  } else {
    // Rediriger vers login si pas connecté
    router.push('/login')
  }
})

// Enchères participées (simulées)
const myParticipations = ref([
  {
    id: 1,
    title: 'MacBook Pro 16" M3 Max',
    category: 'electronics',
    imageUrl: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
    myBid: 2100,
    currentBid: 2300,
    startPrice: 1800,
    endDate: '2025-11-20T18:00:00',
    bidsCount: 12,
    status: 'active'
  },
  {
    id: 2,
    title: 'iPhone 15 Pro Max',
    category: 'electronics',
    imageUrl: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
    myBid: 950,
    currentBid: 980,
    startPrice: 800,
    endDate: '2025-11-18T20:00:00',
    bidsCount: 8,
    status: 'active'
  }
])

// Mes enchères créées (récupération depuis localStorage + données simulées)
const myAuctions = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userAuctions') || '[]')
  const simulated = [
    {
      id: 101,
      title: 'Sony PlayStation 5',
      category: 'electronics',
      imageUrl: 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400',
      startPrice: 400,
      currentBid: 485,
      endDate: '2025-11-19T22:00:00',
      bidsCount: 7,
      winner: null,
      status: 'active'
    },
    {
      id: 102,
      title: 'Canon EOS R6',
      category: 'electronics',
      imageUrl: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400',
      startPrice: 1500,
      currentBid: 1850,
      endDate: '2025-11-15T15:00:00',
      bidsCount: 15,
      winner: 'Marie Martin',
      status: 'completed'
    }
  ]
  
  return [...simulated, ...stored]
})

// Enchères gagnées (simulées)
const wonAuctions = ref([
  {
    id: 201,
    title: 'Apple Watch Series 9',
    category: 'electronics',
    imageUrl: 'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400',
    winningBid: 380,
    endDate: '2025-11-10T16:00:00',
    status: 'won'
  }
])

function getTabCount(tabId) {
  switch (tabId) {
    case 'participations': return myParticipations.value.length
    case 'myAuctions': return myAuctions.value.length
    case 'won': return wonAuctions.value.length
    default: return 0
  }
}

function getAuctionStatus(auction) {
  const now = new Date()
  const endDate = new Date(auction.endDate)
  
  if (auction.status === 'won') {
    return { text: '🏆 Remportée', class: 'won' }
  }
  
  if (endDate < now) {
    return { text: '⏱️ Terminée', class: 'ended' }
  }
  
  return { text: '🔥 En cours', class: 'active' }
}

function getCategoryLabel(category) {
  const labels = {
    electronics: '📱 Électronique',
    fashion: '👗 Mode',
    home: '🏠 Maison',
    sports: '⚽ Sport',
    art: '🎨 Art',
    vehicles: '🚗 Véhicules',
    other: '📦 Autre'
  }
  return labels[category] || category
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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
