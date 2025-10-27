<template>
  <div class="page-title q-mb-md">
    <div class="row items-center q-gutter-sm">
      <q-icon v-if="icon" :name="icon" :color="iconColor" size="md" />
      <h1 class="text-h4 q-my-none">{{ title }}</h1>
    </div>

    <p v-if="subtitle" class="text-subtitle1 text-grey-7 q-mt-sm q-mb-none">
      {{ subtitle }}
    </p>

    <q-separator v-if="separator" class="q-mt-md" />
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: '',
  },
  iconColor: {
    type: String,
    default: 'primary',
  },
  separator: {
    type: Boolean,
    default: true,
  },
})
</script>

<style lang="scss" scoped>
.page-title {
  h1 {
    font-weight: 500;
  }
}
</style>
