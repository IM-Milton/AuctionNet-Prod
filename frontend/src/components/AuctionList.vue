<template>
  <div class="auction-list">
    <div class="list-header">
      <h2>{{ title }}</h2>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>

    <div class="auction-grid">
      <AuctionItem
        v-for="auction in auctions"
        :key="auction.id"
        :auction="auction"
        @click="$emit('auction-click', auction.id)"
      />
    </div>

    <div v-if="auctions.length === 0" class="empty-state">
      <span class="empty-icon">📦</span>
      <h3>Aucune enchère disponible</h3>
      <p>Revenez plus tard pour découvrir de nouvelles offres !</p>
    </div>

    <div v-if="showLoadMore && auctions.length > 0" class="load-more">
      <button @click="$emit('load-more')" class="btn btn-secondary">
        Charger plus d'enchères
      </button>
    </div>
  </div>
</template>

<script setup>
import AuctionItem from './AuctionItem.vue'

defineProps({
  title: {
    type: String,
    default: 'Enchères'
  },
  subtitle: {
    type: String,
    default: ''
  },
  auctions: {
    type: Array,
    required: true
  },
  showLoadMore: {
    type: Boolean,
    default: false
  }
})

defineEmits(['auction-click', 'load-more'])
</script>

<style scoped>
.auction-list {
  margin: 2rem 0;
}

.list-header {
  margin-bottom: 2rem;
}

.list-header h2 {
  font-size: 2rem;
  color: white;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
}

.auction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #666;
}

.load-more {
  text-align: center;
  margin-top: 3rem;
}

.load-more button {
  padding: 1rem 2rem;
  font-size: 1.05rem;
}

@media (max-width: 768px) {
  .auction-grid {
    grid-template-columns: 1fr;
  }
  
  .list-header h2 {
    font-size: 1.5rem;
  }
}
</style>
