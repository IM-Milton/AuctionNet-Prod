<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Bienvenue sur AuctioNet</h1>
        <p class="hero-subtitle">
          Découvrez des enchères exceptionnelles et trouvez vos trésors
        </p>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">{{ activeAuctionsCount }}</span>
            <span class="stat-label">Enchères actives</span>
          </div>
          <!-- <div class="stat">
            <span class="stat-number">15,678</span>
            <span class="stat-label">Membres</span>
          </div> -->
        </div>
      </div>
    </section>

    <!-- Filtres -->
    <section class="filters">
      <div class="filter-group">
        <label>Catégorie :</label>
        <select v-model="selectedCategory">
          <option value="all">Toutes</option>
          <option
            v-for="cat in categories"
            :key="cat"
            :value="cat"
          >
            {{ cat }}
          </option>
        </select>
      </div>

        <div class="filter-group">
    <label>Statut :</label>
    <select v-model="selectedStatus">
      <option value="all">Tous</option>
      <option value="scheduled">À venir</option>
      <option value="running">En cours</option>
      <option value="closed">Terminées</option>
    </select>
  </div>
      
      <div class="filter-group">
        <label>Trier par :</label>
        <select v-model="sortBy">
          <option value="recent">Plus récentes</option>
          <option value="price-low">Prix croissant</option>
          <option value="price-high">Prix décroissant</option>
          <option value="ending">Fin proche</option>
        </select>
      </div>

      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="🔍 Rechercher une enchère..."
        />
      </div>
    </section>

    <!-- Enchères en vedette -->
    <section class="featured">
      <h2>⭐ Enchères {{ loading ? 'en chargement...' : 'en vedette' }}</h2>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner">⏳</div>
        <p>Chargement des enchères...</p>
      </div>
      
      <div v-else-if="filteredAuctions.length > 0" class="auction-grid">
        <AuctionItem
          v-for="auction in filteredAuctions"
          :key="auction.id"
          :auction="auction"
          @click="viewAuction(auction.id)"
        />
      </div>
      
      <div v-else class="no-results">
        <p>😕 Aucune enchère ne correspond à vos critères</p>
      </div>
    </section>

    <!-- Section informative -->
    <section class="info-section">
      <h2>Comment ça marche ?</h2>
      <div class="steps">
        <div class="step">
          <div class="step-icon">1️⃣</div>
          <h3>Inscrivez-vous</h3>
          <p>Créez votre compte gratuitement en quelques secondes</p>
        </div>
        <div class="step">
          <div class="step-icon">2️⃣</div>
          <h3>Explorez</h3>
          <p>Parcourez les enchères et trouvez vos articles préférés</p>
        </div>
        <div class="step">
          <div class="step-icon">3️⃣</div>
          <h3>Enchérissez</h3>
          <p>Placez vos enchères et suivez vos offres en temps réel</p>
        </div>
        <div class="step">
          <div class="step-icon">4️⃣</div>
          <h3>Gagnez</h3>
          <p>Remportez l'enchère et recevez votre article rapidement</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AuctionItem from '../components/AuctionItem.vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const selectedCategory = ref('all')
const sortBy = ref('recent')
const searchQuery = ref('')
const auctions = ref([])
const loading = ref(true)
const categories = ref([])

// Charger les enchères depuis le backend
async function loadAuctions() {
  try {
    loading.value = true
    const filters = {}
    
    if (selectedCategory.value !== 'all') {
      filters.category = selectedCategory.value
    }
    
    const data = await api.getAuctions(filters)
    
    // Adapter les données du backend au format attendu par le frontend
    auctions.value = data.auctions?.map(auction => ({
      id: auction.id,
      title: auction.product?.title || 'Sans titre',
      price: auction.current_price || auction.start_price,
      image: auction.product?.images?.[0] || '/assets/images/placeholder.jpg',
      category: auction.product?.category || 'other',
      endTime: new Date(auction.end_at),
      bids: auction.bids_count || 0,
      status: auction.status
    })) || []
    
  } catch (error) {
    console.error('Erreur lors du chargement des enchères:', error)
    // Fallback sur des données simulées en cas d'erreur
    auctions.value = [
  { 
    id: 1, 
    title: 'Montre Rolex Submariner', 
    price: 3500, 
    image: '/assets/images/rolex.jpg',
    category: 'fashion',
    endTime: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    bids: 23
  },
  { 
    id: 2, 
    title: 'Vélo de course Canyon', 
    price: 1200, 
    image: '/assets/images/velo.jpg',
    category: 'sports',
    endTime: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
    bids: 15
  },
  { 
    id: 3, 
    title: 'MacBook Pro 16"', 
    price: 2100, 
    image: '/assets/images/macbook.jpg',
    category: 'electronics',
    endTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    bids: 42
  },
  { 
    id: 4, 
    title: 'iPhone 15 Pro Max', 
    price: 950, 
    image: '/assets/images/iphone.jpg',
    category: 'electronics',
    endTime: new Date(Date.now() + 5 * 60 * 60 * 1000),
    bids: 67
  },
  { 
    id: 5, 
    title: 'Sac Hermès Birkin', 
    price: 8500, 
    image: '/assets/images/hermes.jpg',
    category: 'fashion',
      endTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      bids: 89
    },
    { 
      id: 6, 
      title: 'Tableau Abstrait Original', 
      price: 750, 
      image: '/assets/images/art.jpg',
      category: 'art',
      endTime: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000),
      bids: 12
    }
    ]
  } finally {
    loading.value = false
  }
}

