export type User = {
  id: number,
  telegram_id: number,
  username: string,
  first_name: string,
  last_name: string,
  language_code: string,
  created_at: string,
  updated_at: string,
  is_active: boolean,
  chat_id: number | null
}