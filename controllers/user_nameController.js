// 사용자의 id가 존재하는지 확인하고, 있다면 name 필드를 반환
var con = require('../db/connection');

exports.getNickname = (req, res) => {
    const userUniqueId = req.body.user_unique_id;

    con.query('SELECT name FROM user WHERE unique_id=?', [userUniqueId], function(err, result) {
        if (err) {
            console.log('[MySQL ERROR]', err);
            res.status(500).json('Database error');
            return;
        }

        if (result && result.length) {
            res.json({ nickname: result[0].name });
        } else {
            res.status(404).json('User not found');
        }
    });
};