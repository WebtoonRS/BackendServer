// 데이터베이스 연결 설정 불러오기
var con = require('../db/connection');

exports.findWebtoonsByKeyword = (req, res) => {
    const keyword = req.body.keyword;

    const query = 'SELECT title, thumbnail_link FROM webtoons WHERE FIND_IN_SET(?, keywords) > 0';

    con.query(query, [keywords], function(err, results) {
        if (err) {
            console.log('[MySQL ERROR]', err);
            res.status(500).json('Database error');
            return;
        }

        res.json(results);
    });
};
