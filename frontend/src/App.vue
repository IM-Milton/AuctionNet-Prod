<template>
  <div>
    <Header />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<style>
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
}
</style>
