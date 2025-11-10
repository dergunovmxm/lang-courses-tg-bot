// controllers/dashboardController.ts
import { Request, Response } from 'express';
import { dashboardService } from '../services/dashboadService';

export const dashboardController = {
  /**
   * Получить основную статистику дашборда
   */
  async getDashboardOverview(req: Request, res: Response) {
    try {
      const dashboardData = await dashboardService.getDashboardOverview();
      
      res.json({
        success: true,
        data: dashboardData,
        message: 'Dashboard data retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching dashboard overview:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  },

  /**
   * Получить статистику роста пользователей
   */
  async getUsersGrowth(req: Request, res: Response) {
    try {
      const growthData = await dashboardService.getUsersGrowth();
      
      res.json({
        success: true,
        data: growthData,
        message: 'Users growth data retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching users growth:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  },

  /**
   * Получить таймлайн роста пользователей
   */
  async getGrowthTimeline(req: Request, res: Response) {
    try {
      const months = req.query.months ? parseInt(req.query.months as string) : 6;
      
      if (isNaN(months) || months < 1 || months > 24) {
        return res.status(400).json({
          success: false,
          data: null,
          message: 'Months parameter must be a number between 1 and 24'
        });
      }

      const timelineData = await dashboardService.getUsersGrowthTimeline(months);
      
      res.json({
        success: true,
        data: timelineData,
        message: 'Growth timeline retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching growth timeline:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  },

  /**
   * Получить ежедневную статистику регистраций
   */
  async getDailyRegistrations(req: Request, res: Response) {
    try {
      const days = req.query.days ? parseInt(req.query.days as string) : 30;
      
      if (isNaN(days) || days < 1 || days > 365) {
        return res.status(400).json({
          success: false,
          data: null,
          message: 'Days parameter must be a number between 1 and 365'
        });
      }

      const dailyData = await dashboardService.getDailyRegistrations(days);
      
      res.json({
        success: true,
        data: dailyData,
        message: 'Daily registrations data retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching daily registrations:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  },

  /**
   * Получить общую сводку дашборда (все данные одним запросом)
   */
  async getDashboardSummary(req: Request, res: Response) {
    try {
      const [overview, growth, timeline, daily] = await Promise.all([
        dashboardService.getDashboardOverview(),
        dashboardService.getUsersGrowth(),
        dashboardService.getUsersGrowthTimeline(6),
        dashboardService.getDailyRegistrations(30)
      ]);

      res.json({
        success: true,
        data: {
          overview,
          growth,
          timeline,
          daily
        },
        message: 'Dashboard summary retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  },

  /**
   * Получить минимальную статистику для виджета
   */
  async getWidgetStats(req: Request, res: Response) {
    try {
      const overview = await dashboardService.getDashboardOverview();
      
      // Формируем упрощенные данные для виджета
      const widgetData = {
        totalUsers: overview.totalUsers,
        currentMonthUsers: overview.currentMonthUsers,
        growthRate: overview.growthRate,
        growthPercentage: overview.growthPercentage,
        lastUpdated: overview.lastUpdated
      };

      res.json({
        success: true,
        data: widgetData,
        message: 'Widget stats retrieved successfully'
      });
    } catch (error) {
      console.error('Error fetching widget stats:', error);
      res.status(500).json({
        success: false,
        data: null,
        message: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  }
};