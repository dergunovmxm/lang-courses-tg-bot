import { useState, useCallback } from 'react';
import type { ModalConfig, ModalState } from '../models/modal';


export const usePortalModal = () => {
  const [modalState, setModalState] = useState<ModalState>({
    visible: false,
    title: '',
    content: '',
    type: 'info',
    onConfirm: undefined,
    onCancel: undefined,
    confirmLoading: false
  });

  const showModal = useCallback((config: ModalConfig) => {
    console.log('config', config)
    setModalState(prev => ({
      ...prev,
      visible: true,
      type: 'info',
      confirmLoading: false,
      ...config
    }));
  }, []);

  const hideModal = useCallback(() => {
    setModalState(prev => ({ ...prev, visible: false }));
  }, []);

  const updateModal = useCallback((updates: Partial<ModalState>) => {
    setModalState(prev => ({ ...prev, ...updates }));
  }, []);

  return {
    showModal,
    hideModal,
    updateModal,
    modalState,
    isVisible: modalState.visible
  };
};

export default usePortalModal;