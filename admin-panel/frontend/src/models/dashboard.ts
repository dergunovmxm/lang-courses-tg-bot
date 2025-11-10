export interface Timeline {
  month: string, 
  count: number,
  period:{
    start:string,
    end:string
  }
}

export interface Overview {
  totalUsers: number;
  currentMonthUsers: number;
  previousMonthUsers: number;
  growthRate: number;
  growthPercentage: string;
  currentMonthStart: string;
  currentMonthEnd: string;
  previousMonthStart: string;
  previousMonthEnd: string;
  lastUpdated: string;
}

export interface Daily {
  period: number;
  startDate: string;
  endDate: string;
  dailyRegistrations: Record<string, number>;
  totalInPeriod: number;
}

export interface Growth {
  newUsersLast30Days: number;
  previousPeriodUsers: number;
  growthRate: number;
  growthPercentage: number;
}