import React, { useEffect } from "react";
import { Form, Input, Select, InputNumber } from "antd";
import type { Task } from "../models/tasks";

const { TextArea } = Input;
const { Option } = Select;

interface CreateTaskFormProps {
  form?: any;
  initialValues?: Partial<Task>;
}

const CreateTaskForm: React.FC<CreateTaskFormProps> = ({
  form: externalForm,
  initialValues,
}) => {
  const [internalForm] = Form.useForm();
  const form = externalForm || internalForm;

  // Инициализация начальных значений
  useEffect(() => {
    if (initialValues) {
      // Преобразуем массив variants в строку для TextArea
      const formattedValues = {
        ...initialValues,
        variants: initialValues.variants?.join("\n") || "",
      };
      form.setFieldsValue(formattedValues);
    }
  }, [form, initialValues]);

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        type: "text",
        level: "easy",
        cost: 1,
        variants: "",
        ...initialValues,
      }}
    >
      <Form.Item<Task> label="Вопрос" name="question" rules={[]}>
        <Input placeholder="Введите вопрос задания" />
      </Form.Item>

      <Form.Item<Task> label="Ответ" name="answer" rules={[]}>
        <Input placeholder="Введите правильный ответ" />
      </Form.Item>

      <Form.Item<Task> label="Решение/Объяснение" name="solution" rules={[]}>
        <TextArea
          rows={3}
          placeholder="Подробное решение или объяснение ответа"
        />
      </Form.Item>

      <Form.Item<Task>
        label="Тема"
        name="theme"
        rules={[{ required: true, message: "Введите тему задания" }]}
      >
        <Input />
      </Form.Item>

      <Form.Item<Task>
        label="Тип задания"
        name="type"
        rules={[{ required: true, message: "Выберите тип задания" }]}
      >
        <Select placeholder="Выберите тип">
          <Option value="text">Текстовый</Option>
          <Option value="test">Тестовый</Option>
          <Option value="multiple">Множественный выбор</Option>
        </Select>
      </Form.Item>

      <Form.Item<Task>
        label="Уровень сложности"
        name="level"
        rules={[{ required: true, message: "Выберите уровень сложности" }]}
      >
        <Select placeholder="Выберите уровень">
          <Option value="easy">Легкий</Option>
          <Option value="medium">Средний</Option>
          <Option value="hard">Сложный</Option>
        </Select>
      </Form.Item>

      <Form.Item<Task>
        label="Варианты ответов (по одному на строку)"
        name="variants"
      >
        <TextArea rows={4} placeholder="Каждый вариант с новой строки" />
      </Form.Item>

      <Form.Item<Task> label="Стоимость (баллы)" name="cost" rules={[]}>
        <InputNumber min={1} max={100} style={{ width: "100%" }} />
      </Form.Item>
    </Form>
  );
};

export default CreateTaskForm;
