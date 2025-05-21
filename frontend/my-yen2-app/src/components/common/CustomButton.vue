<template>
  <button 
    class="custom-button" 
    :class="[type, { disabled: disabled }]" 
    :disabled="disabled"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'primary'
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click']);

const handleClick = (event: any) => {
  if (!props.disabled) {
    emit('click', event);
  }
};
</script>

<style lang="scss">
.custom-button {
  padding: 20rpx 30rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  text-align: center;
  border: none;
  outline: none;
  
  &.primary {
    background-color: #007aff;
    color: #ffffff;
  }
  
  &.secondary {
    background-color: #f8f8f8;
    color: #333333;
    border: 1px solid #dddddd;
  }
  
  &.success {
    background-color: #4cd964;
    color: #ffffff;
  }
  
  &.warning {
    background-color: #f0ad4e;
    color: #ffffff;
  }
  
  &.danger {
    background-color: #dd524d;
    color: #ffffff;
  }
  
  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}
</style>
