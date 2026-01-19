export type Timeline = {
  month: string, 
  count: number,
  period:{
    start:string,
    end:string
  }
}

export type Overview = {
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

export type Daily = {
  period: number;
  startDate: string;
  endDate: string;
  dailyRegistrations: Record<string, number>;
  totalInPeriod: number;
}

export type Growth =  {
  newUsersLast30Days: number;
  previousPeriodUsers: number;
  growthRate: number;
  growthPercentage: number;
}