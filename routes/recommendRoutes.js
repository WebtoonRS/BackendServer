/* 웹툰 추천 관련 API 엔드포인트 정의 */
const express = require('express');
const router = express.Router();
const webtoonService = require('../services/webtoonService');

router.post('/recommendations', async (req, res) => {
    try {
        const { title, mode } = req.body;
        console.log(`Recommendation request - Title: ${title}, Mode: ${mode}`);
        
        const recommendations = await webtoonService.getRecommendationsByTitle(title, mode);
        res.json({
            recommendations: recommendations,
            message: "추천이 완료되었습니다"
        });
    } catch (error) {
        console.error('Recommendation error:', error);
        res.status(500).json({ 
            error: error.message,
            message: "추천 처리 중 오류가 발생했습니다"
        });
    }
});

module.exports = router;
