<template>
  <div class="sell-page">
    <div class="page-header">
      <h1>💰 Créer une enchère</h1>
      <p>Mettez votre produit en vente aux enchères</p>
    </div>

    <div class="form-container">
      <form @submit.prevent="submitAuction">
        <!-- Informations du produit -->
        <section class="form-section">
          <h2>📦 Informations du produit</h2>
          
          <div class="form-group">
            <label for="title">Titre de l'enchère *</label>
            <input
              type="text"
              id="title"
              v-model="form.title"
              placeholder="Ex: iPhone 15 Pro Max 256Go"
              required
            />
          </div>

          <div class="form-group">
            <label for="description">Description *</label>
            <textarea
              id="description"
              v-model="form.description"
              rows="6"
              placeholder="Décrivez votre produit en détail..."
              required
            ></textarea>
            <span class="hint">{{ form.description.length }}/1000 caractères</span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="category">Catégorie *</label>
              <select id="category" v-model="form.category" required>
                <option value="">Sélectionner une catégorie</option>
                <option value="electronics">📱 Électronique</option>
                <option value="fashion">👗 Mode</option>
                <option value="home">🏠 Maison</option>
                <option value="sports">⚽ Sport</option>
                <option value="art">🎨 Art</option>
                <option value="vehicles">🚗 Véhicules</option>
                <option value="other">📦 Autre</option>
              </select>
            </div>

            <div class="form-group">
              <label for="condition">État *</label>
              <select id="condition" v-model="form.condition" required>
                <option value="">Sélectionner l'état</option>
                <option value="new">✨ Neuf</option>
                <option value="like-new">🆕 Comme neuf</option>
                <option value="excellent">⭐ Excellent</option>
                <option value="good">👍 Bon</option>
                <option value="fair">👌 Acceptable</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Prix et enchères -->
        <section class="form-section">
          <h2>💵 Configuration de l'enchère</h2>
          
          <div class="form-row">
            <div class="form-group">
              <label for="startPrice">Prix de départ (€) *</label>
              <input
                type="number"
                id="startPrice"
                v-model.number="form.startPrice"
                min="1"
                step="1"
                placeholder="50"
                required
              />
            </div>

            <div class="form-group">
              <label for="minIncrement">Palier minimum (€) *</label>
              <input
                type="number"
                id="minIncrement"
                v-model.number="form.minIncrement"
                min="1"
                step="1"
                placeholder="5"
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="startDate">Date de début *</label>
              <input
                type="datetime-local"
                id="startDate"
                v-model="form.startDate"
                :min="minStartDate"
                required
              />
            </div>

            <div class="form-group">
              <label for="endDate">Date de fin *</label>
              <input
                type="datetime-local"
                id="endDate"
                v-model="form.endDate"
                :min="form.startDate"
                required
              />
            </div>
          </div>

          <div v-if="auctionDuration" class="duration-info">
            ⏱️ Durée de l'enchère : <strong>{{ auctionDuration }}</strong>
          </div>
        </section>

        <!-- Images -->
        <section class="form-section">
          <h2>📸 Images</h2>
          <div class="form-group">
            <label for="imageUrl">URL de l'image principale *</label>
            <input
              type="url"
              id="imageUrl"
              v-model="form.imageUrl"
              placeholder="https://example.com/image.jpg"
              required
            />
            <span class="hint">Entrez l'URL d'une image hébergée en ligne</span>
          </div>

          <div v-if="form.imageUrl" class="image-preview">
            <img :src="form.imageUrl" alt="Aperçu" @error="imageError = true" />
          </div>
        </section>

        <!-- Actions -->
        <div class="form-actions">
          <button type="button" @click="$router.push('/')" class="btn btn-secondary">
            Annuler
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isFormValid || isSubmitting">
            {{ isSubmitting ? '⏳ Création...' : '🚀 Créer l\'enchère' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const form = ref({
  title: '',
  description: '',
  category: '',
  condition: '',
  startPrice: null,
  minIncrement: 5,
  startDate: '',
  endDate: '',
  imageUrl: ''
})

const imageError = ref(false)

// Date minimum (maintenant + 1 heure)
const minStartDate = computed(() => {
  const date = new Date()
  date.setHours(date.getHours() + 1)
  return date.toISOString().slice(0, 16)
})

// Durée de l'enchère
const auctionDuration = computed(() => {
  if (!form.value.startDate || !form.value.endDate) return null
  
  const start = new Date(form.value.startDate)
  const end = new Date(form.value.endDate)
  const diff = end - start
  
  if (diff <= 0) return 'Dates invalides'
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  
  if (days > 0) return `${days} jour(s) et ${hours} heure(s)`
  return `${hours} heure(s)`
})

// Validation du formulaire
const isFormValid = computed(() => {
  return form.value.title &&
         form.value.description &&
         form.value.category &&
         form.value.condition &&
         form.value.startPrice > 0 &&
         form.value.minIncrement > 0 &&
         form.value.startDate &&
         form.value.endDate &&
         form.value.imageUrl &&
         auctionDuration.value !== 'Dates invalides'
})

const isSubmitting = ref(false)
const errorMessage = ref('')

async function submitAuction() {
  if (!isFormValid.value || isSubmitting.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    // Étape 1: Créer le produit
    const productData = {
      title: form.value.title,
      description: form.value.description,
      category: form.value.category,
      condition: form.value.condition,
      images: [form.value.imageUrl]
    }

    console.log('📦 Création produit:', productData)
    const productResponse = await api.createProduct(productData)
    console.log('✅ Produit créé:', productResponse)

    // Étape 2: Créer l'enchère avec le product_id
    const auctionData = {
      product_id: productResponse.id,
      start_price: form.value.startPrice,
      min_increment: form.value.minIncrement,
      start_at: new Date(form.value.startDate).toISOString(),
      end_at: new Date(form.value.endDate).toISOString()
    }

    console.log('📤 Création enchère:', auctionData)
    const auctionResponse = await api.createAuction(auctionData)
    console.log('✅ Enchère créée:', auctionResponse)

    alert('✅ Votre enchère a été créée avec succès !')
    router.push('/')
  } catch (error) {
    console.error('❌ Erreur création enchère:', error)
    errorMessage.value = error.message || 'Erreur lors de la création de l\'enchère'
    alert('❌ ' + errorMessage.value)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.sell-page {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
}

.form-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2.5rem;
  padding-bottom: 2.5rem;
  border-bottom: 2px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #999;
}

.duration-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #fff3cd;
  border-radius: 8px;
  text-align: center;
  color: #856404;
}

.image-preview {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e0e0e0;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #666;
}

.btn-secondary:hover:not(:disabled) {
  background: #d0d0d0;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .sell-page {
    padding: 1rem;
  }

  .form-container {
    padding: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
