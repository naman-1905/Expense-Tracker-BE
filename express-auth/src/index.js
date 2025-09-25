const express = require("express");
const bodyParser = require("body-parser");
const authRoutes = require("./routes/auth");
const userRoutes = require("./routes/user");

const app = express();
app.use(bodyParser.json());

app.use("/auth", authRoutes);
app.use("/user", userRoutes);

const PORT = process.env.EXPRESS_PORT || 4000;
app.listen(PORT, () => console.log(`Express Auth running on ${PORT}`));
