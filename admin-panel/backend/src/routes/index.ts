import { Router } from 'express';
import usersRouter from './users';
import dashboardRouter from './dashboard'
import taskRouter from './tasks'

const router = Router();

router.use('/users', usersRouter);
router.use('/dashboard', dashboardRouter);
router.use('/tasks', taskRouter);


export default router;