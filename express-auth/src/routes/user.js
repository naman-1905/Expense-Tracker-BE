const express = require("express");
const { getUserInfo } = require("../controllers/userController");
const router = express.Router();

router.get("/:id", getUserInfo);

module.exports = router;
