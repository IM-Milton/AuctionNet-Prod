<template>
  <div class="sell-page">
    <div class="page-header">
      <h1>Créer une enchère</h1>
      <p>Mettez votre produit en vente aux enchères</p>
    </div>

    <div class="form-container">
      <form @submit.prevent="submitAuction">
        <!-- Informations du produit -->
        <section class="form-section">
          <h2>Informations du produit</h2>

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
            <span class="hint"
              >{{ form.description.length }}/1000 caractères</span
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="category">Catégorie *</label>
              <select
                id="category"
                v-model="form.category"
                required
                :disabled="categoriesLoading"
              >
                <option value="">
                  {{
                    categoriesLoading
                      ? "Chargement..."
                      : "Sélectionner une catégorie"
                  }}
                </option>
                <option v-for="cat in categories" :key="cat" :value="cat">
                  {{ getCategoryLabel(cat) }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="condition">État *</label>
              <select id="condition" v-model="form.condition" required>
                <option value="">Sélectionner l'état</option>
                <option value="new">Neuf</option>
                <option value="like-new">Comme neuf</option>
                <option value="excellent">Excellent</option>
                <option value="good">Bon</option>
                <option value="fair">Acceptable</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Prix et enchères -->
        <section class="form-section">
          <h2>Configuration de l'enchère</h2>

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
            Durée de l'enchère : <strong>{{ auctionDuration }}</strong>
          </div>
        </section>

        <!-- Images -->
        <section class="form-section">
          <h2>Images</h2>
          <ImageUploader v-model="form.imageUrl" />
        </section>

        <!-- Actions -->
        <div class="form-actions">
          <button
            type="button"
            @click="$router.push('/')"
            class="btn btn-secondary"
          >
            Annuler
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="!isFormValid || isSubmitting"
          >
            {{ isSubmitting ? "Création..." : "Créer l'enchère" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";
import ImageUploader from "@/components/ImageUploader.vue";

const router = useRouter();

const form = ref({
  title: "",
  description: "",
  category: "",
  condition: "",
  startPrice: null,
  minIncrement: 5,
  startDate: "",
  endDate: "",
  imageUrl: "",
});

const imageError = ref(false);
const categories = ref([]);
const categoriesLoading = ref(true);

// Charger les catégories depuis le backend
async function loadCategories() {
  try {
    categoriesLoading.value = true;
    const data = await api.getCategories();
    categories.value = data.categories || [];
    console.log("Catégories chargées:", categories.value);
  } catch (error) {
    console.error("dureErreur chargement catégories:", error);
    // Fallback sur des catégories par défaut
    categories.value = [
      "electronique",
      "vehicule",
      "immobilier",
      "art",
      "autre",
    ];
  } finally {
    categoriesLoading.value = false;
  }
}

// Obtenir le label d'affichage pour une catégorie
function getCategoryLabel(category) {
  const labels = {
    electronique: "Électronique",
    vehicule: "Véhicules",
    immobilier: "Immobilier",
    art: "Art",
    autre: "Autre",
  };
  return labels[category] || category;
}

onMounted(() => {
  loadCategories();
});

// Date minimum (maintenant + 1 heure)
const minStartDate = computed(() => {
  const date = new Date();
  date.setHours(date.getHours() + 1);
  return date.toISOString().slice(0, 16);
});

// Durée de l'enchère
const auctionDuration = computed(() => {
  if (!form.value.startDate || !form.value.endDate) return null;

  const start = new Date(form.value.startDate);
  const end = new Date(form.value.endDate);
  const diff = end - start;

  if (diff <= 0) return "Dates invalides";

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (days > 0)
    return `${days} jour(s), ${hours} heure(s) et ${minutes} minute(s)`;
  if (hours > 0) return `${hours} heure(s) et ${minutes} minute(s)`;
  return `${minutes} minute(s)`;
});

// Validation du formulaire
const isFormValid = computed(() => {
  return (
    form.value.title &&
    form.value.description &&
    form.value.category &&
    form.value.condition &&
    form.value.startPrice > 0 &&
    form.value.minIncrement > 0 &&
    form.value.startDate &&
    form.value.endDate &&
    form.value.imageUrl &&
    auctionDuration.value !== "Dates invalides"
  );
});

const isSubmitting = ref(false);
const errorMessage = ref("");

async function submitAuction() {
  if (!isFormValid.value || isSubmitting.value) return;

  isSubmitting.value = true;
  errorMessage.value = "";

  try {
    // Étape 1: Créer le produit
    const productData = {
      title: form.value.title,
      description: form.value.description,
      category: form.value.category,
      condition: form.value.condition,
      images: [form.value.imageUrl],
    };

    console.log("Création produit:", productData);
    const productResponse = await api.createProduct(productData);
    console.log("Produit créé:", productResponse);

    // Étape 2: Créer l'enchère avec le product_id
    const auctionData = {
      product_id: productResponse.id,
      start_price: form.value.startPrice,
      min_increment: form.value.minIncrement,
      start_at: new Date(form.value.startDate).toISOString(),
      end_at: new Date(form.value.endDate).toISOString(),
    };

    console.log("Création enchère:", auctionData);
    const auctionResponse = await api.createAuction(auctionData);
    console.log("Enchère créée:", auctionResponse);

    alert("Votre enchère a été créée avec succès !");
    router.push("/");
  } catch (error) {
    console.error("Erreur création enchère:", error);
    errorMessage.value =
      error.message || "Erreur lors de la création de l'enchère";
    alert(errorMessage.value);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped src="./css/SellView.css"></style>
