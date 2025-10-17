<script setup>
import { ref } from 'vue';

import Banner from './component/Banner.vue';
import NavAndMain from './component/NavAndMain.vue';
import ClassShadow from './component/ClassShadow.vue';
import NoteShadow from './component/NoteShadow.vue';

const showNewCourseModal = ref(false);
const showNewNoteModal = ref(false);

</script>

<template>
  <ClassShadow :visible="showNewCourseModal"/>
  <NoteShadow :visible="showNewNoteModal"/>
  <Banner />
  <NavAndMain @NewCourse="showNewCourseModal = true" @NewNote="showNewNoteModal = true"/>
</template>

<style scoped>
@reference "./style/index.css";
</style>
