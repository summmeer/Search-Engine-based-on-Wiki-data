import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import Article from '@/components/Article'
import Query from '@/components/Query'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/search/:q/:t',
      name: 'Query',
      component: Query
    },
    {
      path: '/article/:id',
      name: 'Article',
      component: Article
    }
  ]
})
