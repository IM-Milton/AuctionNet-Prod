<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getAllAuctions } from "../services/auctions";
import type { Auction } from "../models/auction";

const auctions = ref<Auction[]>([]);
onMounted(async () => { auctions.value = await getAllAuctions(); });
</script>

<template>
  <div v-for="a in auctions" :key="a.product_id">
    <img v-if="img(a)" :src="img(a)" style="width:200px" />
    <div>{{ a.product?.title ?? ('Produit ' + a.product_id) }}</div>
    <div>Prix actuel : {{  a.start_price }} €</div>
  </div>
</template>
