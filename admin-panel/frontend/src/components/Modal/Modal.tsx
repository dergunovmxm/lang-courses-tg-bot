import React from "react";
import ReactDOM from "react-dom";
import { Modal } from "antd";
import {
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import type { ModalState } from "../../models/modal";

interface PortalModalProps {
  modalState: ModalState;
  hideModal: () => void;
}

const PortalModal: React.FC<PortalModalProps> = ({ modalState, hideModal }) => {
  const modalRoot = document.getElementById("modal-root");

  if (!modalRoot || !modalState.visible) return null;

  const icons = {
    info: <InfoCircleOutlined style={{ color: "#1890ff", fontSize: 24 }} />,
    success: <CheckCircleOutlined style={{ color: "#52c41a", fontSize: 24 }} />,
    warning: (
      <ExclamationCircleOutlined style={{ color: "#faad14", fontSize: 24 }} />
    ),
    danger: (
      <ExclamationCircleOutlined style={{ color: "#ff4d4f", fontSize: 24 }} />
    ),
  };

  const handleOk = () => {
    if (modalState.onConfirm) {
      modalState.onConfirm();
    }
  };

  const handleCancel = () => {
    if (modalState.onCancel) {
      modalState.onCancel();
    }
    hideModal();
  };

  return ReactDOM.createPortal(
    <Modal
      title={modalState.title}
      open={modalState.visible}
      onOk={handleOk}
      onCancel={handleCancel}
      confirmLoading={modalState.confirmLoading}
      okText={modalState.okText || "Подтвердить"}
      cancelText={modalState.cancelText || "Отмена"}
      okType={modalState.type === "danger" ? "danger" : "primary"}
      closable={true}
      maskClosable={false}
      width={modalState.width || 520}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
        {icons[modalState.type]}
        <div style={{ flex: 1 }}>
          {typeof modalState.content === "string" ? (
            <p style={{ margin: 0 }}>{modalState.content}</p>
          ) : (
            modalState.content
          )}
        </div>
      </div>
    </Modal>,
    modalRoot
  );
};

export default PortalModal;
