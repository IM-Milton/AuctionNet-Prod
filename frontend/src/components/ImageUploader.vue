<template>
  <div class="image-uploader">
    <div class="upload-options">
      <div class="tab-buttons">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: uploadMode === 'file' }"
          @click="uploadMode = 'file'"
        >
          Uploader depuis le disque
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: uploadMode === 'url' }"
          @click="uploadMode = 'url'"
        >
          Depuis une URL
        </button>
      </div>

      <!-- Upload depuis le disque -->
      <div v-if="uploadMode === 'file'" class="upload-section">
        <div
          class="drop-zone"
          :class="{ 'drag-over': isDragging }"
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            multiple
            @change="handleFileSelect"
            style="display: none"
          />
          <div class="drop-zone-content">
            <span class="upload-icon">📤</span>
            <p><strong>Cliquez pour sélectionner des images</strong></p>
            <p class="hint">ou glissez-déposez vos fichiers ici</p>
            <p class="hint-small">
              PNG, JPG, JPEG, GIF (max {{ maxSizeMB }}MB par image)
            </p>
          </div>
        </div>

        <!-- Galerie d'images uploadées -->
        <div v-if="uploadedImages.length > 0" class="image-gallery">
          <div
            v-for="(image, index) in uploadedImages"
            :key="index"
            class="image-item"
            :class="{ 'is-main': index === mainImageIndex }"
          >
            <img :src="image.preview" :alt="`Image ${index + 1}`" />
            <div class="image-overlay">
              <button
                type="button"
                class="btn-icon btn-main"
                @click="setMainImage(index)"
                :title="
                  index === mainImageIndex
                    ? 'Image principale'
                    : 'Définir comme principale'
                "
              >
                {{ index === mainImageIndex ? "⭐" : "☆" }}
              </button>
              <button
                type="button"
                class="btn-icon btn-delete"
                @click="removeImage(index)"
                title="Supprimer"
              >
                🗑️
              </button>
            </div>
            <div v-if="index === mainImageIndex" class="main-badge">
              Image principale
            </div>
          </div>
        </div>

        <p v-if="uploadedImages.length > 0" class="images-count">
          {{ uploadedImages.length }} image(s) ajoutée(s)
          <span v-if="maxImages">(max {{ maxImages }})</span>
        </p>
      </div>

      <!-- Upload depuis URL -->
      <div v-else class="url-section">
        <div class="form-group">
          <label for="imageUrl">URL de l'image</label>
          <input
            type="url"
            id="imageUrl"
            v-model="imageUrl"
            placeholder="https://example.com/image.jpg"
            @blur="validateUrl"
          />
          <span class="hint">Collez l'URL d'une image hébergée en ligne</span>
        </div>

        <div v-if="imageUrl && !urlError" class="url-preview">
          <img
            :src="imageUrl"
            alt="Aperçu"
            @error="urlError = true"
            @load="urlError = false"
          />
        </div>

        <p v-if="urlError" class="error-message">
          ❌ Impossible de charger l'image depuis cette URL
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: [String, Array],
    default: "",
  },
  maxImages: {
    type: Number,
    default: 5,
  },
  maxSizeMB: {
    type: Number,
    default: 5,
  },
  returnType: {
    type: String,
    default: "url", // 'url' ou 'files'
    validator: (value) => ["url", "files"].includes(value),
  },
});

const emit = defineEmits(["update:modelValue"]);

const uploadMode = ref("file");
const fileInput = ref(null);
const uploadedImages = ref([]);
const mainImageIndex = ref(0);
const isDragging = ref(false);
const imageUrl = ref("");
const urlError = ref(false);

// Surveiller les changements du mode
watch(uploadMode, (newMode) => {
  if (newMode === "url" && imageUrl.value) {
    emit("update:modelValue", imageUrl.value);
  } else if (newMode === "file" && uploadedImages.value.length > 0) {
    if (props.returnType === "files") {
      emit("update:modelValue", uploadedImages.value);
    } else {
      emit(
        "update:modelValue",
        uploadedImages.value[mainImageIndex.value]?.preview || ""
      );
    }
  } else {
    emit("update:modelValue", "");
  }
});

// Surveiller l'URL
watch(imageUrl, (newUrl) => {
  if (uploadMode.value === "url" && newUrl && !urlError.value) {
    emit("update:modelValue", newUrl);
  }
});

// Surveiller les images uploadées
watch(
  [uploadedImages, mainImageIndex],
  () => {
    if (uploadMode.value === "file" && uploadedImages.value.length > 0) {
      if (props.returnType === "files") {
        emit("update:modelValue", uploadedImages.value);
      } else {
        emit(
          "update:modelValue",
          uploadedImages.value[mainImageIndex.value]?.preview || ""
        );
      }
    }
  },
  { deep: true }
);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  processFiles(files);
};

const handleDrop = (event) => {
  isDragging.value = false;
  const files = Array.from(event.dataTransfer.files);
  processFiles(files);
};

const processFiles = (files) => {
  const imageFiles = files.filter((file) => file.type.startsWith("image/"));

  if (
    props.maxImages &&
    uploadedImages.value.length + imageFiles.length > props.maxImages
  ) {
    alert(`Vous ne pouvez ajouter que ${props.maxImages} images maximum`);
    return;
  }

  imageFiles.forEach((file) => {
    // Vérifier la taille
    if (file.size > props.maxSizeMB * 1024 * 1024) {
      alert(`${file.name} est trop volumineux (max ${props.maxSizeMB}MB)`);
      return;
    }

    // Créer une prévisualisation
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedImages.value.push({
        file: file,
        preview: e.target.result,
        name: file.name,
        size: file.size,
      });
    };
    reader.readAsDataURL(file);
  });
};

const removeImage = (index) => {
  uploadedImages.value.splice(index, 1);

  // Ajuster l'index de l'image principale si nécessaire
  if (mainImageIndex.value >= uploadedImages.value.length) {
    mainImageIndex.value = Math.max(0, uploadedImages.value.length - 1);
  }

  if (uploadedImages.value.length === 0) {
    emit("update:modelValue", "");
  }
};

const setMainImage = (index) => {
  mainImageIndex.value = index;
};

const validateUrl = () => {
  if (imageUrl.value) {
    urlError.value = false;
  }
};
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: #f5f5f5;
  padding: 0.25rem;
  border-radius: 8px;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: #666;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: #e0e0e0;
}

.tab-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.drop-zone {
  border: 3px dashed #ccc;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: #667eea;
  background: #f0f4ff;
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.drop-zone p {
  margin: 0;
  color: #333;
}

.hint {
  color: #999;
  font-size: 0.9rem;
}

.hint-small {
  color: #999;
  font-size: 0.8rem;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
}

.image-item.is-main {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  transform: scale(1.1);
}

.btn-main:hover {
  background: #ffd700;
}

.btn-delete:hover {
  background: #ff4444;
}

.main-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
}

.images-count {
  margin-top: 1rem;
  text-align: center;
  color: #666;
  font-weight: 600;
}

.url-section {
  animation: fadeIn 0.3s ease;
}

.url-preview {
  margin-top: 1rem;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.url-preview img {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  background: #f5f5f5;
}

.error-message {
  color: #ff4444;
  margin-top: 0.5rem;
  font-weight: 600;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .image-gallery {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .drop-zone {
    padding: 2rem 1rem;
  }

  .upload-icon {
    font-size: 2rem;
  }
}
</style>
