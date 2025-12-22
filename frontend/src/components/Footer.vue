<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h4>Navigation</h4>
        <ul>
          <li><router-link to="/">Accueil</router-link></li>
          <li><router-link to="/login">Connexion</router-link></li>
          <li><a href="#categories">Catégories</a></li>
          <li><a href="#about">À propos</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>Aide & Support</h4>
        <ul>
          <li><a href="#faq">FAQ</a></li>
          <li><a href="#contact">Contact</a></li>
          <li><a href="#conditions">Conditions d'utilisation</a></li>
          <li><a href="#privacy">Confidentialité</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>Newsletter</h4>
        <p>Recevez nos meilleures offres</p>
        <div class="newsletter-form">
          <input type="email" placeholder="Votre email" />
          <button class="btn-subscribe">S'abonner</button>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; 2025 AuctioNet. Tous droits réservés.</p>
    </div>
  </footer>
</template>

<style scoped src="./css/Footer.css"></style>
