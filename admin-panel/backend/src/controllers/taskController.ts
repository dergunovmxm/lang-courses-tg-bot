import { Request, Response } from 'express';
import { taskService  } from '../services/taskService';

export const taskController = {
  async getAllTasks(req: Request, res: Response) {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;
      const result = await taskService.getAllTasks(page, limit);
      res.json({ success: true, data: result});

    } catch(error: any) {
      console.error('Error in getAllTasks:', error);
      res.status(500).json({ success: false, error: error.message });
    }
  }
}
