<template>
  <div class="auction-card" @click="$emit('click')">
    <div class="image-wrapper">
      <img :src="auction.image" class="auction-image" />

      <!-- Badge statut -->
      <div class="status-chip" :class="statusClass">
        {{ statusText }}
      </div>

      <!-- Timer -->
      <div v-if="status !== 'closed' && hasTarget" class="timer-chip">
        <span v-if="status === 'scheduled'">
          ⏳ Commence dans {{ countdownText }}
        </span>
        <span v-else-if="status === 'running'">
          ⏰ Se termine dans {{ countdownText }}
        </span>
      </div>
    </div>

    <div class="auction-body">
      <h3 class="auction-title">{{ auction.title }}</h3>

      <div class="auction-meta-top">
        <span class="category-pill">{{ auction.category }}</span>
        <span class="bids">
          👥 {{ auction.bids }} enchère<span v-if="auction.bids !== 1">s</span>
        </span>
      </div>

      <!-- Afficher le gagnant si l'enchère est terminée -->
      <div
        v-if="status === 'closed' && auction.winner_username"
        class="winner-badge"
      >
        Gagnant: <strong>{{ auction.winner_username }}</strong>
      </div>

      <div class="auction-bottom">
        <div class="price-block">
          <span class="price-label">Prix actuel</span>
          <span class="price-value">{{ auction.price }} €</span>
        </div>

        <div class="status-dot-wrapper">
          <span class="status-dot" :class="statusDotClass"></span>
          <span class="status-small-text">{{ statusText }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

type StatusFilter = "all" | "scheduled" | "running" | "closed";

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
  winner_username?: string;
};

const props = defineProps<{
  auction: UiAuction;
}>();

defineEmits<{
  (e: "click"): void;
}>();

const now = ref(new Date());
let intervalId: number | undefined;

const status = computed<StatusFilter>(() => props.auction.status);

// Cible du compte à rebours
const targetTime = computed<Date | null>(() => {
  if (status.value === "scheduled") return props.auction.startTime;
  if (status.value === "running") return props.auction.endTime;
  return null;
});

const hasTarget = computed(() => !!targetTime.value);

const remainingMs = computed(() => {
  if (!targetTime.value) return 0;
  const diff = targetTime.value.getTime() - now.value.getTime();
  return Math.max(0, diff);
});

const days = computed(() =>
  Math.floor(remainingMs.value / (1000 * 60 * 60 * 24))
);
const hours = computed(() =>
  Math.floor((remainingMs.value % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
);
const minutes = computed(() =>
  Math.floor((remainingMs.value % (1000 * 60 * 60)) / (1000 * 60))
);
const seconds = computed(() =>
  Math.floor((remainingMs.value % (1000 * 60)) / 1000)
);

function z(n: number) {
  return n.toString().padStart(2, "0");
}

const countdownText = computed(() => {
  if (remainingMs.value <= 0) return "00s";
  if (days.value > 0)
    return `${days.value}j ${hours.value}h ${minutes.value}m ${z(
      seconds.value
    )}s`;
  if (hours.value > 0)
    return `${hours.value}h ${minutes.value}m ${z(seconds.value)}s`;
  return `${minutes.value}m ${z(seconds.value)}s`;
});

const statusText = computed(() => {
  switch (status.value) {
    case "scheduled":
      return "À venir";
    case "running":
      return "En cours";
    case "closed":
      return "Terminée";
    default:
      return "";
  }
});

const statusClass = computed(() => {
  return {
    "status-scheduled": status.value === "scheduled",
    "status-running": status.value === "running",
    "status-closed": status.value === "closed",
  };
});

const statusDotClass = computed(() => {
  return {
    "dot-scheduled": status.value === "scheduled",
    "dot-running": status.value === "running",
    "dot-closed": status.value === "closed",
  };
});

onMounted(() => {
  intervalId = window.setInterval(() => {
    now.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (intervalId) {
    window.clearInterval(intervalId);
  }
});
</script>

<style scoped src="./css/AuctionItem.css"></style>
