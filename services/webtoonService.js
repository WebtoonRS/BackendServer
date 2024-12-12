const axios = require('axios');
const mysql = require('mysql2/promise');

class WebtoonService {
    constructor() {
        this.dbConfig = {
            host: "localhost",
            user: "root",
            password: "sookmyung2024",
            database: "webtoon_db",
            waitForConnections: true,
            connectionLimit: 10
        };
        this.pool = mysql.createPool(this.dbConfig);
    }

    async searchWebtoons({ query, type, limit = 10 }) {
        let connection;
        try {
            console.log(`Searching webtoons with title containing: ${query}`);
            connection = await this.pool.getConnection();
            
            const searchQuery = `
                SELECT title
                FROM webtoons
                WHERE title LIKE ?
                LIMIT 10
            `;
            
            console.log('Query:', query);
            
            const [webtoons] = await connection.execute(searchQuery, [
                `%${query}%`
            ]);
            
            console.log('Search results:', webtoons);

            return {
                searchResults: webtoons.map(webtoon => ({
                    title: webtoon.title
                }))
            };

        } catch (error) {
            console.error('Search error:', error);
            throw error;
        } finally {
            if (connection) {
                connection.release();
            }
        }
    }

    async getRecommendationsByTitle(title, mode) {
        try {
            console.log(`Requesting recommendations - Title: "${title}", Mode: ${mode}`);
            
            const pythonEndpoint = `http://localhost:5000/${mode}_recommendations`;

            const response = await axios.post(pythonEndpoint, {
                title: title
            });

            console.log('Python API response:', response.data);

            return {
                recommendations: response.data,
                message: "추천이 완료되었습니다"
            };
        } catch (error) {
            if (error.response && error.response.status === 404) {
                throw new Error("웹툰을 찾을 수 없습니다");
            }
            console.error(`Error getting recommendations for "${title}":`, error);
            throw error;
        }
    }

    async getMultipleRecommendations(titles) {
        try {
            console.log(`Requesting multiple recommendations for titles:`, titles);
            
            const response = await axios.post('http://localhost:5000/api/webtoons/multiple_story_recommendations', {
                titles: titles
            });

            console.log('Python API response:', response.data);

            return {
                recommendations: response.data,
                message: "다중 웹툰 추천이 완료되었습니다"
            };
        } catch (error) {
            if (error.response && error.response.status === 404) {
                throw new Error("웹툰을 찾을 수 없습니다");
            }
            console.error('Error getting multiple recommendations:', error);
            throw error;
        }
    }

    // 웹툰 응답 포맷 통일
    formatWebtoonResponse(webtoon) {
        return {
            id: webtoon.id,
            title: webtoon.title,
            author: webtoon.author,
            synopsis: webtoon.synopsis || "",
            thumbnail_link: webtoon.thumbnail_link,
            similarity_score: webtoon.similarity_score || 0.0
        };
    }
}

module.exports = new WebtoonService(); 