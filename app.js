/* main 루트 파일: express 진입점! */
const express = require('express');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/authRoutes');
const recent_logRoutes = require('./routes/recent_logRoutes');
const user_nameRoutes = require('./routes/user_nameRoutes');
const findWebtoonsByKeyword = require('./routes/findKeywordRoutes');
const randomwebtoon = require('./routes/randomRoutes')

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/auth', authRoutes);
app.use('/api/log', recent_logRoutes);
app.use('/api/user', user_nameRoutes); 
app.use('/api/keyword', findWebtoonsByKeyword);
app.use('/api/recommend', randomwebtoon);


const port = 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
