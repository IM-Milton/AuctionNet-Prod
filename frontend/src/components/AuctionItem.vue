<template>
  <div class="auction-card" @click="$emit('click')">
    <div class="image-wrapper">
      <img :src="auction.image"  class="auction-image" />

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

const countdownText = computed(() => {
  if (remainingMs.value <= 0) return "0 min";
  if (days.value > 0) return `${days.value}j ${hours.value}h`;
  if (hours.value > 0) return `${hours.value}h ${minutes.value}m`;
  return `${minutes.value} min`;
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

<style scoped>
.auction-card {
  position: relative;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease, translate 0.2s ease;
  display: flex;
  flex-direction: column;
}

.auction-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
}

.auction-image {
  width: 100%;
  height: 190px;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.auction-card:hover .auction-image {
  transform: scale(1.03);
}

/* Badge statut en haut à gauche */
.status-chip {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* Timer en bas de l'image */
.timer-chip {
  position: absolute;
  bottom: 0.75rem;
  left: 0.75rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 500;
  color: #fff;
  background: rgba(17, 24, 39, 0.85);
  backdrop-filter: blur(4px);
}

/* Couleurs du statut */
.status-scheduled {
  background: linear-gradient(135deg, #ffb347, #ffcc33);
}

.status-running {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.status-closed {
  background: #6c757d;
}

/* Corps de carte */
.auction-body {
  padding: 1rem 1.1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.auction-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2933;
  margin: 0;
  line-height: 1.4;
}

/* Ligne avec catégorie + nb d'enchères */
.auction-meta-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-pill {
  padding: 0.18rem 0.6rem;
  border-radius: 999px;
  background: #f1f3ff;
  color: #667eea;
  font-size: 0.78rem;
  font-weight: 500;
}

.bids {
  font-size: 0.8rem;
  color: #6b7280;
}

/* Bas de la carte : prix + statut mini */
.auction-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.4rem;
}

.price-block {
  display: flex;
  flex-direction: column;
}

.price-label {
  font-size: 0.78rem;
  color: #9ca3af;
}

.price-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: #667eea;
}

/* petit indicateur de statut à droite */
.status-dot-wrapper {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: #6b7280;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

/* couleurs dot */
.dot-scheduled {
  background: #ffb347;
}
.dot-running {
  background: #22c55e;
}
.dot-closed {
  background: #9ca3af;
}

.status-small-text {
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
</style>
