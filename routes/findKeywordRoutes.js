const express = require('express');
const router = express.Router();
const {findWebtoonsByKeyword} = require('../controllers/findKeywordController');

// 키워드를 기반으로 웹툰 검색 API 엔드포인트
router.post('/search', findWebtoonsByKeyword);

module.exports = router;
