const express = require('express');
const router = express.Router();
const { getWebtoonsByGenre } = require('../controllers/Randomwebtoon');

// 장르에 따른 웹툰 가져오는 라우트
router.post('/get_webtoons', getWebtoonsByGenre);

module.exports = router;
