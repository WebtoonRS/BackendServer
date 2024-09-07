// 사용자가 웹툰 클릭했을때, 최근 본 웹툰 테이블 (id, title)형태로 업데이트 

var con = require('../db/connection');

exports.updateRecentWebtoon = (req, res) => {
    const userUniqueId = req.body.user_unique_id; // 사용자의 고유 ID
    const webtoonTitle = req.body.title; // 웹툰의 제목

    // 최근 본 웹툰 테이블에 기록 추가
    con.query('INSERT INTO recentlog (user_id, webtoon_name) VALUES (?, ?)', [userUniqueId, webtoonTitle], function(err) {
        if (err) {
            console.log('[MySQL ERROR]', err);
            res.status(500).json('Database error');
            return;
        }

        res.json('Recent webtoon saved');
    });
};

