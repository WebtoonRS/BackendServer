const connection = require('../db/connection');

// 장르에 따른 무작위 웹툰 30개 가져오는 함수
exports.getWebtoonsByGenre = (req, res) => {
    const genre = req.body.genre;

    const query = `
        SELECT title, thumbnail_link 
        FROM webtoons 
        WHERE keywords LIKE ?
    `;

    connection.query(query, [`%${genre}%`], (err, results) => {
        if (err) {
            console.error('Database error:', err);
            res.status(500).json({ error: 'Database error' });
            return;
        }

        // 결과에서 무작위로 30개의 웹툰 선택
        const shuffledResults = results.sort(() => 0.5 - Math.random());
        const selectedWebtoons = shuffledResults.slice(0, 30);

        res.json(selectedWebtoons);
    });
};
