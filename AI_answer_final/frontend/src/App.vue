<template>
  <div class="layout">
    <header class="header">
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/chat">AI 对话</router-link>
      </nav>
    </header>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Arial, sans-serif;
}

.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  background: #1a73e8;
  padding: 14px;
}

.header nav {
  display: flex;
  gap: 20px;
}

.header a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.header a.router-link-active {
  font-weight: 700;
  text-decoration: underline;
}

.main {
  flex: 1;
  padding: 20px;
}
</style>