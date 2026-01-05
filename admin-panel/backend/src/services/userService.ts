import { db } from "../db";

export const userService = {

  async getUsers(page: number = 1, limit: number = 10): Promise<any> {
    try {
      const offset = (page - 1) * limit;

      // Получаем пользователей с пагинацией
      const usersResult = await db.query(
        `SELECT * FROM users 
         ORDER BY created_at DESC 
         LIMIT $1 OFFSET $2`,
        [limit, offset]
      );

      // Получаем общее количество пользователей
      const countResult = await db.query('SELECT COUNT(*) as total FROM users');
      const totalCount = parseInt(countResult.rows[0].total) || 0;
      
      const totalPages = Math.ceil(totalCount / limit);

      return {
        users: usersResult.rows || [],
        count: totalCount,
        page,
        limit,
        totalPages
      };
    } catch (error) {
      console.error('Error in getUsers:', error);
      throw new Error(`Failed to fetch users: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },


  // async getUserById(id: string): Promise<User> {
  //   const { data: user, error } = await supabase
  //     .from('users')
  //     .select('*')
  //     .eq('id', id)
  //     .single();

  //   if (error) {
  //     throw new Error(`User not found: ${error.message}`);
  //   }

  //   return user;
  // },
} 