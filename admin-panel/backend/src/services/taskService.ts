import { db } from "../db";
import { Task } from "../models/tasks";

export const taskService = {
  async getAllTasks(page: number = 1, limit: number = 10): Promise<Task[]> {
    try {
      const offset = (page - 1) * limit;
      const tasks = await db.query(
        "SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        [limit, offset]
      );
      
      return tasks.rows;
    } catch (error) {
      console.error("Error fetching tasks:", error);
      throw error;
    }
  }
}