export type ModalConfig = {
  title: string;
  content: string | React.ReactNode;
  type?: 'info' | 'success' | 'warning' | 'danger';
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmLoading?: boolean;
  width?: number;
  okText?: string;
  cancelText?: string;
};

export type ModalState = ModalConfig & {
  visible: boolean;
  type: 'info' | 'success' | 'warning' | 'danger';
  confirmLoading: boolean;
};
