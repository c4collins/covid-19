module.exports = {
  entry: ["./src/frontend/app.js"],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ["babel-loader"]
      }
    ]
  },
  output: {
    path: __dirname + "/src/static",
    filename: "bundle.js"
  }
};
