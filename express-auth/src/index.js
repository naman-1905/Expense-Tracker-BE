const express = require("express");
const bodyParser = require("body-parser");
const authRoutes = require("./routes/auth");

const app = express();
app.use(bodyParser.json());

app.use("/auth", authRoutes);

const PORT = process.env.EXPRESS_PORT || 4000;
app.listen(PORT, () => console.log(`Express Auth running on ${PORT}`));
