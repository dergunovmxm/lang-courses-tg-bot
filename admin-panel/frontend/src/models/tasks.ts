export type Task = {
  id: number,
  created_at: string,
  question: string,
  answer: string,
  solution: string,
  theme: string,
  type: string,
  level: string,
  variants: string[],
  cost: number
}