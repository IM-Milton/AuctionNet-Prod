<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>{{ isLogin ? "Connexion" : "Inscription" }}</h2>
        <p>{{ isLogin ? "Bienvenue sur AuctioNet" : "Créez votre compte" }}</p>
      </div>

      <!-- Messages d'erreur et succès -->
      <div v-if="errorMessage" class="alert alert-error">
        ❌ {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success">
        ✅ {{ successMessage }}
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group" v-if="!isLogin">
          <label for="name">Nom complet *</label>
          <input
            type="text"
            id="name"
            v-model="form.name"
            placeholder="John Doe"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">Email *</label>
          <input
            type="email"
            id="email"
            v-model="form.email"
            placeholder="votre@email.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Mot de passe *</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            :placeholder="isLogin ? '••••••••' : 'Min. 6 caractères'"
            :minlength="isLogin ? 1 : 6"
            required
          />
        </div>

        <div class="form-group" v-if="!isLogin">
          <label for="confirmPassword">Confirmer le mot de passe *</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="form.confirmPassword"
            placeholder="••••••••"
            minlength="6"
            required
          />
        </div>

        <button type="submit" class="btn btn-submit" :disabled="isLoading">
          <span v-if="isLoading">⏳ Chargement...</span>
          <span v-else>{{ isLogin ? "Se connecter" : "S'inscrire" }}</span>
        </button>
      </form>

      <div class="login-footer">
        <p>
          {{ isLogin ? "Pas encore de compte ?" : "Déjà un compte ?" }}
          <a @click="toggleMode" class="toggle-link">
            {{ isLogin ? "S'inscrire" : "Se connecter" }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();
const isLogin = ref(true);
const errorMessage = ref("");
const successMessage = ref("");
const isLoading = ref(false);

const form = ref({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
});

function toggleMode() {
  isLogin.value = !isLogin.value;
  errorMessage.value = "";
  successMessage.value = "";
  form.value = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  };
}

async function handleSubmit() {
  errorMessage.value = "";
  successMessage.value = "";
  isLoading.value = true;

  try {
    // Validation pour l'inscription
    if (!isLogin.value) {
      if (form.value.password !== form.value.confirmPassword) {
        errorMessage.value = "Les mots de passe ne correspondent pas !";
        isLoading.value = false;
        return;
      }

      if (form.value.password.length < 6) {
        errorMessage.value =
          "Le mot de passe doit contenir au moins 6 caractères";
        isLoading.value = false;
        return;
      }

      if (!form.value.name.trim()) {
        errorMessage.value = "Le nom est obligatoire";
        isLoading.value = false;
        return;
      }
    }

    if (isLogin.value) {
      // Connexion avec le backend
      const response = await api.login({
        email: form.value.email,
        password: form.value.password,
      });

      // Récupérer les informations de l'utilisateur
      const userData = await api.getCurrentUser();

      // Sauvegarder les infos utilisateur dans localStorage
      localStorage.setItem(
        "currentUser",
        JSON.stringify({
          id: userData.id,
          email: userData.email,
          balance: userData.balance,
          held: userData.held,
          purchases: userData.purchases,
        })
      );

      successMessage.value = `Bienvenue !`;

      setTimeout(() => {
        window.location.href = "/";
      }, 800);
    } else {
      // Inscription avec le backend
      const response = await api.register({
        email: form.value.email,
        password: form.value.password,
      });

      // Connexion automatique après inscription
      await api.login({
        email: form.value.email,
        password: form.value.password,
      });

      // Récupérer les informations de l'utilisateur
      const userData = await api.getCurrentUser();

      // Sauvegarder les infos utilisateur dans localStorage
      localStorage.setItem(
        "currentUser",
        JSON.stringify({
          id: userData.id,
          email: userData.email,
          balance: userData.balance,
          held: userData.held,
          purchases: userData.purchases,
        })
      );

      successMessage.value = `Compte créé avec succès ! Bienvenue !`;

      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    }
  } catch (error) {
    console.error("Error:", error);
    errorMessage.value =
      error.message || "Une erreur est survenue. Veuillez réessayer.";
  } finally {
    isLoading.value = false;
  }
}

function loginWithGoogle() {
  alert("Connexion avec Google - Fonctionnalité à venir");
}

function loginWithFacebook() {
  alert("Connexion avec Facebook - Fonctionnalité à venir");
}
</script>

<style scoped src="./css/LoginView.css"></style>
