<template>
  <div class="auction-item" @click="$emit('click')">
    <div class="image-container">
      <img :src="auction.image" :alt="auction.title" />
      <div class="badge" v-if="isEndingSoon">
        ⏰ Fin proche
      </div>
    </div>
    
    <div class="content">
      <h3 class="title">{{ auction.title }}</h3>
      
      <div class="info-row">
        <span class="price">{{ auction.price }} €</span>
        <span class="bids">👥 {{ auction.bids }} enchères</span>
      </div>
      
      <div class="timer" v-if="auction.endTime">
        <span>⏱️</span>
        <span>{{ timeRemaining }}</span>
      </div>
      
      <button class="btn-bid" @click.stop="$emit('click')">
        Enchérir maintenant
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  auction: {
    type: Object,
    required: true
  }
})

const now = ref(new Date())
let interval

onMounted(() => {
  interval = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const timeRemaining = computed(() => {
  if (!props.auction.endTime) return 'N/A'
  
  const diff = props.auction.endTime - now.value
  if (diff <= 0) return 'Terminé'
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  
  if (days > 0) return `${days}j ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m ${seconds}s`
})

const isEndingSoon = computed(() => {
  if (!props.auction.endTime) return false
  const diff = props.auction.endTime - now.value
  return diff > 0 && diff < 24 * 60 * 60 * 1000 // Moins de 24h
})
</script>

<style scoped>
.auction-item {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.auction-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.image-container {
  position: relative;
  overflow: hidden;
  height: 220px;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.auction-item:hover .image-container img {
  transform: scale(1.1);
}

.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff5252;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(255, 82, 82, 0.4);
}

.content {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.title {
  font-size: 1.1rem;
  color: #333;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.bids {
  font-size: 0.9rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.timer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #fff3cd;
  border-radius: 8px;
  font-weight: 600;
  color: #856404;
  font-size: 0.9rem;
}

.btn-bid {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: auto;
}

.btn-bid:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>
