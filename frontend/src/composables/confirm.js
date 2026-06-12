import { reactive } from "vue";

const state = reactive({
  visible: false,
  message: "",
  resolve: null,
});

export function showConfirm(message) {
  // 如果已有未完成的确认框，先拒绝它
  if (state.visible && state.resolve) {
    state.resolve(false);
  }
  return new Promise((resolve) => {
    state.message = message;
    state.visible = true;
    state.resolve = resolve;
  });
}

export function useConfirmState() {
  return state;
}
