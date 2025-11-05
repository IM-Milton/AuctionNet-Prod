<template>
  <div class="auction-item" @click="$emit('click')">
    <img :src="image" alt="Produit" />
    <h3>{{ title }}</h3>
    <p>{{ price }} €</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  price: Number,
  image: String
})
</script>

<style scoped>
.auction-item {
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  background: white;
  cursor: pointer;
  transition: 0.2s;
}
.auction-item:hover {
  transform: scale(1.03);
}
img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}
h3 {
  margin: 0.5rem;
}
p {
  color: #1976d2;
  margin: 0 0.5rem 1rem;
}
</style>
