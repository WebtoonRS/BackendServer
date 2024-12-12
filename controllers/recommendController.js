/* 웹툰 추천 관련 API 요청 처리: 추천 결과 저장 및 웹툰 목록 가져옴 */
const axios = require('axios');
const con = require('../db/connection');
const { PythonShell } = require('python-shell');
const webtoonService = require('../services/webtoonService');

exports.saveRecommendations = async (req, res) => {
    const { user_unique_id, selected_indices } = req.body;

    con.query('SELECT * FROM user WHERE unique_id = ?', [user_unique_id], async (err, results) => {
        if (err) {
            console.error('Error querying data: ' + err.stack);
            res.status(500).send('Error querying data.');
            return;
        }

        if (results.length === 0) {
            res.status(404).send('User not found.');
            return;
        }

        try {
            const response = await axios.post('http://localhost:5000/recommendations', { selected_indices });
            const recommendations = response.data;

            const likedWebtoons = recommendations.map(rec => rec.title).join(', ');
            const insertQuery = 'INSERT INTO user_preferences (user_unique_id, liked_webtoons) VALUES (?, ?)';
            con.query(insertQuery, [user_unique_id, likedWebtoons], (insertErr) => {
                if (insertErr) {
                    console.error('Error inserting data: ' + insertErr.stack);
                    res.status(500).send('Error inserting data.');
                    return;
                }
                res.status(201).send('Recommendations saved successfully.');
            });
        } catch (apiError) {
            console.error('Error calling Flask API: ', apiError);
            res.status(500).send('Error calling Flask API.');
        }
    });
};

exports.displayWebtoons = async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5000/display-webtoons');
        const webtoons = response.data;

        console.log("Randomly selected webtoons:\n");
        webtoons.forEach((webtoon, index) => {
            console.log(`${index + 1}: ${webtoon.title} - ${webtoon.genre} (Index: ${webtoon.index})`);
        });

        res.status(200).json(webtoons);
    } catch (apiError) {
        console.error('Error calling Flask API: ', apiError);
        res.status(500).send('Error calling Flask API.');
    }
};

exports.searchAndRecommend = async (req, res) => {
    try {
        const query = req.query.query;
        if (!query) {
            return res.status(400).json({ error: '검색어가 필요합니다.' });
        }

        // 검색 결과 가져오기
        const searchResults = webtoonService.searchWebtoons(query);

        if (searchResults.length === 0) {
            return res.json({ searchResults: [], recommendations: [] });
        }

        // 첫 번째 검색 결과를 기반으로 추천
        const firstResult = searchResults[0];
        
        const options = {
            mode: 'json',
            pythonPath: 'python3',
            scriptPath: './python_recommendation',
            args: [JSON.stringify({ webtoon_id: firstResult.id })]
        };

        PythonShell.run('recommendation.py', options, function (err, results) {
            if (err) {
                console.error('Python 스크립트 실행 오류:', err);
                return res.status(500).json({ error: '추천 시스템 실행 중 오류가 발생했습니다.' });
            }
            
            res.json({
                searchResults: searchResults.slice(0, 5),
                recommendations: results[0].recommendations
            });
        });
    } catch (error) {
        console.error('서버 오류:', error);
        res.status(500).json({ error: error.message });
    }
};

exports.getWebtoonDetails = (req, res) => {
    const webtoonId = parseInt(req.params.id);
    const webtoon = webtoonService.getWebtoonById(webtoonId);
    
    if (!webtoon) {
        return res.status(404).json({ error: '웹툰을 찾을 수 없습니다.' });
    }
    
    res.json(webtoon);
};
