const express = require('express');
const router = express.Router();
const { updateRecentWebtoon } = require('../controllers/recent_logController');

// 최근 본 웹툰 업데이트 API 엔드포인트
router.post('/recentlog', updateRecentWebtoon);

module.exports = router;