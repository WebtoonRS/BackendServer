/* 사용자 인증 관련 API 요청 처리 */
var uuid = require('uuid');
var con = require('../db/connection');
var { saltHashPassword, checkHashPassword } = require('../utils/hashUtils');


exports.register = (req, res) => {
    var post_data = req.body;
    var uid = uuid.v4();
    var plaint_password = post_data.password;
    var hash_data = saltHashPassword(plaint_password);
    var password = hash_data.passwordHash;
    var salt = hash_data.salt;
    var name = post_data.name;
    var email = post_data.email;

    con.query('SELECT * FROM user WHERE email=?', [email], function(err, result) {
        if (err) {
            console.log('[MySQL ERROR]', err);
            res.status(500).json('Register error');
            return;
        }

        if (result && result.length) {
            res.json('User already exists!!');
        } else {
            con.query('INSERT INTO user (unique_id, name, email, encrypted_password, salt, created_at, updated_at) VALUES (?, ?, ?, ?, ?, NOW(), NOW())',
            [uid, name, email, password, salt], function(err) {
                if (err) {
                    console.log('[MySQL ERROR]', err);
                    res.status(500).json('Register error');
                    return;
                }
                res.json('Register successful');
            });
        }
    });
};

exports.login = (req, res) => {
    var post_data = req.body;
    //extract email and password from request
    var user_password = post_data.password;
    var email = post_data.email;

    con.query('SELECT * FROM user WHERE email=?', [email], function(err, result, fields){
        if (err) {
            console.log('[MySQL ERROR]', err);
            res.status(500).json('Register error');
            return;
        }
        
        if (result && result.length) {
            var salt = result[0].salt; //Get salt of result if account exist
            var encrypted_password = result[0].encrypted_password;
            //Hash password from Login request with salt in Dtabase
            var hash_password = checkHashPassword(user_password,salt).passwordHash;
            if(encrypted_password == hash_password)
                res.end(JSON.stringify(result[0])); //if password is true, return all info user
            else 
                res.end(JSON.stringify('Wrong password'));
        } else {
            // Insert new user
            res.json('User not exist!');
        }
    });
};

//ver2

