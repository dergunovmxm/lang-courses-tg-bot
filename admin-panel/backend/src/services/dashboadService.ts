// dashboardService.ts
import { db } from "../db";

export const dashboardService = {
  async getDashboardOverview(): Promise<any> {
    try {
      // Получаем общее количество пользователей
      const totalUsersResult = await db.query('SELECT COUNT(*) as count FROM users');
      const totalUsers = parseInt(totalUsersResult.rows[0].count) || 0;

      // Получаем статистику за текущий месяц
      const currentMonthStats = await this.getCurrentMonthStats();
      
      // Получаем статистику за предыдущий месяц
      const previousMonthStats = await this.getPreviousMonthStats();

      // Рассчитываем прирост
      const growthRate = currentMonthStats.count - previousMonthStats.count;

      return {
        totalUsers: totalUsers,
        currentMonthUsers: currentMonthStats.count,
        previousMonthUsers: previousMonthStats.count,
        // growthRate: growthRate,
        growthPercentage: previousMonthStats.count > 0 
          ? ((growthRate / previousMonthStats.count) * 100).toFixed(2)
          : currentMonthStats.count > 0 ? 100 : 0,
        currentMonthStart: currentMonthStats.startDate,
        currentMonthEnd: currentMonthStats.endDate,
        previousMonthStart: previousMonthStats.startDate,
        previousMonthEnd: previousMonthStats.endDate,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to fetch dashboard overview: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  async getUsersGrowth(): Promise<any> {
    try {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

      const newUsersResult = await db.query(
        'SELECT COUNT(*) as count FROM users WHERE created_at >= $1',
        [thirtyDaysAgo.toISOString()]
      );

      const newUsers = parseInt(newUsersResult.rows[0].count) || 0;

      // Получаем данные за предыдущий 30-дневный период
      const sixtyDaysAgo = new Date();
      sixtyDaysAgo.setDate(sixtyDaysAgo.getDate() - 60);
      
      const previousPeriodResult = await db.query(
        'SELECT COUNT(*) as count FROM users WHERE created_at >= $1 AND created_at < $2',
        [sixtyDaysAgo.toISOString(), thirtyDaysAgo.toISOString()]
      );
      const previousPeriodUsers = parseInt(previousPeriodResult.rows[0].count) || 0;

      const growthRate = newUsers - previousPeriodUsers;

      return {
        newUsersLast30Days: newUsers || 0,
        previousPeriodUsers: previousPeriodUsers || 0,
        growthRate,
        growthPercentage: previousPeriodUsers > 0 
          ? ((growthRate / previousPeriodUsers) * 100).toFixed(2)
          : newUsers && newUsers > 0 ? 100 : 0
      };
    } catch (error) {
      throw new Error(`Failed to get users growth: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  async getCurrentMonthStats(): Promise<{ count: number; startDate: string; endDate: string }> {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);

    const result = await db.query(
      'SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN $1 AND $2',
      [startOfMonth.toISOString(), endOfMonth.toISOString()]
    );

    const count = parseInt(result.rows[0].count) || 0;

    return {
      count: count || 0,
      startDate: startOfMonth.toISOString(),
      endDate: endOfMonth.toISOString()
    };
  },

  async getPreviousMonthStats(): Promise<{ count: number; startDate: string; endDate: string }> {
    const now = new Date();
    const startOfPreviousMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const endOfPreviousMonth = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59, 999);

    const result = await db.query(
      'SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN $1 AND $2',
      [startOfPreviousMonth.toISOString(), endOfPreviousMonth.toISOString()]
    );
    const count = parseInt(result.rows[0].count) || 0;

    return {
      count: count || 0,
      startDate: startOfPreviousMonth.toISOString(),
      endDate: endOfPreviousMonth.toISOString()
    };
  },

  // // Дополнительные методы для расширенной аналитики
  async getUsersGrowthTimeline(months: number = 6): Promise<any> {
    const timeline = [];
    
    for (let i = 0; i < months; i++) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      
      const startOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
      const endOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);

      const result = await db.query(
        'SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN $1 AND $2',
        [startOfMonth.toISOString(), endOfMonth.toISOString()]
      );
      const count = parseInt(result.rows[0].count) || 0;
      
      timeline.unshift({
        month: startOfMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
        count: count || 0,
        period: {
          start: startOfMonth.toISOString(),
          end: endOfMonth.toISOString()
        }
      });
    }

    return timeline;
  },

  async getDailyRegistrations(lastDays: number = 30): Promise<any> {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - lastDays);

    // Для daily статистики лучше использовать более сложный запрос с группировкой по дате
    const result = await db.query(
      `SELECT 
        DATE(created_at) as date,
        COUNT(*) as registrations
       FROM users 
       WHERE created_at >= $1
       GROUP BY DATE(created_at)
       ORDER BY date ASC`,
      [startDate.toISOString()]
    );

    // Преобразуем в объект с датами как ключами
    const dailyStats: { [key: string]: number } = {};
    let totalInPeriod = 0;
    
    result.rows.forEach(row => {
      const dateStr = new Date(row.date).toISOString().split('T')[0];
      dailyStats[dateStr] = parseInt(row.registrations);
      totalInPeriod += parseInt(row.registrations);
    });

    return {
      period: lastDays,
      startDate: startDate.toISOString(),
      endDate: new Date().toISOString(),
      dailyRegistrations: dailyStats,
      totalInPeriod
    };
  }
}