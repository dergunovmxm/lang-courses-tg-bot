// dashboardService.ts
import { supabase } from "../db";

export const dashboardService = {
  async getDashboardOverview(): Promise<any> {
    try {
      // Получаем общее количество пользователей
      const { count: totalUsers, error: usersError } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true });

      if (usersError) {
        throw new Error(`Failed to get users count: ${usersError.message}`);
      }

      // Получаем статистику за текущий месяц
      const currentMonthStats = await this.getCurrentMonthStats();
      
      // Получаем статистику за предыдущий месяц
      const previousMonthStats = await this.getPreviousMonthStats();

      // Рассчитываем прирост
      const growthRate = await this.calculateGrowthRate(previousMonthStats.count, currentMonthStats.count);

      return {
        totalUsers: totalUsers || 0,
        currentMonthUsers: currentMonthStats.count || 0,
        previousMonthUsers: previousMonthStats.count || 0,
        growthRate: growthRate,
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

      const { count: newUsers, error } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', thirtyDaysAgo.toISOString());

      if (error) {
        throw new Error(`Failed to get users growth: ${error.message}`);
      }

      // Получаем данные за предыдущий 30-дневный период
      const sixtyDaysAgo = new Date();
      sixtyDaysAgo.setDate(sixtyDaysAgo.getDate() - 60);
      
      const { count: previousPeriodUsers } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', sixtyDaysAgo.toISOString())
        .lt('created_at', thirtyDaysAgo.toISOString());

      const growthRate = await this.calculateGrowthRate(previousPeriodUsers || 0, newUsers || 0);

      return {
        newUsersLast30Days: newUsers || 0,
        previousPeriodUsers: previousPeriodUsers || 0,
        growthRate: growthRate,
        growthPercentage: previousPeriodUsers && previousPeriodUsers > 0 
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

    const { count, error } = await supabase
      .from('users')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', startOfMonth.toISOString())
      .lte('created_at', endOfMonth.toISOString());

    if (error) {
      throw new Error(`Failed to get current month stats: ${error.message}`);
    }

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

    const { count, error } = await supabase
      .from('users')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', startOfPreviousMonth.toISOString())
      .lte('created_at', endOfPreviousMonth.toISOString());

    if (error) {
      throw new Error(`Failed to get previous month stats: ${error.message}`);
    }

    return {
      count: count || 0,
      startDate: startOfPreviousMonth.toISOString(),
      endDate: endOfPreviousMonth.toISOString()
    };
  },

  async calculateGrowthRate(previousCount: number, currentCount: number): Promise<number> {
    return currentCount - previousCount;
  },

  // Дополнительные методы для расширенной аналитики
  async getUsersGrowthTimeline(months: number = 6): Promise<any> {
    const timeline = [];
    
    for (let i = 0; i < months; i++) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      
      const startOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
      const endOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);

      const { count } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', startOfMonth.toISOString())
        .lte('created_at', endOfMonth.toISOString());

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
    const { data, error } = await supabase
      .from('users')
      .select('created_at')
      .gte('created_at', startDate.toISOString())
      .order('created_at', { ascending: true });

    if (error) {
      throw new Error(`Failed to get daily registrations: ${error.message}`);
    }

    // Группируем по дням
    const dailyStats: { [key: string]: number } = {};
    
    data?.forEach(user => {
      const date = new Date(user.created_at).toISOString().split('T')[0];
      dailyStats[date] = (dailyStats[date] || 0) + 1;
    });

    return {
      period: lastDays,
      startDate: startDate.toISOString(),
      endDate: new Date().toISOString(),
      dailyRegistrations: dailyStats,
      totalInPeriod: data?.length || 0
    };
  }
}