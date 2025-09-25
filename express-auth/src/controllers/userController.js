const pool = require("../db");

exports.getUserInfo = async (req, res) => {
    try {
        const { id } = req.params;
        const result = await pool.query(
            "SELECT user_id, name, email, created_on FROM users WHERE user_id=$1",
            [id]
        );
        if (result.rows.length === 0) return res.status(404).json({ error: "User not found" });
        res.json(result.rows[0]);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
};
