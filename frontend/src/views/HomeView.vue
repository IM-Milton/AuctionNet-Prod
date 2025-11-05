<template>
  <section>
    <h2>Enchères en cours</h2>
    <div class="auction-grid">
      <AuctionItem
        v-for="auction in auctions"
        :key="auction.id"
        :title="auction.title"
        :price="auction.price"
        :image="auction.image"
        @click="viewAuction(auction.id)"
      />
    </div>
  </section>
</template>

<script setup>
import AuctionItem from '../components/AuctionItem.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const auctions = [
  { id: 1, title: 'Montre Rolex Submariner', price: 3500, image: '/assets/images/rolex.jpg' },
  { id: 2, title: 'Vélo de course Canyon', price: 1200, image: '/assets/images/velo.jpg' },
  { id: 3, title: 'MacBook Pro 16"', price: 2100, image: '/assets/images/macbook.jpg' }
]

function viewAuction(id) {
  router.push(`/auction/${id}`)
}
</script>

<style scoped>
h2 {
  margin-bottom: 1.5rem;
}
.auction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}
</style>
