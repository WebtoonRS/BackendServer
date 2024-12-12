const express = require('express');
const router = express.Router();
const webtoonController = require('../controllers/webtoonController');

// 웹툰 검색 API
router.get('/search', webtoonController.searchWebtoons);
router.post('/style_recommendations', webtoonController.getRecommendations);
router.post('/story_recommendations', webtoonController.getRecommendations);
router.post('/multiple_recommendations', webtoonController.getMultipleRecommendations);

module.exports = router; 