// Charger les catégories
async function loadCategories() {
  try {
    const data = await api.getCategories()
    categories.value = data.categories || []
  } catch (error) {
    console.error('Erreur lors du chargement des catégories:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    loadAuctions(),
    loadCategories()
  ])
})
const selectedCategory = ref<"all" | string>("all");
const selectedStatus = ref<StatusFilter>("running"); 
const sortBy = ref<"recent" | "price-low" | "price-high" | "ending">("recent");
const searchQuery = ref("");

type UiAuction = {
  id: string;
  title: string;
  price: number;
  image: string;
  category: string;
  startTime: Date | null;
  endTime: Date | null;
  bids: number;
  status: StatusFilter; 
};

const auctions = ref<UiAuction[]>([]);
const categories = ref<string[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

function mapAuctionToUi(a: Auction): UiAuction {
  const p = a.product ?? { title: "Sans titre", category: "autre", images: [] };
  const images = p.images[0];
  console.log(images);

  return {
    id: a.id,
    title: p.title ?? "Sans titre",
    price: (a as any).current_price ?? a.start_price,
    image: toMediaUrl(images),
    category: p.category ?? "autre",
    startTime: a.start_at ? new Date(a.start_at) : null,   
    endTime: a.end_at ? new Date(a.end_at) : null,
    bids: 0,
    status: (a as any).status ?? "running",
  };
}

async function loadCategories() {
  try {
    const cats = await getCategories();
    categories.value = cats;
  } catch (e) {
    console.error(e);
  }
}

async function loadAuctions() {
  try {
    loading.value = true;
    error.value = null;

    const Auctions = await getAllAuctions({
      // ici on ne filtre pas par status côté backend, on chargera tout
      // status: "running",
    });

    auctions.value = Auctions.map(mapAuctionToUi);
  } catch (e: any) {
    console.error(e);
    error.value = e.message ?? "Erreur inconnue";
  } finally {
    loading.value = false;
  }
}

const filteredAuctions = computed(() => {
  let result = auctions.value;

  if (selectedStatus.value !== "all") {
    result = result.filter((a) => a.status === selectedStatus.value);
  }

  // Filtrer par catégorie
  if (selectedCategory.value !== "all") {
    result = result.filter((a) => a.category === selectedCategory.value);
  }

  // Filtrer par recherche
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter((a) => a.title.toLowerCase().includes(q));
  }

  // Tri
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case "price-low":
        return a.price - b.price;
      case "price-high":
        return b.price - a.price;
      case "ending":
        if (!a.endTime || !b.endTime) return 0;
        return a.endTime.getTime() - b.endTime.getTime();
      default:
        return String(b.id).localeCompare(String(a.id));
    }
  });

  return result;
});

const activeAuctionsCount = computed(() =>
  filteredAuctions.value.filter((a) => a.status === "running").length
);

function viewAuction(id: string) {
  router.push(`/auction/${id}`);
}

onMounted(() => {
  loadCategories();
  loadAuctions();
});
</script>


<style scoped>
.home {
  animation: fadeIn 0.6s ease;
}

.hero {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
  border-radius: 16px;
  padding: 4rem 2rem;
  margin-bottom: 3rem;
  text-align: center;
  color: white;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-group select:focus {
  outline: none;
  border-color: #667eea;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 1rem;
}

.featured h2 {
  margin-bottom: 1.5rem;
  color: white;
  font-size: 2rem;
}

.auction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.no-results {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  color: #666;
  font-size: 1.2rem;
}

.info-section {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  margin-top: 3rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  color: #333;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2rem;
}

.step {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.step:hover {
  background: #f8f9ff;
  transform: translateY(-5px);
}

.step-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.step h3 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

.step p {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-stats {
    gap: 1.5rem;
  }
  
  .stat-number {
    font-size: 1.8rem;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .auction-grid {
    grid-template-columns: 1fr;
  }
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-state .spinner {
  font-size: 3rem;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #666;
  font-size: 1.1rem;
}
</style>
