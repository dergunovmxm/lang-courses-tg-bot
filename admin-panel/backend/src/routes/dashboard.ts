// routes/dashboardRoutes.ts
import { Router } from 'express';
import { dashboardController } from '../controllers/dashboardController';

const router = Router();

/**
 * @route GET /api/dashboard/overview
 * @desc Получить основную статистику дашборда
 * @access Private/Public (в зависимости от ваших требований)
 */
router.get('/overview', dashboardController.getDashboardOverview);

/**
 * @route GET /api/dashboard/growth
 * @desc Получить статистику роста пользователей
 * @access Private/Public
 */
router.get('/growth', dashboardController.getUsersGrowth);

/**
 * @route GET /api/dashboard/timeline
 * @desc Получить таймлайн роста пользователей
 * @query months - количество месяцев (по умолчанию 6, максимум 24)
 * @access Private/Public
 */
router.get('/timeline', dashboardController.getGrowthTimeline);

/**
 * @route GET /api/dashboard/daily
 * @desc Получить ежедневную статистику регистраций
 * @query days - количество дней (по умолчанию 30, максимум 365)
 * @access Private/Public
 */
router.get('/daily', dashboardController.getDailyRegistrations);

/**
 * @route GET /api/dashboard/summary
 * @desc Получить полную сводку дашборда
 * @access Private/Public
 */
router.get('/summary', dashboardController.getDashboardSummary);

/**
 * @route GET /api/dashboard/widget
 * @desc Получить минимальную статистику для виджета
 * @access Private/Public
 */
router.get('/widget', dashboardController.getWidgetStats);

export default router;