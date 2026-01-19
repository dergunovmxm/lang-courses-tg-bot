import { Request, Response } from 'express';
import { userService } from '../services/userService';

export const userController = {
  async getUsers(req: Request, res: Response) {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;
      const search = req.query.search as string;
      const result = await userService.getUsers(page, limit);

      // TODO добавить когда будет поиск
      // if (search) {
      //   result = await userService.searchUsers(search, page, limit);
      // } else {
      //   result = await userService.getUsers(page, limit);
      // }
      res.json({ success: true, data: result });
    } catch (error: any) {
      console.error('Error in getUsers:', error);
      res.status(500).json({ success: false, error: error.message });
    }
  },
}