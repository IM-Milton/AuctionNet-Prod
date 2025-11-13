import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AuctionView from '../views/AuctionView.vue'
import LoginView from '../views/LoginView.vue'
import SellView from '../views/SellView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  { 
    path: '/', 
    name: 'home', 
    component: HomeView,
    meta: { title: 'Accueil - AuctioNet' }
  },
  { 
    path: '/auction/:id', 
    name: 'auction', 
    component: AuctionView,
    meta: { title: 'Détails de l\'enchère - AuctioNet' }
  },
  { 
    path: '/login', 
    name: 'login', 
    component: LoginView,
    meta: { title: 'Connexion - AuctioNet' }
  },
  { 
    path: '/sell', 
    name: 'sell', 
    component: SellView,
    meta: { title: 'Créer une enchère - AuctioNet' }
  },
  { 
    path: '/profile', 
    name: 'profile', 
    component: ProfileView,
    meta: { title: 'Mon Profil - AuctioNet' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// Mise à jour du titre de la page
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'AuctioNet - Enchères en ligne'
  next()
})

export default router
