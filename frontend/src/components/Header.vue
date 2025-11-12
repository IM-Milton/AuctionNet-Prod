<template>
  <header class="header">
    <div class="header-content">
      <router-link to="/" class="logo">
        <span class="logo-icon">⚡</span>
        <span class="logo-text">AuctioNet</span>
      </router-link>
      
      <nav class="nav">
        <router-link to="/" class="nav-link">
          <span>🏠</span> Accueil
        </router-link>
        <router-link to="/login" class="nav-link">
          <span>👤</span> Connexion
        </router-link>
        <button class="btn-sell">
          <span>💰</span> Vendre
        </button>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #1976d2;
  font-size: 1.5rem;
  font-weight: 700;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
  text-decoration: none;
}

.logo-icon {
  font-size: 2rem;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #555;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f0f0f0;
  color: #1976d2;
  text-decoration: none;
}

.nav-link.router-link-active {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-sell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-sell:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }
  
  .nav {
    gap: 0.75rem;
  }
  
  .nav-link span,
  .btn-sell span {
    display: none;
  }
}
</style>
