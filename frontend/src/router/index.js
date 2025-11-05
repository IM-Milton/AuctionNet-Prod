import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AuctionViewTest from '../views/AuctionViewTest.vue'
import AuctionView from '../views/AuctionView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/auction/:id', name: 'auction', component: AuctionView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
