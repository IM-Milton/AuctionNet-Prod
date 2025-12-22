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
import AuctionItem from "./AuctionItem.vue";

defineProps({
  title: {
    type: String,
    default: "Enchères",
  },
  subtitle: {
    type: String,
    default: "",
  },
  auctions: {
    type: Array,
    required: true,
  },
  showLoadMore: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["auction-click", "load-more"]);
</script>

<style scoped src="./css/AuctionList.css"></style>
