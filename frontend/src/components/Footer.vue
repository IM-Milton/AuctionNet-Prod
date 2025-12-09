<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h3>⚡ AuctioNet</h3>
        <p>La plateforme d'enchères en ligne de confiance</p>
        <div class="social-links">
          <a href="#" class="social-link">📘 Facebook</a>
          <a href="#" class="social-link">📷 Instagram</a>
          <a href="#" class="social-link">🐦 Twitter</a>
        </div>
      </div>

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
      <p>Fait avec ❤️ en France</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-top: 4rem;
  padding: 3rem 2rem 1rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.footer-section h4 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.footer-section p {
  opacity: 0.9;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section ul li {
  margin-bottom: 0.5rem;
}

.footer-section ul li a {
  color: white;
  text-decoration: none;
  opacity: 0.9;
  transition: all 0.3s ease;
}

.footer-section ul li a:hover {
  opacity: 1;
  text-decoration: underline;
  padding-left: 5px;
}

.social-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.social-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.newsletter-form {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.newsletter-form input {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
}

.newsletter-form input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
}

.btn-subscribe {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-subscribe:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-bottom p {
  opacity: 0.9;
  margin: 0;
}

@media (max-width: 768px) {
  .footer {
    padding: 2rem 1rem 1rem;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
  
  .newsletter-form {
    flex-direction: column;
  }
}
</style>
