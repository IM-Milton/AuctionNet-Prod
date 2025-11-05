<template>
  <header class="header">
    <h1 class="logo">🕑 AuctioNet</h1>
    <nav>
      <router-link to="/">Accueil</router-link>
    </nav>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1976d2;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.logo {
  font-weight: bold;
}
nav a {
  color: white;
  text-decoration: none;
  margin-left: 1rem;
}
nav a:hover {
  text-decoration: underline;
}
</style>
