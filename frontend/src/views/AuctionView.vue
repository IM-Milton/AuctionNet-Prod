<template>
  <div class="auction-detail">
    <img :src="auction.image" alt="Produit" class="image" />
    <div class="info">
      <h2>{{ auction.title }}</h2>
      <p class="price">Prix actuel : {{ auction.price }} €</p>
      <input
        type="number"
        v-model="bidAmount"
        placeholder="Montant de votre enchère"
        min="auction.price + 1"
      />
      <button @click="placeBid">Placer une enchère</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id

const auctions = {
  1: { title: 'Montre Rolex Submariner', price: 3500, image: '/assets/images/rolex.jpg' },
  2: { title: 'Vélo de course Canyon', price: 1200, image: '/assets/images/velo.jpg' },
  3: { title: 'MacBook Pro 16"', price: 2100, image: '/assets/images/macbook.jpg' }
}

const auction = auctions[id]
const bidAmount = ref(auction.price + 10)

function placeBid() {
  alert(`Enchère de ${bidAmount.value} € placée sur "${auction.title}" !`)
}
</script>

<style scoped>
.auction-detail {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.image {
  width: 400px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.info {
  flex: 1;
}
.price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #1976d2;
}
input {
  width: 100%;
  margin: 1rem 0;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}
button {
  background: #1976d2;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
button:hover {
  background: #125ca1;
}
</style>
