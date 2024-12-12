const webtoonService = require('../services/webtoonService');

exports.searchWebtoons = async (req, res) => {
    try {
        const { query, type } = req.query;
        console.log('Received search request:', { query, type });
        
        if (!query) {
            return res.status(400).json({ 
                error: '검색어를 입력해주세요.' 
            });
        }

        const result = await webtoonService.searchWebtoons({
            query,
            type,
            limit: 10
        });

        console.log('Search result:', result);
        res.json(result);

    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({ 
            error: '검색 중 오류가 발생했습니다.',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
};

exports.getRecommendations = async (req, res) => {
    try {
        const { title, type } = req.query;
        
        if (!title) {
            return res.status(400).json({ 
                error: '웹툰 제목이 필요합니다.' 
            });
        }

        const recommendations = await webtoonService.getRecommendationsByTitle(title, type);
        
        res.json({
            recommendations
        });

    } catch (error) {
        console.error('Recommendation error:', error);
        res.status(500).json({ 
            error: '추천 처리 중 오류가 발생했습니다.' 
        });
    }
};

exports.getMultipleRecommendations = async (req, res) => {
    try {
        const { titles } = req.body;
        
        if (!titles || !Array.isArray(titles) || titles.length === 0) {
            return res.status(400).json({ error: "웹툰 제목 목록이 필요합니다" });
        }

        const result = await webtoonService.getMultipleRecommendations(titles);
        res.json(result);
    } catch (error) {
        console.error('Controller error:', error);
        res.status(500).json({ error: error.message });
    }
}; 