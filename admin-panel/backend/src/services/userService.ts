import { User } from "@supabase/supabase-js";
import { supabase } from "../db";

export const userService = {

  async getUsers(page: number = 1, limit: number = 10): Promise<any> {
    const start = (page - 1) * limit;
    const end = start + limit - 1;

    const { data: users, error, count } = await supabase
      .from('users')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(start, end);

    if (error) {
      throw new Error(`Failed to fetch users: ${error.message}`);
    }

    const totalCount = count || 0;
    const totalPages = Math.ceil(totalCount / limit);

    return {
      users: users || [],
      count: totalCount,
      page,
      limit,
      totalPages
    };
  },

  async getUserById(id: string): Promise<User> {
    const { data: user, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      throw new Error(`User not found: ${error.message}`);
    }

    return user;
  },
} 