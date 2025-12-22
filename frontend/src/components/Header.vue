<template>
  <header class="header">
    <div class="header-content">
      <router-link to="/" class="logo">
        <span class="logo-text">AuctioNet</span>
      </router-link>

      <nav class="nav">
        <router-link to="/" class="nav-link">
          <span class="nav-text">Accueil</span>
        </router-link>

        <!-- Si connecté -->
        <template v-if="currentUser">
          <router-link to="/profile" class="nav-link">
            <span>👤</span>
            <span class="nav-text">{{ currentUser.email }}</span>
          </router-link>
          <router-link to="/sell" class="btn-sell">
            <span class="nav-text">Vendre</span>
          </router-link>
          <button @click="logout" class="btn-logout">
            <span class="nav-text">Déconnexion</span>
          </button>
        </template>

        <!-- Si non connecté -->
        <template v-else>
          <router-link to="/login" class="btn-login">
            <span class="nav-text">Connexion</span>
          </router-link>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();
const currentUser = ref(null);

onMounted(() => {
  loadCurrentUser();
});

function loadCurrentUser() {
  const user = localStorage.getItem("currentUser");
  if (user) {
    currentUser.value = JSON.parse(user);
  }
}

function logout() {
  if (confirm("Êtes-vous sûr de vouloir vous déconnecter ?")) {
    api.logout(); // Supprime le token et les données utilisateur
    currentUser.value = null;
    router.push("/");
    window.location.reload();
  }
}
</script>

<style scoped src="./css/Header.css"></style>
