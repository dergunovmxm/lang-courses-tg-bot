import { Router } from 'express';
import usersRouter from './users';
import dashboardRouter from './dashboard'

const router = Router();

router.use('/users', usersRouter);
router.use('/dashboard', dashboardRouter);


export default router;