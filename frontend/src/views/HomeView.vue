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
        </div>
      </div>
    </section>

    <!-- Filtres -->
    <section class="filters">
      <div class="filter-group">
        <label>Catégorie :</label>
        <select v-model="selectedCategory">
          <option value="all">Toutes</option>
          <option v-for="cat in categories" :key="cat" :value="cat">
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
      <h2>Enchères {{ loading ? "en chargement..." : "en vedette" }}</h2>

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
        <p>Aucune enchère ne correspond à vos critères</p>
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
import { ref, computed, onMounted, onActivated, onBeforeUnmount } from "vue";
import AuctionItem from "../components/AuctionItem.vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();

const selectedCategory = ref("all");
const selectedStatus = ref("running");
const sortBy = ref("recent");
const searchQuery = ref("");
const auctions = ref([]);
const loading = ref(true);
const categories = ref([]);
let expirationCheckInterval = null;

// Helper pour obtenir l'URL d'une image
function getImageUrl(images) {
  if (!images || images.length === 0) {
    return "/assets/images/placeholder.jpg";
  }

  const img = images[0];
  if (!img) return "/assets/images/placeholder.jpg";

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

  return "/assets/images/placeholder.jpg";
}

// Charger les enchères depuis le backend
async function loadAuctions() {
  try {
    loading.value = true;
    const filters = {};

    if (selectedCategory.value !== "all") {
      filters.category = selectedCategory.value;
    }

    const data = await api.getAuctions(filters);

    // Adapter les données du backend au format attendu par le frontend
    auctions.value =
      data.auctions?.map((auction) => ({
        id: auction.id,
        title: auction.product?.title || "Sans titre",
        price: auction.current_price || auction.start_price,
        image: getImageUrl(auction.product?.images),
        category: auction.product?.category || "other",
        startTime: auction.start_at ? new Date(auction.start_at) : null,
        endTime: new Date(auction.end_at),
        bids: auction.bids_count || 0,
        status: auction.status,
        winner_username: auction.winner_username,
      })) || [];
  } catch (error) {
    console.error("Erreur lors du chargement des enchères:", error);
    // Fallback sur des données simulées en cas d'erreur
    auctions.value = [
      {
        id: 1,
        title: "Montre Rolex Submariner",
        price: 3500,
        image: "/assets/images/rolex.jpg",
        category: "fashion",
        endTime: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
        bids: 23,
      },
      {
        id: 2,
        title: "Vélo de course Canyon",
        price: 1200,
        image: "/assets/images/velo.jpg",
        category: "sports",
        endTime: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
        bids: 15,
      },
      {
        id: 3,
        title: 'MacBook Pro 16"',
        price: 2100,
        image: "/assets/images/macbook.jpg",
        category: "electronics",
        endTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
        bids: 42,
      },
      {
        id: 4,
        title: "iPhone 15 Pro Max",
        price: 950,
        image: "/assets/images/iphone.jpg",
        category: "electronics",
        endTime: new Date(Date.now() + 5 * 60 * 60 * 1000),
        bids: 67,
      },
      {
        id: 5,
        title: "Sac Hermès Birkin",
        price: 8500,
        image: "/assets/images/hermes.jpg",
        category: "fashion",
        endTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        bids: 89,
      },
      {
        id: 6,
        title: "Tableau Abstrait Original",
        price: 750,
        image: "/assets/images/art.jpg",
        category: "art",
        endTime: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000),
        bids: 12,
      },
    ];
  } finally {
    loading.value = false;
  }
}

// Charger les catégories
async function loadCategories() {
  try {
    const data = await api.getCategories();
    categories.value = data.categories || [];
  } catch (error) {
    console.error("Erreur lors du chargement des catégories:", error);
  }
}

onMounted(async () => {
  console.log("🏠 HomeView: Mounted");
  try {
    await Promise.all([loadAuctions(), loadCategories()]);
    console.log("✅ HomeView: Data loaded successfully");
    startExpirationCheck();
  } catch (error) {
    console.error("❌ HomeView: Error loading data:", error);
  }
});

// Recharger les enchères quand on revient sur la page
onActivated(async () => {
  console.log("🔄 HomeView: Activated - Rechargement des enchères");
  await loadAuctions();
  startExpirationCheck();
});

// Vérifier les changements de statut des enchères toutes les 5 secondes
function checkExpiredAuctions() {
  const now = new Date().getTime();
  let hasChanged = false;

  auctions.value = auctions.value.map((auction) => {
    // Vérifier si une enchère "en cours" est expirée
    if (auction.status === "running" && auction.endTime) {
      const endTime = new Date(auction.endTime).getTime();
      if (now >= endTime) {
        console.log(
          `⏰ Enchère ${auction.id} expirée, statut: running -> closed`
        );
        hasChanged = true;
        return { ...auction, status: "closed" };
      }
    }

    return auction;
  });

  // Si des enchères ont changé de statut, recharger depuis le backend pour sync (mais une seule fois)
  if (hasChanged) {
    console.log("🔄 Rechargement des enchères suite à changement de statut");
    // Arrêter l'intervalle temporairement pour éviter les boucles
    stopExpirationCheck();
    loadAuctions().then(() => {
      // Redémarrer l'intervalle après le rechargement
      startExpirationCheck();
    });
  }
}

function startExpirationCheck() {
  // Nettoyer l'ancien intervalle s'il existe
  if (expirationCheckInterval) {
    clearInterval(expirationCheckInterval);
  }
  // Vérifier toutes les 5 secondes (au lieu de 1 seconde pour éviter les boucles)
  expirationCheckInterval = setInterval(checkExpiredAuctions, 5000);
  console.log("✅ Vérification d'expiration démarrée (toutes les 5 secondes)");
}

function stopExpirationCheck() {
  if (expirationCheckInterval) {
    clearInterval(expirationCheckInterval);
    expirationCheckInterval = null;
    console.log("🛑 Vérification d'expiration arrêtée");
  }
}

onBeforeUnmount(() => {
  stopExpirationCheck();
});

// Computed: filtrer et trier les enchères
const filteredAuctions = computed(() => {
  let result = auctions.value;

  // Filtrer par statut
  if (selectedStatus.value !== "all") {
    result = result.filter((a) => a.status === selectedStatus.value);
  }

  // Filtrer par catégorie
  if (selectedCategory.value !== "all") {
    result = result.filter((a) => a.category === selectedCategory.value);
  }

  // Filtrer par recherche
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter((a) => a.title.toLowerCase().includes(query));
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
        return b.id - a.id;
    }
  });

  return result;
});

const activeAuctionsCount = computed(
  () => filteredAuctions.value.filter((a) => a.status === "running").length
);

function viewAuction(id) {
  router.push(`/auction/${id}`);
}
</script>

<style scoped src="./css/HomeView.css"></style>
