<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>{{ isLogin ? 'Connexion' : 'Inscription' }}</h2>
        <p>{{ isLogin ? 'Bienvenue sur AuctioNet' : 'Créez votre compte' }}</p>
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
          <span v-else>{{ isLogin ? 'Se connecter' : "S'inscrire" }}</span>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const isLogin = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

function toggleMode() {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
  successMessage.value = ''
  form.value = {
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  }
}

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    // Validation pour l'inscription
    if (!isLogin.value) {
      if (form.value.password !== form.value.confirmPassword) {
        errorMessage.value = 'Les mots de passe ne correspondent pas !'
        isLoading.value = false
        return
      }
      
      if (form.value.password.length < 6) {
        errorMessage.value = 'Le mot de passe doit contenir au moins 6 caractères'
        isLoading.value = false
        return
      }
      
      if (!form.value.name.trim()) {
        errorMessage.value = 'Le nom est obligatoire'
        isLoading.value = false
        return
      }
    }

    if (isLogin.value) {
      // Connexion avec le backend
      const response = await api.login({
        email: form.value.email,
        password: form.value.password
      })
      
      // Récupérer les informations de l'utilisateur
      const userData = await api.getCurrentUser()
      
      // Sauvegarder les infos utilisateur dans localStorage
      localStorage.setItem('currentUser', JSON.stringify({
        id: userData.id,
        email: userData.email,
        balance: userData.balance,
        held: userData.held,
        purchases: userData.purchases
      }))
      
      successMessage.value = `Bienvenue !`
      
      setTimeout(() => {
        window.location.href = '/'
      }, 800)
    } else {
      // Inscription avec le backend
      const response = await api.register({
        email: form.value.email,
        password: form.value.password
      })
      
      // Connexion automatique après inscription
      await api.login({
        email: form.value.email,
        password: form.value.password
      })
      
      // Récupérer les informations de l'utilisateur
      const userData = await api.getCurrentUser()
      
      // Sauvegarder les infos utilisateur dans localStorage
      localStorage.setItem('currentUser', JSON.stringify({
        id: userData.id,
        email: userData.email,
        balance: userData.balance,
        held: userData.held,
        purchases: userData.purchases
      }))
      
      successMessage.value = `Compte créé avec succès ! Bienvenue !`
      
      setTimeout(() => {
        window.location.href = '/'
      }, 1000)
    }
  } catch (error) {
    console.error('Error:', error)
    errorMessage.value = error.message || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    isLoading.value = false
  }
}

function loginWithGoogle() {
  alert('Connexion avec Google - Fonctionnalité à venir')
}

function loginWithFacebook() {
  alert('Connexion avec Facebook - Fonctionnalité à venir')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 2rem 1rem;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  animation: fadeIn 0.5s ease;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h2 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.login-header p {
  color: #666;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.btn-submit {
  width: 100%;
  margin-top: 1rem;
  padding: 1rem;
  font-size: 1.05rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-submit:hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.login-footer p {
  color: #666;
  font-size: 0.95rem;
}

.toggle-link {
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s ease;
}

.toggle-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.social-login {
  margin-top: 2rem;
}

.divider {
  position: relative;
  text-align: center;
  margin: 1.5rem 0;
  color: #999;
  font-size: 0.9rem;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #e0e0e0;
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.divider span {
  background: white;
  padding: 0 1rem;
}

.social-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.btn-social {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-social:hover {
  border-color: #667eea;
  background: #f8f9ff;
  transform: translateY(-2px);
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-weight: 500;
  text-align: center;
  animation: slideDown 0.3s ease;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 2px solid #fcc;
}

.alert-success {
  background: #efe;
  color: #3a3;
  border: 2px solid #cfc;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }
  
  .social-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
