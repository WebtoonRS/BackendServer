const express = require('express');
const router = express.Router();
const { getNickname } = require('../controllers/user_nameController');

// 최근 본 웹툰 업데이트 API 엔드포인트
router.post('/getName', getNickname);

module.exports = router;