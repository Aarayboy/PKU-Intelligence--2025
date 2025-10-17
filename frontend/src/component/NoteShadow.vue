<script setup>
const props = defineProps({visible : Boolean});

</script>

<template>
      <div v-show="visible" class="global-mask">
        <div class="loader-content">
            <div class="custom-spinner"></div> <!-- 替换成你的品牌动画 -->
            <p class="text">加载中，请稍候...</p>
        </div>
    </div>
</template>

<style scoped>
.global-mask {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    /* 品牌主色调遮罩 */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.loader-content {
    text-align: center;
    color: white;
}

.custom-spinner {
    /* 自定义旋转动画实现 */
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 10px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

</style>