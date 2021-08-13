import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import Diff from "../views/Diff.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/diff",
    name: "Diff",
    component: Diff
  }
];

const router = new VueRouter({
  routes
});

export default router;
